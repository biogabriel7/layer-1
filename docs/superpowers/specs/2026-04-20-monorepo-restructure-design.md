# Monorepo Restructure — Design

**Date:** 2026-04-20
**Status:** Approved for implementation planning
**Repo:** `biogabriel7/layer-1` → `biogabriel7/extraction-pipeline`

## Goal

Turn the current single-package `layer-1` repository into a UV-workspace monorepo so that (a) a new `layer-1.5` (student-contextualized extraction) can be built as a sibling package, (b) agents can work on different layers in isolated Conductor workspaces without stepping on each other, and (c) shared plumbing (LLM client, text utilities, Layer 1 output schema) lives in one place rather than being copy-pasted.

The broader pipeline — Layer 2 (profile accumulation), Layer 3 (wellness/risk detection) — is out of scope for this restructure but the layout must accommodate adding them later as additional `packages/` members.

## Non-goals

- No changes to extraction logic, prompts, or eval metrics.
- No implementation of Layer 1.5 beyond an empty package skeleton.
- No GitHub-side repo rename automation — the repo is renamed via the GitHub UI.
- No Makefile / justfile. UV commands are short enough.

## Approach (Approach A: UV workspace with shared `core/`)

A single-repo UV workspace with three initial members:

- `core/` — shared library (LLM client, text utilities, Layer 1 output schema, generic jsonl helpers).
- `layer-1/` — current project, moved under `packages/`.
- `layer-1.5/` — empty skeleton for future agent work.

One root `.venv/`, one `uv.lock`, one set of dev tools (ruff, mypy). Each layer has its own `pyproject.toml`, prompts, CLI entry points, and eval suite.

Rejected alternatives:

- **Flat sibling packages, no workspace, two venvs** — strongest isolation but duplicates OpenRouter plumbing the moment Layer 1.5 starts.
- **Single package with submodules** — blurs the layer boundaries that the framework doc is careful to preserve.

## Final layout

```
extraction-pipeline/              ← repo root (was layer-1)
├── pyproject.toml                ← UV workspace root; dev tools only
├── uv.lock                       ← single lockfile
├── .venv/                        ← single venv
├── .python-version
├── README.md                     ← top-level: repo purpose, how to pick a layer
├── CLAUDE.md                     ← shared rules
├── conductor.json                ← unchanged script paths
├── .gitignore                    ← adjusted for per-package outputs
├── .env                          ← shared OPENROUTER_API_KEY
│
├── packages/
│   ├── core/
│   │   ├── pyproject.toml
│   │   └── src/core/
│   │       ├── __init__.py
│   │       ├── llm.py            ← from pipeline/llm.py
│   │       ├── text.py           ← from pipeline/text.py
│   │       ├── io.py             ← generic jsonl helpers (factored from loader.py)
│   │       └── schema/
│   │           ├── __init__.py
│   │           └── layer1.py     ← Signal, ExtractionOutput, Participant
│   │
│   ├── layer-1/
│   │   ├── pyproject.toml
│   │   ├── README.md             ← Layer-1-specific
│   │   ├── prompts/
│   │   │   ├── extractor.md
│   │   │   └── judge_reference_free.md
│   │   ├── scripts/calibration/
│   │   ├── inputs/               ← symlink (target updated by Conductor setup)
│   │   ├── outputs/              ← gitignored
│   │   ├── tasks/
│   │   └── src/layer_1/
│   │       ├── __init__.py
│   │       ├── cli/
│   │       │   ├── extract.py    ← entry point: layer-1-extract
│   │       │   └── eval.py       ← entry point: layer-1-eval
│   │       └── pipeline/
│   │           ├── models.py     ← dataclasses (ResultFile, Metrics, AuditMetrics)
│   │           ├── schema.py     ← audit-only Pydantic (AuditCheck, AuditResponse)
│   │           ├── loader.py
│   │           ├── scoring.py
│   │           ├── report.py
│   │           ├── analysis.py
│   │           └── judge.py
│   │
│   └── layer-1.5/
│       ├── pyproject.toml
│       ├── README.md             ← stub
│       ├── prompts/              ← empty
│       ├── outputs/              ← gitignored
│       └── src/layer_1_5/
│           └── __init__.py
│
├── docs/
│   ├── framework.md              ← the full Analysis Framework doc
│   └── superpowers/specs/        ← design docs land here
│
├── scripts/conductor/            ← setup/run/archive stay at repo root
└── tasks/                        ← repo-level plans
```

## `core/` boundary

`core/` holds only what crosses layer boundaries. The guiding principle: if only one layer uses it, it does not belong in `core/`.

### Moves to `core/`

