"""Reference-free audit. Runs a cross-family LLM judge over every result,
evaluating each signal against the observation text alone — no human-annotated
answer key required. Three atomic per-signal checks: evidence grounded,
reasoning justifies classification, no over-extraction.
"""

import argparse
import functools
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Iterable

from openai import OpenAI

from layer_1.pipeline.llm import call_json, make_client
from layer_1.pipeline.models import (
    AUDIT_CACHE_DIR,
    AUDIT_PROMPT_PATH,
    JUDGE_MODEL,
    AuditCheckResult,
    AuditedSignal,
    AuditMetrics,
    ResultFile,
)
from layer_1.pipeline.schema import AuditResponse


@functools.lru_cache(maxsize=None)
def load_audit_prompt() -> str:
    """Audit system prompt is the judge rubric alone. The extractor prompt is
    deliberately NOT appended — the judge evaluates quote-fidelity on
    principle, not compliance with extractor rules. Appending the rubric
    would tightly couple judge to extractor and reward rule-echo over
    real quality."""
    return AUDIT_PROMPT_PATH.read_text()


def build_user_message(result: ResultFile, raw_signals: list[dict[str, Any]]) -> str:
    payload = {
        "observation": result.observation,
        "student_count": result.student_count,
        "named_students": result.raw.get("named_students", []),
        "predicted_signals": [
            {
                "signal_index": i,
                "evidence": s.get("evidence", ""),
                "type": s.get("type", ""),
                "confidence": s.get("confidence", ""),
                "valence": s.get("valence"),
                "target": s.get("target"),
                "agency": s.get("agency"),
                "temporality_cue": s.get("temporality_cue"),
                "domain_descriptors": s.get("domain_descriptors", []),
                "participants": s.get("participants", []),
                "reasoning": s.get("reasoning", ""),
            }
            for i, s in enumerate(raw_signals)
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _cache_key(judge_prompt: str, user_msg: str, model: str) -> str:
    """sha256 over (model + judge prompt + user message). The user message
    embeds the full result JSON, so drift in any input busts the cache.
    Including the model prevents stale judgments from leaking across judge swaps."""
    raw = model + "\n---\n" + judge_prompt + "\n---\n" + user_msg
    return hashlib.sha256(raw.encode()).hexdigest()


def _raw_signals(result: ResultFile) -> list[dict[str, Any]]:
    return [s for s in result.raw.get("signals", []) if isinstance(s, dict)]


def audit_one(
    result: ResultFile,
    judge_prompt: str,
    client: OpenAI | None,
    *,
    force: bool,
    dry_run: bool,
    model: str = JUDGE_MODEL,
) -> AuditResponse | None:
    """Cache-aware audit call. Returns None in dry-run or when there are no
    signals to audit."""
    raw_signals = _raw_signals(result)
    if not raw_signals:
        return None

    user_msg = build_user_message(result, raw_signals)
    rc_key = _cache_key(judge_prompt, user_msg, model)
    cache_path = AUDIT_CACHE_DIR / f"{rc_key}.json"

    if dry_run:
        first_line = judge_prompt.split("\n", 1)[0]
        print(f"[dry-run] {result.cache_key[:12]}  cache={rc_key[:12]}  model={model}")
        print(f"  system: {first_line[:120]}")
        print(f"  user:   {user_msg[:200].replace(chr(10), ' ')}...")
        return None

    if not force and cache_path.exists():
        raw = json.loads(cache_path.read_text())
    else:
        if client is None:
            raise RuntimeError("audit_one needs a client when the cache is cold")
        raw = call_json(client, judge_prompt, user_msg, model=model)
        cache_path.write_text(json.dumps(raw, indent=2, ensure_ascii=False))

    return AuditResponse.model_validate(raw)


def aggregate(entries: Iterable[tuple[str, AuditResponse]]) -> AuditMetrics:
    m = AuditMetrics()
    for cache_key, resp in sorted(entries, key=lambda kv: kv[0]):
        m.obs_total += 1
        for sig in resp.per_signal:
            m.signals_total += 1
            snippet = sig.evidence if len(sig.evidence) <= 100 else sig.evidence[:97] + "..."

            grounded_passed = sig.checks.evidence_grounded.passed
            reasoning_passed = sig.checks.reasoning_justifies_classification.passed
            over_extraction_passed = sig.checks.no_over_extraction.passed

            if grounded_passed:
                m.grounded_passed += 1
            else:
                m.grounded_failures.append(AuditCheckResult(
                    cache_key=cache_key, signal_index=sig.signal_index,
                    evidence_snippet=snippet, note=sig.checks.evidence_grounded.note,
                ))

            if reasoning_passed:
                m.reasoning_passed += 1
            else:
                m.reasoning_failures.append(AuditCheckResult(
                    cache_key=cache_key, signal_index=sig.signal_index,
                    evidence_snippet=snippet,
                    note=sig.checks.reasoning_justifies_classification.note,
                ))

            if over_extraction_passed:
                m.over_extraction_passed += 1
            else:
                m.over_extraction_failures.append(AuditCheckResult(
                    cache_key=cache_key, signal_index=sig.signal_index,
                    evidence_snippet=snippet, note=sig.checks.no_over_extraction.note,
                ))

            m.audited_signals.append(AuditedSignal(
                cache_key=cache_key,
                signal_index=sig.signal_index,
                evidence_snippet=snippet,
                grounded_passed=grounded_passed,
                reasoning_passed=reasoning_passed,
                over_extraction_passed=over_extraction_passed,
            ))
    return m


def run_audit(
    results: list[ResultFile], args: argparse.Namespace,
) -> AuditMetrics | None:
    """Run the reference-free audit on results. Capped by args.limit when set."""
    judge_prompt = load_audit_prompt()
    model = getattr(args, "judge_model", JUDGE_MODEL)

    candidates = list(results)
    cap = getattr(args, "limit", None)
    if cap is not None:
        candidates = candidates[:cap]

    if not candidates:
        return None

    if getattr(args, "dry_run", False):
        for r in candidates:
            audit_one(
                r, judge_prompt, client=None,
                force=args.force, dry_run=True, model=model,
            )
        return None

    AUDIT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    client = make_client()

    def _do(r: ResultFile) -> tuple[str, AuditResponse] | None:
        resp = audit_one(
            r, judge_prompt, client,
            force=args.force, dry_run=False, model=model,
        )
        if resp is None:
            return None
        return (r.cache_key, resp)

    entries: list[tuple[str, AuditResponse]] = []
    errors = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_do, r): r for r in candidates}
        for future in as_completed(futures):
            try:
                out = future.result()
                if out is not None:
                    entries.append(out)
            except Exception as e:
                r = futures[future]
                print(
                    f"ERROR auditing {r.cache_key[:12]}: {type(e).__name__}: {e}",
                    file=sys.stderr,
                )
                errors += 1

    if errors:
        print(f"\n{errors} audit errors", file=sys.stderr)
    return aggregate(entries)
