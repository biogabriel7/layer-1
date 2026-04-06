# Layer 1: Raw Extraction Pipeline

## Project Overview

Reads teacher observations from `sample-obs.csv`, sends each one to an LLM via OpenRouter, and extracts structured insight signals. Outputs JSON results used by `eval.py` to measure extraction quality.

## Stack

- Python 3.13, UV (`uv run`, `uv add` — never pip)
- OpenRouter via `openai` SDK (base URL swap)
- `python-dotenv` for env vars
- `mypy --strict`, `ruff` for linting

## Build & Run

```bash
uv sync                        # installs dependencies into the project's virtual environment
uv run extract.py --limit 5   # runs extract.py in the venv, stops after 5 rows (for testing)
uv run extract.py              # full run (3,119 observations)
uv run eval.py                 # score results against golden dataset
```

## File Structure

```
extract.py       # reads CSV → calls API → writes results/
eval.py          # reads results/ + golden/ → reports 5 eval metrics
prompt.md        # system prompt — do not modify, managed separately
sample-obs.csv   # 3,119 real observations (input)
results/         # extraction output, gitignored
golden/          # human-annotated observations for eval
```

## Deterministic Post-Processing

After parsing the LLM response, always enforce these in code regardless of what the model returns:

- `signal_count` = `len(signals)`
- `observation_type`: `student_count == 1` → `"individual"`, `student_count > 1` → `"group"`
- `insight_density`: `0-1 signals` → `"low"`, `2-3` → `"medium"`, `4+` → `"high"`

## API Config

- Model: `anthropic/claude-sonnet-4-6` via OpenRouter
- `temperature: 0.0`
- `response_format: {"type": "json_object"}`
- Cache results by SHA256 of `(observation + student_count)` — skip API call if cached
- `--force` flag busts cache and re-calls all observations
- `--limit N` processes only first N rows (smoke testing without burning API credits)
- `--dry-run` prints the prompt without calling the API
- Observations are independent — parallelize with `--workers N`

## Eval Dimensions

`eval.py` measures 5 pass/fail dimensions:

| Dimension | How to check | Target |
|---|---|---|
| Evidence Grounding | `evidence in observation` (case-insensitive, whitespace-normalized) | 100% |
| Signal Completeness | recall vs golden annotations | ≥85% |
| No Hallucinated Signals | precision vs golden annotations | 100% |
| Type Accuracy | type match vs golden annotations | ≥95% |
| Observation Type | matches `student_count` rule | 100% |

Evidence Grounding and Observation Type are programmatic — run on all 3,119 observations. The other three require `golden/` annotations.

## Project-Specific Rules

- **TEMPORARY: Always use `--limit 10` when running `extract.py` — never run the full dataset**
- `eval.py` never calls the API — reads from `results/` only
- `results/` and `.env` are gitignored

## Environment

```
OPENROUTER_API_KEY=...
```

## Synced Rules
This project uses shared team conventions from the [data-harness](https://github.com/biogabriel7/data-harness) repo.

Rules sync automatically via Conductor setup script. To sync manually:
```bash
$DATA_HARNESS_PATH/scripts/sync.sh . [project-name]
```