| Current | Destination | Why |
|---|---|---|
| `pipeline/llm.py` (`make_client`, `call_json`) | `core/llm.py` | Pure OpenRouter plumbing, no Layer 1 semantics |
| `pipeline/text.py` (`normalize`, `evidence_grounded`, `cache_key`) | `core/text.py` | Substring match + hashing are layer-agnostic |
| `Signal`, `ExtractionOutput`, `Participant` (from `pipeline/schema.py`) | `core/schema/layer1.py` | The interface between Layer 1 and Layer 1.5 — belongs at the boundary |
| generic jsonl read/write helpers (factored from `pipeline/loader.py`) | `core/io.py` | Both layers emit/read jsonl |

### Stays in `layer-1/`

| File | Why it stays |
|---|---|
| `models.py` (`ResultFile`, `Metrics`, `AuditMetrics` dataclasses) | Internal eval state, never consumed externally |
| `schema.py` (audit schemas: `AuditCheck`, `AuditResponse`, `AuditChecks`, `AuditSignalEntry`) | Judge-output schema is Layer-1-specific evaluation internal |
| `loader.py` (layer-1-specific paths: `EXTRACTIONS_PATH`, `OBSERVATIONS_PATH`) | Tied to Layer 1's file layout |
| `scoring.py`, `report.py`, `analysis.py`, `judge.py` | All tied to Layer 1's eval metrics |

### Layer 1.5's expected imports

```python
from core.llm import make_client, call_json
from core.text import normalize, cache_key
from core.io import read_jsonl
from core.schema.layer1 import ExtractionOutput, Signal
```

Layer 1.5 never imports from `layer_1.*`. The only coupling is via the `core.schema.layer1` contract.

## UV workspace configuration

### Root `pyproject.toml`

```toml
[project]
name = "extraction-pipeline"
version = "0.1.0"
description = "Layered extraction pipeline for SEL teacher observations"
requires-python = ">=3.13"

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
core    = { workspace = true }
layer-1 = { workspace = true }

[dependency-groups]
dev = [
  "mypy>=1.20.0",
  "ruff>=0.15.9",
]

[tool.mypy]
strict = true

[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "W"]

[tool.ruff.lint.isort]
known-first-party = ["core", "layer_1", "layer_1_5"]
```

### `packages/core/pyproject.toml`

```toml
[project]
name = "core"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
  "openai>=2.30.0",
  "pydantic>=2.0",
  "python-dotenv>=1.2.2",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/core"]
```

### `packages/layer-1/pyproject.toml`

```toml
[project]
name = "layer-1"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["core"]

[project.scripts]
layer-1-extract = "layer_1.cli.extract:main"
layer-1-eval    = "layer_1.cli.eval:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/layer_1"]
```

### `packages/layer-1.5/pyproject.toml`

```toml
[project]
name = "layer-1-5"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["core"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/layer_1_5"]
```

### Conventions baked in

- **Package names use hyphens; Python import paths use underscores.** `layer-1` → `layer_1`, `layer-1.5` → `layer_1_5`. Standard Python; UV handles the mapping.
- **`extract.py` and `eval.py` become installable entry points.** Moved under `src/layer_1/cli/`; each gets a `main()` function wired to `[project.scripts]`.

### How things are run

```bash
uv sync                                              # installs core + all layers + dev
uv run --package layer-1 layer-1-extract --limit 10
uv run --package layer-1 layer-1-eval
uv run --package layer-1 layer-1-eval --no-audit
uv run mypy packages/
uv run ruff check packages/
```

## Conductor & agent workflow

### `conductor.json` — unchanged

```json
{
  "scripts": {
    "setup":   "./scripts/conductor/setup.sh",
    "run":     "./scripts/conductor/run.sh",
    "archive": "./scripts/conductor/archive.sh"
  }
}
```

### Changes to `scripts/conductor/setup.sh`

- `inputs/` symlink target changes from `$PWD/inputs` to `$PWD/packages/layer-1/inputs`.
- `uv sync` runs once at workspace root; one `.venv/` covers all packages.
- `.env` copy stays at repo root (shared across layers).
- `PROJECT_NAME` changes from `"quality-observations"` to `"extraction-pipeline"` if data-harness has a matching rule set; otherwise the old name is kept and this is flagged for follow-up.

### `run.sh` — kept as stub

No dev server to launch. Current version is already a stub.

### Agent pattern

**Default pattern: one agent per layer, separate Conductor workspaces.**

- Agent on Layer 1: workspace on a `feat/layer-1-*` branch.
- Agent on Layer 1.5: a different workspace on a `feat/layer-1-5-*` branch.
- Each workspace has its own `inputs/` symlink (created by `setup.sh`) and its own `.venv/`. They share the repo but touch disjoint file sets.
- Merge independently into `main` via PRs.

**Exception: contract changes to `core/`** require a single workspace that touches both layers coherently.

### Handoff file — not shared state

`packages/layer-1/outputs/extractions.jsonl` is Layer 1.5's input. Outputs are gitignored and regenerated per workspace. An agent on Layer 1.5 runs `uv run --package layer-1 layer-1-extract --limit N` in its own workspace to get fresh input — it never depends on another workspace's outputs.

## Migration plan

