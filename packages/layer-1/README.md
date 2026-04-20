# Layer 1: Raw Extraction Pipeline

LLM-assisted content analysis of teacher observations — turning free-text classroom notes into structured, evidence-grounded signals. Two pieces:

1. **Extraction** (`extract.py`) — structured information extraction from qualitative data. Every signal is quote-anchored: it must reference verbatim text from the observation, no inferential leaps. Curriculum-agnostic on purpose; framework-coupled analysis (CASEL, IB ATL, standards) lives in downstream modules.
2. **Evaluation** (`eval.py`) — **LLM-as-a-judge** auditing. The reference-free judge re-checks grounding and over-extraction on every extraction. Cross-family by design: GPT judges Claude's output to avoid self-enhancement bias.

The umbrella term is **LLM-based annotation with judge-based evaluation** — a subfield of AI evals applied to qualitative education data.

## Install

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.local.example .env.local   # then fill in OPENROUTER_API_KEY
```

## Run

```bash
uv run extract.py --limit 10      # extract 10 observations (see --help for flags)
uv run eval.py                    # programmatic checks + LLM audit
uv run eval.py --no-audit         # programmatic only, zero LLM cost
```

Inputs live in `inputs/observations-{school-slug}-{YYYY-MM-DD}.json` (gitignored — real client data). Outputs go to `outputs/extractions.jsonl` and `outputs/analysis/eval-report.json`. Upstream quality scores are kept in a sidecar at `outputs/quality-checks.jsonl`, joinable on `observation_id`.

## Canonical schema

The extraction schema and per-facet rules live in `prompts/extractor.md`. When a signal's shape or a facet cue is ambiguous, that file is the source of truth — not this README.

## Calibration

The judge flags suspicious extractions. To check whether the judge is right, the calibration harness exports flagged rows for hand-labeling and computes judge↔human agreement:

```bash
uv run scripts/calibration/export.py                           # flagged rows → CSV
# fill `human_verdict` (flagged / not_flagged) and `human_note` by hand
uv run scripts/calibration/agreement.py outputs/analysis/calibration-{ts}.csv
```

## Layout

```
extract.py               CLI: observations → LLM → outputs/extractions.jsonl
eval.py                  CLI: extractions → programmatic checks + LLM audit → eval-report.json

pipeline/                library: schema, loader, scoring, judge, analysis, report, llm, text
prompts/                 system prompts (extractor + reference-free judge)
scripts/conductor/       workspace hooks (bash)
scripts/calibration/     human-in-the-loop review helpers (python)
inputs/                  per-school observation JSON (gitignored)
outputs/                 generated artifacts (gitignored)
```

## Design notes

- **No framework coupling in Layer 1.** CASEL, IB ATL, mastery levels, standards matching — all live in downstream modules. Layer 1 emits shape, not interpretation.
- **Pydantic guards the LLM boundary.** Malformed responses raise at parse time; required fields are never silently defaulted.
- **Observations are independent.** Parallelize freely via `--workers N`.
