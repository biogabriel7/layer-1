"""Reads sample-obs.csv, sends each observation to an LLM via OpenRouter,
and extracts structured insight signals to results/."""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env.local")

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

RESULTS_DIR = Path("results")
PROMPT_PATH = Path("prompt.md")
GOLDEN_PATH = Path("golden.md")
MODEL = "anthropic/claude-opus-4-6"


def cache_key(observation: str, student_count: int) -> str:
    raw = f"{observation}|{student_count}"
    return hashlib.sha256(raw.encode()).hexdigest()


def load_system_prompt() -> str:
    if not PROMPT_PATH.exists():
        print("ERROR: prompt.md not found", file=sys.stderr)
        sys.exit(1)
    return PROMPT_PATH.read_text()


def build_user_message(observation: str, student_count: int) -> str:
    return json.dumps({"observation": observation, "student_count": student_count})


def postprocess(result: dict[str, object], student_count: int) -> dict[str, object]:
    """Enforce deterministic fields regardless of what the model returned."""
    signals = result.get("signals", [])
    assert isinstance(signals, list)
    signal_count = len(signals)

    result["signal_count"] = signal_count

    if student_count == 1:
        result["observation_type"] = "individual"
    else:
        result["observation_type"] = "group"

    if signal_count <= 1:
        result["insight_density"] = "low"
    elif signal_count <= 3:
        result["insight_density"] = "medium"
    else:
        result["insight_density"] = "high"

    return result


def call_api(
    client: OpenAI,
    system_prompt: str,
    observation: str,
    student_count: int,
) -> dict[str, object]:
    user_msg = build_user_message(observation, student_count)
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": user_msg},
        ],
        extra_body={
            "transforms": ["anthropic-cache"],
        },
    )
    content = response.choices[0].message.content
    assert content is not None
    # OpenRouter sometimes wraps JSON in markdown code fences
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]  # drop opening ```json
        text = text.rsplit("```", 1)[0]  # drop closing ```
    return json.loads(text)  # type: ignore[no-any-return]


def process_row(
    client: OpenAI,
    system_prompt: str,
    comment_key: str,
    observation: str,
    student_count: int,
    *,
    force: bool,
    dry_run: bool,
) -> str:
    """Process a single observation row. Returns the cache key."""
    key = cache_key(observation, student_count)
    out_path = RESULTS_DIR / f"{key}.json"

    if not force and out_path.exists():
        return key

    if dry_run:
        print(f"[dry-run] {comment_key}")
        print(f"  system: {system_prompt[:80]}...")
        print(f"  user:   {build_user_message(observation, student_count)[:120]}...")
        return key

    raw = call_api(client, system_prompt, observation, student_count)

    required_signal_keys = {
        "evidence", "type", "sel_competencies",
        "observation_confidence", "reasoning",
    }
    signals = raw.get("signals", [])
    if isinstance(signals, list):
        for i, signal in enumerate(signals):
            if isinstance(signal, dict):
                for rk in required_signal_keys:
                    if rk not in signal:
                        raise ValueError(f"signal[{i}] missing required key: {rk}")

    signals = raw.get("signals", [])
    assert isinstance(signals, list)
    result = postprocess({"signals": signals}, student_count)

    output = {
        "signals": result["signals"],
        "observation_type": result["observation_type"],
        "signal_count": result["signal_count"],
        "insight_density": result["insight_density"],
    }
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    return key


def load_csv(path: str = "sample-obs.csv") -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_golden_rows(limit: int | None = None) -> list[dict[str, str]]:
    """Read just `Observation:` and `Student Count:` from golden.md.

    Deliberately does NOT touch the **Output** section, so the answer key
    cannot enter this script even by accident. Returns rows in the same
    shape as load_csv() so the rest of the pipeline stays unchanged.
    """
    if not GOLDEN_PATH.exists():
        print(f"ERROR: {GOLDEN_PATH} not found", file=sys.stderr)
        sys.exit(1)

    text = GOLDEN_PATH.read_text()
    parts = re.split(r"^##\s*Example\s+(\d+)\s*$", text, flags=re.MULTILINE)
    # parts = [preamble, num, body, num, body, ...]

    rows: list[dict[str, str]] = []
    for i in range(1, len(parts), 2):
        number = parts[i]
        body = parts[i + 1]
        obs_match = re.search(
            r'Observation:\s*"(.+?)"\s*\n\s*Student Count:',
            body,
            re.DOTALL,
        )
        sc_match = re.search(r"Student Count:\s*(\d+)", body)
        if not obs_match or not sc_match:
            continue
        rows.append({
            "comment_key": f"golden#{number}",
            "observation": obs_match.group(1),
            "student_count": sc_match.group(1),
        })
        if limit is not None and len(rows) >= limit:
            break
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract insight signals from observations")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N rows")
    parser.add_argument("--force", action="store_true", help="Bust cache and re-call all")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without API calls")
    parser.add_argument("--workers", type=int, default=1, help="Parallel workers")
    parser.add_argument(
        "--golden",
        type=int,
        default=None,
        metavar="N",
        help="Extract first N golden.md observations instead of sample-obs.csv "
             "(answer key is never read)",
    )
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)

    system_prompt = load_system_prompt()

    if args.golden is not None:
        rows = load_golden_rows(limit=args.golden)
    else:
        rows = load_csv()
        if args.limit is not None:
            rows = rows[: args.limit]

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
    )

    processed = 0
    cached = 0
    errors = 0

    def handle_row(row: dict[str, str]) -> tuple[str, bool, str | None]:
        comment_key = row["comment_key"]
        observation = row["observation"]
        student_count = int(row["student_count"])
        key = cache_key(observation, student_count)
        out_path = RESULTS_DIR / f"{key}.json"
        was_cached = not args.force and out_path.exists()

        try:
            process_row(
                client,
                system_prompt,
                comment_key,
                observation,
                student_count,
                force=args.force,
                dry_run=args.dry_run,
            )
            return key, was_cached, None
        except Exception as e:
            return key, False, f"{comment_key}: {e}"

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(handle_row, row): row for row in rows}
        for future in as_completed(futures):
            key, was_cached, error = future.result()
            if error:
                print(f"ERROR {error}", file=sys.stderr)
                errors += 1
            elif was_cached:
                cached += 1
            else:
                processed += 1

    total = processed + cached + errors
    print(f"\nDone: {total} rows | {processed} extracted | {cached} cached | {errors} errors")


if __name__ == "__main__":
    main()
