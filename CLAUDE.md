# Layer 1: Raw Extraction Pipeline

## What this is

**LLM-assisted content analysis** of teacher observations — turning free-text classroom notes into structured, evidence-grounded signals. Two pieces:

1. **Extraction** — structured information extraction from qualitative data. Each observation is quote-anchored: every signal must reference verbatim text, no inferential leaps. Curriculum-agnostic on purpose; framework-coupled analysis (CASEL, IB ATL, standards) happens downstream.
2. **Evaluation** — **LLM-as-a-judge** auditing, both reference-free (judge re-checks grounding and over-extraction) and reference-based (against golden annotations). Cross-family by design: GPT judges Claude's output to avoid self-enhancement bias. A **human-in-the-loop calibration** harness measures judge↔human agreement on flagged rows.

The umbrella term is **LLM-based annotation with judge-based evaluation** — a subfield of AI evals applied to qualitative education data.

The full architectural framework — what each layer does, how they compose,
non-goals — lives in [`docs/framework.md`](docs/framework.md). Read it before
touching Layer 1.5 or anything that crosses layer boundaries.

## How it runs

Reads teacher observations from a per-school JSON export, runs each one through an LLM, and writes structured signals to `outputs/extractions.jsonl`. `eval.py` then scores those extractions.

Canonical schema and extraction rules live in `prompts/extractor.md`. When in doubt, read that file.

## Run it

```bash
uv sync --all-packages
uv run --package layer-1 layer-1-extract --limit 10   # extract (always use --limit until told otherwise)
uv run --package layer-1 layer-1-eval                 # programmatic checks + LLM audit
uv run --package layer-1 layer-1-eval --no-audit      # skip the audit for zero LLM cost
```

Inputs live in `inputs/observations-{school}-{YYYY-MM-DD}.json` (gitignored, real client data). Outputs go to `outputs/` (also gitignored).

## Calibration

The audit flags suspicious extractions. To check whether the judge is right:

```bash
uv run python packages/layer-1/scripts/calibration/export.py                           # flagged rows → CSV
# fill `human_verdict` (flagged / not_flagged) and `human_note` by hand
uv run python packages/layer-1/scripts/calibration/agreement.py packages/layer-1/outputs/analysis/calibration-{ts}.csv
```

## Rules that aren't in the code

- **Always pass `--limit 10` to `extract.py`** until told otherwise. Full runs burn API credits.
- **Don't add framework fields to Layer 1.** No CASEL, no IB ATL, no mastery levels, no standard matches. Those live in Evolution and Lila downstream. If you're reaching for one, you're in the wrong module.
- **The judge is cross-family on purpose.** Default judge is `openai/gpt-5.4`; the extractor is Claude. Same-family judging has documented self-enhancement bias.
- **Pydantic guards the LLM boundary.** Malformed responses raise — don't add silent defaults for required fields.

## Environment

```
OPENROUTER_API_KEY=...
```

## Synced rules

Team conventions sync from [data-harness](https://github.com/biogabriel7/data-harness) via the Conductor setup script. Re-sync manually:

```bash
$DATA_HARNESS_PATH/scripts/sync.sh . [project-name]
```
