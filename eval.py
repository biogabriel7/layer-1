"""Scores extraction results against golden.md and the programmatic rules.

Reads results/*.json (produced by extract.py) and sample-obs.csv, parses the
human-annotated examples in golden.md, and reports the five Layer 1 eval
dimensions:

  1. Evidence Grounding   — every signal's evidence is a substring of the
                            source observation (case-insensitive, whitespace-
                            normalized).
  2. Signal Completeness  — recall of extracted signals vs. golden annotations,
                            matched by evidence overlap.
  3. No Hallucinated      — precision of extracted signals vs. golden
     Signals                annotations.
  4. Type Accuracy        — predicted type matches golden type on matched
                            signals.
  5. Observation Type     — observation_type matches the student_count rule
                            (1 → individual, >1 → group).

Evidence Grounding and Observation Type run on every result. The other three
require a golden annotation, so they cover only the subset of observations
present in golden.md.
"""

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv
from openai import OpenAI

RESULTS_DIR = Path("results")
CSV_PATH = Path("sample-obs.csv")
GOLDEN_PATH = Path("golden.md")
JUDGE_PROMPT_PATH = Path("judge_prompt.md")
REASONING_EVAL_DIR = Path("reasoning_eval")
SUMMARY_PATH = Path("summary.md")
JUDGE_MODEL = "anthropic/claude-sonnet-4-6"

VALID_TYPES = {
    "behavioral_evidence",
    "emotional_indicator",
    "context_marker",
    "concern_flag",
}

# Targets (pass) and minimum-acceptable floors from the eval spec.
TARGETS = {
    "evidence_grounding": (1.00, 0.95),
    "signal_completeness": (0.85, 0.75),
    "no_hallucinated_signals": (1.00, 0.95),
    "type_accuracy": (0.95, 0.85),
    "observation_type": (1.00, 0.98),
}

# Target for the LLM-judge reasoning audit (--audit-reasoning).
REASONING_TARGET = (0.95, 0.85)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class Signal:
    evidence: str
    type: str


@dataclass
class GoldenExample:
    number: int
    observation: str
    student_count: int
    signals: list[Signal]


@dataclass
class ResultFile:
    cache_key: str
    observation: str
    student_count: int
    observation_type: str
    signals: list[Signal]


@dataclass
class Metrics:
    # Evidence grounding (signal-level)
    eg_total: int = 0
    eg_passed: int = 0
    eg_failures: list[tuple[str, str]] = field(default_factory=list)  # (cache_key, evidence)

    # Observation type (observation-level)
    ot_total: int = 0
    ot_passed: int = 0

    # Recall / precision / type accuracy (over golden-annotated observations)
    golden_observations: int = 0
    golden_signals_total: int = 0
    golden_signals_matched: int = 0  # → recall
    predicted_signals_total: int = 0
    predicted_signals_matched: int = 0  # → precision
    type_matches: int = 0
    type_total: int = 0


# Reasoning-audit data models (used only when --audit-reasoning is set).


@dataclass
class SignalJudgement:
    signal_index: int
    evidence: str
    matches_answer: tuple[bool, str]          # (passed, note)


@dataclass
class ObservationJudgement:
    cache_key: str
    per_signal: list[SignalJudgement]


