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
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RESULTS_DIR = Path("results")
CSV_PATH = Path("sample-obs.csv")
GOLDEN_PATH = Path("golden.md")

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
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Score Layer 1 extraction results")
    parser.add_argument(
        "--show-failures",
        action="store_true",
        help="Print evidence grounding failures for debugging",
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


if __name__ == "__main__":
    main()