Ordered list of steps to execute during implementation. No behavior changes — only moves + import rewrites.

1. **Rename the GitHub repo** (manual, via GitHub UI): `biogabriel7/layer-1` → `biogabriel7/extraction-pipeline`. Update local remote: `git remote set-url origin https://github.com/biogabriel7/extraction-pipeline.git`.

2. **Create the skeleton**: write the root `pyproject.toml` and the three package `pyproject.toml` files (exact contents in the **UV workspace configuration** section above), plus empty `__init__.py` files under each `src/` tree.

3. **`git mv` existing files into `packages/layer-1/`** (preserves history):
   - `pipeline/` → `packages/layer-1/src/layer_1/pipeline/`
   - `extract.py` → `packages/layer-1/src/layer_1/cli/extract.py`
   - `eval.py` → `packages/layer-1/src/layer_1/cli/eval.py`
   - `prompts/` → `packages/layer-1/prompts/`
   - `scripts/calibration/` → `packages/layer-1/scripts/calibration/`
   - `tasks/` → `packages/layer-1/tasks/`
   - `README.md` → `packages/layer-1/README.md` (top-level `README.md` rewritten)

4. **Extract `core/` modules** (move + adjust imports):
   - `pipeline/llm.py` → `packages/core/src/core/llm.py`
   - `pipeline/text.py` → `packages/core/src/core/text.py`
   - `Signal`, `ExtractionOutput`, `Participant` (from `pipeline/schema.py`) → `packages/core/src/core/schema/layer1.py`
   - Generic jsonl helper (factored from `pipeline/loader.py`) → `packages/core/src/core/io.py`

5. **Rewrite imports** (mechanical):
   - `from pipeline.llm` → `from core.llm`
   - `from pipeline.text` → `from core.text`
   - `from pipeline.schema import Signal, ExtractionOutput, Participant` → `from core.schema.layer1 import Signal, ExtractionOutput, Participant`
   - `from pipeline.{models,loader,scoring,report,analysis,judge}` → `from layer_1.pipeline.{models,loader,scoring,report,analysis,judge}`

6. **Wire CLI entry points**: add `def main()` to `extract.py` and `eval.py` if not already; confirm `[project.scripts]` declarations resolve.

7. **Update Conductor setup**: change `inputs/` symlink target to `packages/layer-1/inputs` in `scripts/conductor/setup.sh`; update `PROJECT_NAME` if applicable.

8. **Update `.gitignore`**: add `packages/*/outputs/`, `packages/*/.venv/`.

9. **Move `CLAUDE.md` to repo root**: update "Run it" paths to `uv run --package layer-1 ...`. Add pointer to `docs/framework.md`.

10. **Add `docs/framework.md`**: drop the Analysis Framework doc into `docs/framework.md`.

11. **Recreate `inputs/` symlink for the current workspace**: the existing symlink at the old repo-root location needs to be deleted and recreated at `packages/layer-1/inputs` pointing to the real input directory. (Step 7 only updates `setup.sh` for *future* workspaces; this step fixes the in-flight one.)

12. **Verify**:
    ```bash
    uv sync
    uv run --package layer-1 layer-1-extract --limit 2
    uv run --package layer-1 layer-1-eval --no-audit
    uv run mypy packages/
    uv run ruff check packages/
    ```

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| `git mv` history lost | Use `git mv` (not `rm + add`); verify with `git log --follow` on one moved file before committing |
| Import rewrites miss a spot | `mypy` catches unresolved imports; also grep for `from pipeline` and `import pipeline` before committing each step |
| `inputs/` symlink points to old path after move | Recreate symlink explicitly; Conductor re-runs `setup.sh` for new workspaces so it self-heals there |
| `data-harness` sync expects project name `quality-observations` | Check whether data-harness has a rule set for `extraction-pipeline`; if not, keep the old `PROJECT_NAME` temporarily and flag for follow-up |
| Calibration scripts have hardcoded paths | Audit `scripts/calibration/` for paths like `outputs/analysis/...`; update if relative to old root |
| Existing open PRs / branches break on rename | GitHub auto-redirects the URL; local clones need `git remote set-url`. Any open PRs survive the rename |

## Verification criteria

The restructure is complete when:

- `uv sync` at repo root succeeds.
- `uv run --package layer-1 layer-1-extract --limit 2` produces a valid `extractions.jsonl` under `packages/layer-1/outputs/`.
- `uv run --package layer-1 layer-1-eval --no-audit` reports on the extraction.
- `uv run mypy packages/` passes with the existing strict config.
- `uv run ruff check packages/` passes.
- `git log --follow packages/core/src/core/llm.py` shows history going back through the old `pipeline/llm.py`.
- `packages/layer-1.5/` exists with a working `pyproject.toml` (empty package, but `uv sync` picks it up).
- Conductor setup script creates a new workspace cleanly: `inputs/` symlinked at `packages/layer-1/inputs`, `.venv/` populated at root, `.env` copied.
