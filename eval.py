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
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv
from openai import OpenAI

RESULTS_DIR = Path("results")
CSV_PATH = Path("sample-obs.csv")
GOLDEN_PATH = Path("golden.md")
JUDGE_PROMPT_PATH = Path("judge_prompt.md")
REASONING_EVAL_DIR = Path("reasoning_eval")
JUDGE_MODEL = "anthropic/claude-sonnet-4-6"

VALID_TYPES = {
    "behavioral_evidence",
    "emotional_indicator",
    "context_marker",
    "mastery_signal",
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

# Targets for the LLM-judge reasoning audit (--audit-reasoning).
REASONING_TARGETS = {
    "reasoning_supports_type":         (0.95, 0.85),
    "reasoning_supports_competencies": (0.95, 0.85),
    "reasoning_supports_confidence":   (0.95, 0.85),
    "reasoning_complete":              (0.95, 0.85),
    "no_missing_signals":              (1.00, 0.95),
    "no_hallucinated_signals":         (1.00, 0.95),
    "type_agreement":                  (0.95, 0.85),
}


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
    supports_type: tuple[bool, str]          # (passed, note)
    supports_competencies: tuple[bool, str]
    supports_confidence: tuple[bool, str]
    complete: tuple[bool, str]


@dataclass
class ObservationJudgement:
    cache_key: str
    per_signal: list[SignalJudgement]
    missing_signals: list[tuple[str, str]]                       # (evidence, note)
    hallucinated_signals: list[tuple[int, str]]                  # (signal_index, note)
    type_disagreements: list[tuple[int, str, str, str]]          # (idx, predicted, golden, note)
    matched_pair_count: int                                      # denominator for type_agreement


@dataclass
class ReasoningMetrics:
    supports_type_total: int = 0
    supports_type_passed: int = 0
    supports_comp_total: int = 0
    supports_comp_passed: int = 0
    supports_conf_total: int = 0
    supports_conf_passed: int = 0
    complete_total: int = 0
    complete_passed: int = 0

    obs_total: int = 0
    no_missing_passed: int = 0
    no_hallucinated_passed: int = 0
    type_pair_total: int = 0
    type_pair_passed: int = 0

    # (cache_key, "[check_label] evidence snippet", judge note)
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
    """Pair each result JSON with its source row in sample-obs.csv."""
    if not RESULTS_DIR.exists():
        print(f"ERROR: {RESULTS_DIR}/ not found — run extract.py first", file=sys.stderr)
        sys.exit(1)

    # Index CSV by cache key so we can recover the observation text.
    csv_index: dict[str, tuple[str, int]] = {}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            obs = row["observation"]
            sc = int(row["student_count"])
            csv_index[cache_key(obs, sc)] = (obs, sc)

    results: list[ResultFile] = []
    for path in sorted(RESULTS_DIR.glob("*.json")):
        key = path.stem
        if key not in csv_index:
            # Orphaned result (observation no longer in CSV) — skip silently.
            continue
        obs, sc = csv_index[key]
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


def report(m: Metrics, show_failures: bool) -> None:
    eg = pct(m.eg_passed, m.eg_total)
    ot = pct(m.ot_passed, m.ot_total)
    recall = pct(m.golden_signals_matched, m.golden_signals_total)
    precision = pct(m.predicted_signals_matched, m.predicted_signals_total)
    type_acc = pct(m.type_matches, m.type_total)

    rows: list[tuple[str, float, tuple[float, float], str]] = [
        ("Evidence Grounding", eg, TARGETS["evidence_grounding"],
         f"{m.eg_passed}/{m.eg_total} signals"),
        ("Observation Type", ot, TARGETS["observation_type"],
         f"{m.ot_passed}/{m.ot_total} observations"),
        ("Signal Completeness (recall)", recall, TARGETS["signal_completeness"],
         f"{m.golden_signals_matched}/{m.golden_signals_total} golden signals"),
        ("No Hallucinated Signals (precision)", precision,
         TARGETS["no_hallucinated_signals"],
         f"{m.predicted_signals_matched}/{m.predicted_signals_total} predicted signals"),
        ("Type Accuracy", type_acc, TARGETS["type_accuracy"],
         f"{m.type_matches}/{m.type_total} matched pairs"),
    ]

    print()
    print(f"{'Dimension':<40} {'Rate':>8} {'Target':>8} {'Floor':>8}  Result  Detail")
    print("-" * 110)
    for name, rate, (target, floor), detail in rows:
        v = verdict(rate, target, floor)
        print(
            f"{name:<40} {rate*100:>7.1f}% {target*100:>7.0f}% {floor*100:>7.0f}%"
            f"  {v:<6}  {detail}"
        )

    print()
    print(f"Golden-annotated observations scored: {m.golden_observations}")

    if show_failures and m.eg_failures:
        print("\nEvidence grounding failures (first 20):")
        for key, ev in m.eg_failures[:20]:
            snippet = ev if len(ev) <= 100 else ev[:97] + "..."
            print(f"  {key[:12]}  {snippet!r}")
        if len(m.eg_failures) > 20:
            print(f"  ...and {len(m.eg_failures) - 20} more")


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
    golden: GoldenExample,
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
        "golden_signals": [
            {"evidence": s.evidence, "type": s.type}
            for s in golden.signals
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
    raw: dict[str, Any], result_cache_key: str, predicted_count: int
) -> ObservationJudgement:
    per_signal: list[SignalJudgement] = []
    for entry in raw.get("per_signal", []):
        if not isinstance(entry, dict):
            continue
        per_signal.append(
            SignalJudgement(
                signal_index=int(entry.get("signal_index", -1)),
                evidence=str(entry.get("evidence", "")),
                supports_type=_check(entry.get("reasoning_supports_type")),
                supports_competencies=_check(entry.get("reasoning_supports_competencies")),
                supports_confidence=_check(entry.get("reasoning_supports_confidence")),
                complete=_check(entry.get("reasoning_complete")),
            )
        )

    missing: list[tuple[str, str]] = [
        (str(e.get("evidence", "")), str(e.get("note", "")))
        for e in raw.get("missing_signals", [])
        if isinstance(e, dict)
    ]
    hallucinated: list[tuple[int, str]] = [
        (int(e.get("signal_index", -1)), str(e.get("note", "")))
        for e in raw.get("hallucinated_signals", [])
        if isinstance(e, dict)
    ]
    type_disagreements: list[tuple[int, str, str, str]] = [
        (
            int(e.get("signal_index", -1)),
            str(e.get("predicted", "")),
            str(e.get("golden", "")),
            str(e.get("note", "")),
        )
        for e in raw.get("type_disagreements", [])
        if isinstance(e, dict)
    ]

    matched_pair_count = max(0, predicted_count - len(hallucinated))

    return ObservationJudgement(
        cache_key=result_cache_key,
        per_signal=per_signal,
        missing_signals=missing,
        hallucinated_signals=hallucinated,
        type_disagreements=type_disagreements,
        matched_pair_count=matched_pair_count,
    )


def audit_one(
    result: ResultFile,
    golden: GoldenExample,
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
    user_msg = build_judge_user_message(result, raw_signals, golden)
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

    return parse_judge_response(raw_judge, result.cache_key, len(raw_signals))


def aggregate_reasoning(judgements: Iterable[ObservationJudgement]) -> ReasoningMetrics:
    m = ReasoningMetrics()
    for j in judgements:
        m.obs_total += 1
        if not j.missing_signals:
            m.no_missing_passed += 1
        if not j.hallucinated_signals:
            m.no_hallucinated_passed += 1
        m.type_pair_total += j.matched_pair_count
        m.type_pair_passed += max(0, j.matched_pair_count - len(j.type_disagreements))

        for sj in j.per_signal:
            for label, (passed, note) in (
                ("supports_type", sj.supports_type),
                ("supports_competencies", sj.supports_competencies),
                ("supports_confidence", sj.supports_confidence),
                ("complete", sj.complete),
            ):
                if label == "supports_type":
                    m.supports_type_total += 1
                    if passed:
                        m.supports_type_passed += 1
                elif label == "supports_competencies":
                    m.supports_comp_total += 1
                    if passed:
                        m.supports_comp_passed += 1
                elif label == "supports_confidence":
                    m.supports_conf_total += 1
                    if passed:
                        m.supports_conf_passed += 1
                else:
                    m.complete_total += 1
                    if passed:
                        m.complete_passed += 1

                if not passed:
                    snippet = sj.evidence if len(sj.evidence) <= 100 else sj.evidence[:97] + "..."
                    m.failures.append((j.cache_key, f"[{label}] {snippet}", note))
    return m


def report_reasoning(m: ReasoningMetrics, show_failures: bool) -> None:
    rows: list[tuple[str, float, tuple[float, float], str]] = [
        ("Reasoning supports type",
         pct(m.supports_type_passed, m.supports_type_total),
         REASONING_TARGETS["reasoning_supports_type"],
         f"{m.supports_type_passed}/{m.supports_type_total} signals"),
        ("Reasoning supports competencies",
         pct(m.supports_comp_passed, m.supports_comp_total),
         REASONING_TARGETS["reasoning_supports_competencies"],
         f"{m.supports_comp_passed}/{m.supports_comp_total} signals"),
        ("Reasoning supports confidence",
         pct(m.supports_conf_passed, m.supports_conf_total),
         REASONING_TARGETS["reasoning_supports_confidence"],
         f"{m.supports_conf_passed}/{m.supports_conf_total} signals"),
        ("Reasoning complete (Rule 10)",
         pct(m.complete_passed, m.complete_total),
         REASONING_TARGETS["reasoning_complete"],
         f"{m.complete_passed}/{m.complete_total} signals"),
        ("No missing signals vs. golden",
         pct(m.no_missing_passed, m.obs_total),
         REASONING_TARGETS["no_missing_signals"],
         f"{m.no_missing_passed}/{m.obs_total} observations"),
        ("No hallucinated signals vs. golden",
         pct(m.no_hallucinated_passed, m.obs_total),
         REASONING_TARGETS["no_hallucinated_signals"],
         f"{m.no_hallucinated_passed}/{m.obs_total} observations"),
        ("Type agreement vs. golden",
         pct(m.type_pair_passed, m.type_pair_total),
         REASONING_TARGETS["type_agreement"],
         f"{m.type_pair_passed}/{m.type_pair_total} matched pairs"),
    ]

    print()
    print(f"Reasoning Audit (N={m.obs_total} golden-annotated observations)")
    print(f"{'Dimension':<40} {'Rate':>8} {'Target':>8} {'Floor':>8}  Result  Detail")
    print("-" * 110)
    for name, rate, (target, floor), detail in rows:
        v = verdict(rate, target, floor)
        print(
            f"{name:<40} {rate*100:>7.1f}% {target*100:>7.0f}% {floor*100:>7.0f}%"
            f"  {v:<6}  {detail}"
        )

    if show_failures and m.failures:
        print("\nFlagged signals (first 20):")
        for key, label_ev, note in m.failures[:20]:
            note_snip = note if len(note) <= 80 else note[:77] + "..."
            print(f"  {key[:12]}  {label_ev!r}  → {note_snip}")
        if len(m.failures) > 20:
            print(f"  ...and {len(m.failures) - 20} more")


def run_reasoning_audit(
    results: list[ResultFile],
    golden_by_key: dict[str, GoldenExample],
    args: argparse.Namespace,
) -> None:
    judge_prompt = load_judge_prompt()
    audit_candidates: list[tuple[ResultFile, GoldenExample]] = [
        (r, golden_by_key[r.cache_key])
        for r in results
        if r.cache_key in golden_by_key
    ]
    if args.limit is not None:
        audit_candidates = audit_candidates[: args.limit]

    if not audit_candidates:
        print("\nNo golden-matched results to audit.", file=sys.stderr)
        return

    if args.dry_run:
        for result, golden in audit_candidates:
            audit_one(
                result, golden, judge_prompt,
                client=None, force=args.force, dry_run=True,
            )
        return

    load_dotenv(".env.local")
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    def _do_audit(r: ResultFile, g: GoldenExample) -> ObservationJudgement | None:
        return audit_one(
            r, g, judge_prompt, client, force=args.force, dry_run=False,
        )

    judgements: list[ObservationJudgement] = []
    errors = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_do_audit, r, g): r for r, g in audit_candidates}
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
    args = parser.parse_args()

    results = load_results()
    if not results:
        print("No results found. Run `uv run extract.py` first.", file=sys.stderr)
        sys.exit(1)

    golden_by_key: dict[str, GoldenExample] = {}
    for ex in parse_golden(GOLDEN_PATH):
        golden_by_key[cache_key(ex.observation, ex.student_count)] = ex

    m = Metrics()
    for result in results:
        score_programmatic(result, m)
        gold = golden_by_key.get(result.cache_key)
        if gold is not None:
            score_against_golden(result, gold, m)

    print(f"Scored {len(results)} results "
          f"({len(golden_by_key)} golden annotations available)")
    report(m, show_failures=args.show_failures)

    if args.audit_reasoning:
        run_reasoning_audit(results, golden_by_key, args)


if __name__ == "__main__":
    main()