@dataclass
class ReasoningMetrics:
    obs_total: int = 0
    signals_total: int = 0
    signals_passed: int = 0

    # (cache_key, evidence snippet, judge note)
    failures: list[tuple[str, str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def cache_key(observation: str, student_count: int) -> str:
    """Mirror extract.py.cache_key so we can locate the result file."""
    raw = f"{observation}|{student_count}"
    return hashlib.sha256(raw.encode()).hexdigest()


def normalize(s: str) -> str:
    """Lowercase, collapse whitespace, strip surrounding punctuation/quotes."""
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip(" \t\n\r\"'“”‘’.,;:!?")


def evidence_grounded(evidence: str, observation: str) -> bool:
    """Evidence must appear verbatim in the observation (normalized)."""
    ne = normalize(evidence)
    no = normalize(observation)
    if not ne:
        return False
    return ne in no


def evidence_overlap(a: str, b: str) -> float:
    """Token-level Jaccard, with a substring shortcut."""
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return 0.0
    if na in nb or nb in na:
        return 1.0
    ta, tb = set(na.split()), set(nb.split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def evidence_matches(a: str, b: str, threshold: float = 0.5) -> bool:
    return evidence_overlap(a, b) >= threshold


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_results() -> list[ResultFile]:
    """Pair each result JSON with its source observation (from sample-obs.csv
    or golden.md, since extract.py can read either)."""
    if not RESULTS_DIR.exists():
        print(f"ERROR: {RESULTS_DIR}/ not found — run extract.py first", file=sys.stderr)
        sys.exit(1)

    # Index CSV by cache key so we can recover the observation text.
    # Skip malformed rows (e.g. unquoted observations that bleed across
    # columns and leave student_count empty) — they can't have results.
    obs_index: dict[str, tuple[str, int]] = {}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            obs = row["observation"]
            try:
                sc = int(row["student_count"])
            except (ValueError, TypeError):
                continue
            obs_index[cache_key(obs, sc)] = (obs, sc)

    # Also index golden.md observations so results extracted via
    # `extract.py --golden N` can be recovered even if absent from the CSV.
    for ex in parse_golden(GOLDEN_PATH):
        obs_index.setdefault(
            cache_key(ex.observation, ex.student_count),
            (ex.observation, ex.student_count),
        )

    results: list[ResultFile] = []
    for path in sorted(RESULTS_DIR.glob("*.json")):
        key = path.stem
        if key not in obs_index:
            # Orphaned result (source observation no longer present) — skip.
            continue
        obs, sc = obs_index[key]
        data = json.loads(path.read_text())
        signals_raw = data.get("signals", [])
        signals = [
            Signal(
                evidence=str(s.get("evidence", "")),
                type=str(s.get("type", "")).strip(),
            )
            for s in signals_raw
        ]
        results.append(
            ResultFile(
                cache_key=key,
                observation=obs,
                student_count=sc,
                observation_type=str(data.get("observation_type", "")),
                signals=signals,
            )
        )
    return results


def parse_golden(path: Path) -> list[GoldenExample]:
    """Parse each '## Example N' block. Tolerates the minor JSON defects in
    golden.md (stray quotes, trailing commas, typos). Skips examples whose
    Output section is a template placeholder or is missing entirely."""
    if not path.exists():
        return []
    text = path.read_text()

    # Split on the Example headers; keep the numbers.
    parts = re.split(r"^##\s*Example\s+(\d+)\s*$", text, flags=re.MULTILINE)
    # parts = [preamble, num, body, num, body, ...]

    examples: list[GoldenExample] = []
    for i in range(1, len(parts), 2):
        number = int(parts[i])
        body = parts[i + 1]

        obs_match = re.search(
            r'Observation:\s*"(.+?)"\s*\n\s*Student Count:',
            body,
            re.DOTALL,
        )
        sc_match = re.search(r"Student Count:\s*(\d+)", body)
        if not obs_match or not sc_match:
            continue
        observation = obs_match.group(1)
        student_count = int(sc_match.group(1))

        # Locate the Output section; if missing, this example is un-annotated.
        out_match = re.search(
            r"\*\*Output\*\*\s*(.+?)(?=^##\s*Example|\Z)",
            body,
            re.DOTALL | re.MULTILINE,
        )
        if not out_match:
            continue
        output = out_match.group(1)

        # Placeholder rows use the literal "|" union spec — skip them.
        if "behavioral_evidence | emotional_indicator" in output:
            continue

        signals = _extract_signals(output)
        examples.append(
            GoldenExample(
                number=number,
                observation=observation,
                student_count=student_count,
                signals=signals,
            )
        )
    return examples


def _extract_signals(output: str) -> list[Signal]:
    """Extract (evidence, type) pairs from a signals block.

    golden.md isn't valid JSON in many places (stray `""`, trailing commas,
    typo'd keys), so we scan line-by-line and pair evidence with its
    following type within each `{ ... }` signal object.
    """
    signals: list[Signal] = []
    current_evidence: str | None = None
    depth = 0

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if line.startswith("{"):
            depth += 1
            current_evidence = None
            continue
        if line.startswith("}"):
            depth = max(0, depth - 1)
            current_evidence = None
            continue
        if depth == 0:
            continue

        ev = _field_value(line, "evidence")
        if ev is not None:
            current_evidence = ev
            continue

        ty = _field_value(line, "type")
        if ty is not None and current_evidence is not None:
            signals.append(Signal(evidence=current_evidence, type=ty.strip()))
            current_evidence = None

    return signals


def _field_value(line: str, field_name: str) -> str | None:
    """Pull a quoted string value from a line like `"key": "value",`.

    Strips the leading/trailing quotes and trailing comma, which handles the
    common `""value""` doubling seen in golden.md."""
    m = re.match(rf'^"{field_name}"\s*:\s*(.*?)\s*,?\s*$', line)
    if not m:
        return None
    val = m.group(1)
    # Peel off any number of surrounding double quotes.
    while len(val) >= 2 and val[0] == '"' and val[-1] == '"':
        val = val[1:-1]
    return val


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def expected_observation_type(student_count: int) -> str:
    return "individual" if student_count == 1 else "group"


def score_programmatic(result: ResultFile, m: Metrics) -> None:
    """Evidence Grounding + Observation Type. Runs on every result."""
    # Evidence Grounding (signal-level).
    for sig in result.signals:
        m.eg_total += 1
        if evidence_grounded(sig.evidence, result.observation):
            m.eg_passed += 1
        else:
            m.eg_failures.append((result.cache_key, sig.evidence))

    # Observation Type (observation-level).
    m.ot_total += 1
    if result.observation_type == expected_observation_type(result.student_count):
        m.ot_passed += 1


def score_against_golden(
    result: ResultFile, golden: GoldenExample, m: Metrics
) -> None:
    """Recall, precision, and type accuracy using evidence-overlap matching."""
    m.golden_observations += 1
    m.golden_signals_total += len(golden.signals)
    m.predicted_signals_total += len(result.signals)

    used_predicted: set[int] = set()

    # Greedy best-match: for each golden signal, find the highest-overlap
    # predicted signal that hasn't been claimed yet.
    for gsig in golden.signals:
        best_idx = -1
        best_score = 0.0
        for idx, psig in enumerate(result.signals):
            if idx in used_predicted:
                continue
            score = evidence_overlap(gsig.evidence, psig.evidence)
            if score > best_score:
                best_score = score
                best_idx = idx
        if best_idx >= 0 and best_score >= 0.5:
            used_predicted.add(best_idx)
            m.golden_signals_matched += 1
            m.predicted_signals_matched += 1
            # Type accuracy: check only on matched pairs.
            m.type_total += 1
            if gsig.type.strip() == result.signals[best_idx].type.strip():
                m.type_matches += 1


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def pct(num: int, den: int) -> float:
    return 0.0 if den == 0 else num / den


def verdict(rate: float, target: float, floor: float) -> str:
    if rate >= target:
        return "PASS"
    if rate >= floor:
        return "WARN"
    return "FAIL"


_RowList = list[tuple[str, float, tuple[float, float], str]]


def _metrics_rows(m: Metrics) -> _RowList:
    return [
        ("Evidence Grounding", pct(m.eg_passed, m.eg_total),
         TARGETS["evidence_grounding"], f"{m.eg_passed}/{m.eg_total} signals"),
        ("Observation Type", pct(m.ot_passed, m.ot_total),
         TARGETS["observation_type"], f"{m.ot_passed}/{m.ot_total} observations"),
        ("Signal Completeness (recall)",
         pct(m.golden_signals_matched, m.golden_signals_total),
         TARGETS["signal_completeness"],
         f"{m.golden_signals_matched}/{m.golden_signals_total} golden signals"),
        ("No Hallucinated Signals (precision)",
         pct(m.predicted_signals_matched, m.predicted_signals_total),
         TARGETS["no_hallucinated_signals"],
         f"{m.predicted_signals_matched}/{m.predicted_signals_total} predicted signals"),
        ("Type Accuracy", pct(m.type_matches, m.type_total),
         TARGETS["type_accuracy"], f"{m.type_matches}/{m.type_total} matched pairs"),
    ]


def _reasoning_rows(rm: ReasoningMetrics) -> _RowList:
    return [
        ("Reasoning matches answer",
         pct(rm.signals_passed, rm.signals_total),
         REASONING_TARGET,
         f"{rm.signals_passed}/{rm.signals_total} signals"),
    ]


def _format_table(rows: _RowList) -> str:
    lines = [
        f"{'Dimension':<40} {'Rate':>8} {'Target':>8} {'Floor':>8}  Result  Detail",
        "-" * 110,
    ]
    for name, rate, (target, floor), detail in rows:
        v = verdict(rate, target, floor)
        lines.append(
            f"{name:<40} {rate*100:>7.1f}% {target*100:>7.0f}% {floor*100:>7.0f}%"
            f"  {v:<6}  {detail}"
        )
    return "\n".join(lines)


def _format_eg_failures(m: Metrics, max_n: int = 20) -> str:
    if not m.eg_failures:
        return ""
    lines = [f"Evidence grounding failures (first {max_n}):"]
    for key, ev in m.eg_failures[:max_n]:
        snippet = ev if len(ev) <= 100 else ev[:97] + "..."
        lines.append(f"  {key[:12]}  {snippet!r}")
    if len(m.eg_failures) > max_n:
        lines.append(f"  ...and {len(m.eg_failures) - max_n} more")
    return "\n".join(lines)


def _format_reasoning_failures(rm: ReasoningMetrics, max_n: int = 20) -> str:
    if not rm.failures:
        return ""
    lines = [f"Flagged signals (first {max_n}):"]
    for key, snippet, note in rm.failures[:max_n]:
        note_snip = note if len(note) <= 80 else note[:77] + "..."
        lines.append(f"  {key[:12]}  {snippet!r}  → {note_snip}")
    if len(rm.failures) > max_n:
        lines.append(f"  ...and {len(rm.failures) - max_n} more")
    return "\n".join(lines)


def report(m: Metrics, show_failures: bool) -> None:
    print()
    print(_format_table(_metrics_rows(m)))
    print()
    print(f"Golden-annotated observations scored: {m.golden_observations}")

    if show_failures:
        failures = _format_eg_failures(m)
        if failures:
            print()
            print(failures)


# ---------------------------------------------------------------------------
# Reasoning audit (LLM-judge, opt-in via --audit-reasoning)
# ---------------------------------------------------------------------------


def load_judge_prompt() -> str:
    if not JUDGE_PROMPT_PATH.exists():
        print(f"ERROR: {JUDGE_PROMPT_PATH} not found", file=sys.stderr)
        sys.exit(1)
    return JUDGE_PROMPT_PATH.read_text()


def build_judge_user_message(
    result: ResultFile,
    raw_signals: list[dict[str, Any]],
) -> str:
    """Serialize the judge input. raw_signals comes from results/<key>.json so
    that reasoning, sel_competencies, and observation_confidence are preserved
    (the trimmed ResultFile.signals only carries evidence + type)."""
    payload = {
        "observation": result.observation,
        "student_count": result.student_count,
        "predicted_signals": [
            {
                "signal_index": i,
                "evidence": s.get("evidence", ""),
                "type": s.get("type", ""),
                "sel_competencies": s.get("sel_competencies", []),
                "observation_confidence": s.get("observation_confidence", ""),
                "reasoning": s.get("reasoning", ""),
            }
            for i, s in enumerate(raw_signals)
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def reasoning_cache_key(judge_prompt: str, user_msg: str) -> str:
    """sha256 over (judge prompt + user message). The user message embeds the
    full result JSON and the golden annotation, so any drift in any of those
    three inputs busts the cache automatically."""
    raw = judge_prompt + "\n---\n" + user_msg
    return hashlib.sha256(raw.encode()).hexdigest()


def call_judge_api(client: OpenAI, system_prompt: str, user_msg: str) -> dict[str, Any]:
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
    )
    content = response.choices[0].message.content
    assert content is not None
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    parsed: dict[str, Any] = json.loads(text)
    return parsed


def _check(d: Any) -> tuple[bool, str]:
    if not isinstance(d, dict):
        return (False, "judge returned malformed entry")
    return (bool(d.get("passed", False)), str(d.get("note", "")))


def parse_judge_response(
    raw: dict[str, Any], result_cache_key: str
) -> ObservationJudgement:
    per_signal: list[SignalJudgement] = []
    for entry in raw.get("per_signal", []):
        if not isinstance(entry, dict):
            continue
        per_signal.append(
            SignalJudgement(
                signal_index=int(entry.get("signal_index", -1)),
                evidence=str(entry.get("evidence", "")),
                matches_answer=_check(entry.get("reasoning_matches_answer")),
            )
        )

    return ObservationJudgement(
        cache_key=result_cache_key,
        per_signal=per_signal,
    )


def audit_one(
    result: ResultFile,
    judge_prompt: str,
    client: OpenAI | None,
    *,
    force: bool,
    dry_run: bool,
) -> ObservationJudgement | None:
    """Cache-aware judge call. Returns None in dry-run."""
    raw_data = json.loads((RESULTS_DIR / f"{result.cache_key}.json").read_text())
    raw_signals_obj = raw_data.get("signals", [])
    raw_signals: list[dict[str, Any]] = [s for s in raw_signals_obj if isinstance(s, dict)]
    user_msg = build_judge_user_message(result, raw_signals)
    rc_key = reasoning_cache_key(judge_prompt, user_msg)
    cache_path = REASONING_EVAL_DIR / f"{rc_key}.json"

    if dry_run:
        first_line = judge_prompt.split("\n", 1)[0]
        print(f"[dry-run] {result.cache_key[:12]}  cache={rc_key[:12]}")
        print(f"  system: {first_line[:120]}")
        print(f"  user:   {user_msg[:200].replace(chr(10), ' ')}...")
        return None

    if not force and cache_path.exists():
        raw_judge = json.loads(cache_path.read_text())
    else:
        assert client is not None
        raw_judge = call_judge_api(client, judge_prompt, user_msg)
        REASONING_EVAL_DIR.mkdir(exist_ok=True)
        cache_path.write_text(json.dumps(raw_judge, indent=2, ensure_ascii=False))

    return parse_judge_response(raw_judge, result.cache_key)


def aggregate_reasoning(judgements: Iterable[ObservationJudgement]) -> ReasoningMetrics:
    m = ReasoningMetrics()
    for j in judgements:
        m.obs_total += 1
        for sj in j.per_signal:
            m.signals_total += 1
            passed, note = sj.matches_answer
            if passed:
                m.signals_passed += 1
            else:
                snippet = sj.evidence if len(sj.evidence) <= 100 else sj.evidence[:97] + "..."
                m.failures.append((j.cache_key, snippet, note))
    return m


def report_reasoning(m: ReasoningMetrics, show_failures: bool) -> None:
    print()
    print(f"Reasoning Audit (N={m.obs_total} observations)")
    print(_format_table(_reasoning_rows(m)))

    if show_failures:
        failures = _format_reasoning_failures(m)
        if failures:
            print()
            print(failures)


def run_reasoning_audit(
    results: list[ResultFile],
    golden_by_key: dict[str, GoldenExample],
    args: argparse.Namespace,
) -> ReasoningMetrics | None:
    judge_prompt = load_judge_prompt()
    # Scope the audit to golden-annotated observations so the judge runs on a
    # curated sample by default. --golden/--limit further narrow the scope.
    audit_candidates: list[ResultFile] = [
        r for r in results if r.cache_key in golden_by_key
    ]
    if args.limit is not None:
        audit_candidates = audit_candidates[: args.limit]

    if not audit_candidates:
        print("\nNo golden-matched results to audit.", file=sys.stderr)
        return None

    if args.dry_run:
        for result in audit_candidates:
            audit_one(
                result, judge_prompt,
                client=None, force=args.force, dry_run=True,
            )
        return None

    load_dotenv(".env.local")
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    def _do_audit(r: ResultFile) -> ObservationJudgement | None:
        return audit_one(
            r, judge_prompt, client, force=args.force, dry_run=False,
        )

    judgements: list[ObservationJudgement] = []
    errors = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_do_audit, r): r for r in audit_candidates}
        for future in as_completed(futures):
            try:
                j = future.result()
                if j is not None:
                    judgements.append(j)
            except Exception as e:
                r = futures[future]
                print(f"ERROR auditing {r.cache_key[:12]}: {e}", file=sys.stderr)
                errors += 1

    if errors:
        print(f"\n{errors} audit errors", file=sys.stderr)

    metrics = aggregate_reasoning(judgements)
    report_reasoning(metrics, show_failures=args.show_failures)
    return metrics


# ---------------------------------------------------------------------------
# Summary file (Markdown with Mermaid charts)
# ---------------------------------------------------------------------------


def _distributions(results: list[ResultFile]) -> dict[str, Any]:
    """Collect counts needed for summary charts. Re-reads each result JSON
    because ResultFile.Signal only carries evidence + type."""
    type_counts: dict[str, int] = {}
    confidence_counts: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    sel_counts: dict[str, int] = {}
    signals_per_obs: dict[int, int] = {}
    obs_type_counts: dict[str, int] = {"individual": 0, "group": 0}

    for r in results:
        obs_type_counts[r.observation_type] = obs_type_counts.get(r.observation_type, 0) + 1
        n = len(r.signals)
        signals_per_obs[n] = signals_per_obs.get(n, 0) + 1
        for sig in r.signals:
            type_counts[sig.type] = type_counts.get(sig.type, 0) + 1

        raw = json.loads((RESULTS_DIR / f"{r.cache_key}.json").read_text())
        for s in raw.get("signals", []):
            if not isinstance(s, dict):
                continue
            conf = str(s.get("observation_confidence", ""))
            if conf in confidence_counts:
                confidence_counts[conf] += 1
            comps = s.get("sel_competencies") or []
            if isinstance(comps, list):
                for comp in comps:
                    sel_counts[str(comp)] = sel_counts.get(str(comp), 0) + 1

    return {
        "type_counts": type_counts,
        "confidence_counts": confidence_counts,
        "sel_counts": sel_counts,
        "signals_per_obs": signals_per_obs,
        "obs_type_counts": obs_type_counts,
    }


def _mermaid_bar(
    title: str,
    labels: list[str],
    values: list[float],
    y_label: str,
    y_max: float | None = None,
) -> str:
    if y_max is None:
        peak = max(values) if values else 1.0
        y_max = math.ceil(peak * 1.1 / 5) * 5 if peak > 0 else 10
    labels_str = "[" + ", ".join(f'"{lbl}"' for lbl in labels) + "]"
    values_str = "[" + ", ".join(f"{v:g}" for v in (round(v, 1) for v in values)) + "]"
    return (
        "```mermaid\n"
        "xychart-beta\n"
        f'    title "{title}"\n'
        f"    x-axis {labels_str}\n"
        f'    y-axis "{y_label}" 0 --> {y_max}\n'
        f"    bar {values_str}\n"
        "```"
    )


def _summary_report_block(m: Metrics, reasoning: ReasoningMetrics | None) -> str:
    """Build the terminal-style report (table + failures) for embedding in
    summary.md as a fenced code block."""
    sections: list[str] = [
        f"Scored {m.ot_total} results "
        f"({m.golden_observations} golden annotations available)",
        "",
        _format_table(_metrics_rows(m)),
        "",
        f"Golden-annotated observations scored: {m.golden_observations}",
    ]
    eg_failures = _format_eg_failures(m)
    if eg_failures:
        sections += ["", eg_failures]

    if reasoning is not None:
        sections += [
            "",
            f"Reasoning Audit (N={reasoning.obs_total} observations)",
            _format_table(_reasoning_rows(reasoning)),
        ]
        rs_failures = _format_reasoning_failures(reasoning)
        if rs_failures:
            sections += ["", rs_failures]

    return "\n".join(sections)


def write_summary(
    m: Metrics,
    reasoning: ReasoningMetrics | None,
    results: list[ResultFile],
    scope_desc: str,
) -> None:
    """Render summary.md with eval metrics + Mermaid charts."""
    dist = _distributions(results)

    # Chart 1: pass rates across all eval dimensions
    pass_labels = ["Evidence", "ObsType", "Recall", "Precision", "TypeAcc"]
    pass_values: list[float] = [
        pct(m.eg_passed, m.eg_total) * 100,
        pct(m.ot_passed, m.ot_total) * 100,
        pct(m.golden_signals_matched, m.golden_signals_total) * 100,
        pct(m.predicted_signals_matched, m.predicted_signals_total) * 100,
        pct(m.type_matches, m.type_total) * 100,
    ]
    if reasoning is not None:
        pass_labels.append("Reasoning")
        pass_values.append(pct(reasoning.signals_passed, reasoning.signals_total) * 100)
    pass_chart = _mermaid_bar(
        "Eval Dimension Pass Rates (%)",
        pass_labels, pass_values, "Pass %", y_max=100,
    )

    # Chart 2: signal type distribution
    type_order = ["behavioral_evidence", "emotional_indicator",
                  "context_marker", "concern_flag"]
    type_labels = [t.replace("_", " ") for t in type_order]
    type_values = [float(dist["type_counts"].get(t, 0)) for t in type_order]
    type_chart = _mermaid_bar(
        "Signal Type Distribution", type_labels, type_values, "Signals",
    )

    # Chart 3: confidence distribution
    conf_order = ["high", "medium", "low"]
    conf_values = [float(dist["confidence_counts"].get(c, 0)) for c in conf_order]
    conf_chart = _mermaid_bar(
        "Observation Confidence Distribution", conf_order, conf_values, "Signals",
    )

    # Chart 4: signals-per-observation histogram
    spo: dict[int, int] = dist["signals_per_obs"]
    max_n = max(spo.keys()) if spo else 0
    spo_labels = [str(i) for i in range(max_n + 1)]
    spo_values = [float(spo.get(i, 0)) for i in range(max_n + 1)]
    spo_chart = _mermaid_bar(
        "Signals per Observation", spo_labels, spo_values, "Observations",
    )

    # Chart 5: SEL competency frequency
    sel_order = ["self_awareness", "self_management", "social_awareness",
                 "relationship_skills", "responsible_decision_making"]
    sel_labels = ["self-aware", "self-mgmt", "social-aware",
                  "rel-skills", "resp-decide"]
    sel_values = [float(dist["sel_counts"].get(s, 0)) for s in sel_order]
    sel_chart = _mermaid_bar(
        "SEL Competency Frequency", sel_labels, sel_values, "Signal mentions",
    )

    obs_ind = dist["obs_type_counts"].get("individual", 0)
    obs_grp = dist["obs_type_counts"].get("group", 0)
    total_signals = sum(dist["type_counts"].values())

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    header_line = (
        f"**{len(results)} observations scored · {total_signals} signals extracted · "
        f"{obs_ind} individual / {obs_grp} group**"
    )
    body = f"""# Layer 1 Evaluation Summary

_Generated {timestamp} — scope: {scope_desc}_

{header_line}

## Results

```text
{_summary_report_block(m, reasoning)}
```

## Pass Rates

{pass_chart}

## Signal Mix

{type_chart}

{conf_chart}

## Density

{spo_chart}

## SEL Competencies

{sel_chart}
"""
    SUMMARY_PATH.write_text(body)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Score Layer 1 extraction results")
    parser.add_argument(
        "--show-failures",
        action="store_true",
        help="Print evidence-grounding (and reasoning-audit) failures for debugging",
    )
    parser.add_argument(
        "--audit-reasoning",
        action="store_true",
        help="Run the LLM judge over per-signal `reasoning` and print a second table",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bust the reasoning-audit cache (only with --audit-reasoning)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Audit only the first N golden-matched observations (only with --audit-reasoning)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Parallel judge workers (only with --audit-reasoning)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the judge prompt without calling the API (only with --audit-reasoning)",
    )
    parser.add_argument(
        "--golden",
        type=int,
        default=None,
        metavar="N",
        help="Restrict scoring to the first N examples in golden.md "
             "(file order). Filters programmatic, golden, and audit metrics.",
    )
    args = parser.parse_args()

    results = load_results()
    if not results:
        print("No results found. Run `uv run extract.py` first.", file=sys.stderr)
        sys.exit(1)

    golden_examples = parse_golden(GOLDEN_PATH)
    if args.golden is not None:
        golden_examples = golden_examples[: args.golden]
    golden_by_key: dict[str, GoldenExample] = {
        cache_key(ex.observation, ex.student_count): ex for ex in golden_examples
    }

    if args.golden is not None:
        results = [r for r in results if r.cache_key in golden_by_key]
        if not results:
            print(
                "No cached results match the first "
                f"{args.golden} golden examples. Run "
                f"`uv run extract.py --golden {args.golden}` first.",
                file=sys.stderr,
            )
            sys.exit(1)

    m = Metrics()
    for result in results:
        score_programmatic(result, m)
        gold = golden_by_key.get(result.cache_key)
        if gold is not None:
            score_against_golden(result, gold, m)

    print(f"Scored {len(results)} results "
          f"({len(golden_by_key)} golden annotations available)")
    report(m, show_failures=args.show_failures)

    reasoning_metrics: ReasoningMetrics | None = None
    if args.audit_reasoning:
        reasoning_metrics = run_reasoning_audit(results, golden_by_key, args)

    scope_desc = (
        f"first {args.golden} golden examples"
        if args.golden is not None
        else f"all {len(results)} results"
    )
    if args.audit_reasoning and not args.dry_run:
        scope_desc += " (with reasoning audit)"
    write_summary(m, reasoning_metrics, results, scope_desc)
    print(f"\nWrote {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
