# Monorepo Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the single-package `layer-1` repository into a UV-workspace monorepo (`extraction-pipeline`) with three initial members — `core/`, `layer-1/`, `layer-1.5/` — so Layer 1.5 can be built as a sibling package and agents can work on different layers in isolated Conductor workspaces.

**Architecture:** UV workspace at the repo root with members under `packages/`. Shared plumbing (LLM client, text utilities, Layer 1 output schema, generic jsonl helpers) lives in `core/`. Each layer is a self-contained package with its own `pyproject.toml`, prompts, CLI entry points, and eval suite. Layer 1.5 consumes Layer 1's outputs via file handoff — no Python-level import from `layer_1`.

**Tech Stack:** Python 3.13, UV workspace, hatchling build backend, Pydantic 2, OpenAI SDK (against OpenRouter), mypy strict, ruff.

---

## Reference spec

Full design: `docs/superpowers/specs/2026-04-20-monorepo-restructure-design.md`. Read that first if any part of this plan feels under-specified.

## Parallel manual step (user does this, not the agent)

The user renames the GitHub repo `biogabriel7/layer-1` → `biogabriel7/extraction-pipeline` via the GitHub UI at any time and then updates their local remote with:

```
git remote set-url origin https://github.com/biogabriel7/extraction-pipeline.git
```

This does not block any task below. The agent does not need to verify the remote URL.

## File structure — final target

This is the target layout; the plan walks through building it up. Every path below is relative to the repo root.

- `pyproject.toml` — workspace declaration + dev tools (ruff, mypy); no runtime deps
- `uv.lock` — single lockfile
- `README.md` — top-level repo README
- `CLAUDE.md` — shared rules, moved from current location (already at root)
- `conductor.json` — unchanged script paths
- `.gitignore` — adjusted for per-package outputs
- `.env` — shared OPENROUTER_API_KEY (unchanged)
- `scripts/conductor/{setup,run,archive}.sh` — stays at repo root
- `docs/framework.md` — the Analysis Framework doc
- `docs/superpowers/{specs,plans}/` — this plan + the spec
- `packages/core/pyproject.toml`
- `packages/core/src/core/__init__.py`
- `packages/core/src/core/llm.py` — moved from `pipeline/llm.py`
- `packages/core/src/core/text.py` — moved from `pipeline/text.py`
- `packages/core/src/core/io.py` — new; generic jsonl helpers
- `packages/core/src/core/schema/__init__.py`
- `packages/core/src/core/schema/layer1.py` — `Signal`, `ExtractionOutput`, `Participant` + Literal types, split out of `pipeline/schema.py`
- `packages/layer-1/pyproject.toml`
- `packages/layer-1/README.md` — layer-specific; moved from repo-root README
- `packages/layer-1/prompts/{extractor,judge_reference_free}.md`
- `packages/layer-1/scripts/calibration/*`
- `packages/layer-1/inputs` — symlink to the real inputs directory
- `packages/layer-1/outputs/` — gitignored
- `packages/layer-1/tasks/` — moved from repo root
- `packages/layer-1/src/layer_1/__init__.py`
- `packages/layer-1/src/layer_1/cli/{__init__,extract,eval}.py`
- `packages/layer-1/src/layer_1/pipeline/{__init__,models,loader,schema,scoring,report,analysis,judge}.py`
- `packages/layer-1.5/pyproject.toml`
- `packages/layer-1.5/README.md` — one-line stub
- `packages/layer-1.5/src/layer_1_5/__init__.py`

---

## Task 1: Pre-migration sanity check

**Why first:** confirm the current layout works end-to-end before touching anything. If `extract.py` fails now (e.g., missing API key, input file moved), we want to know before we start rearranging files — not halfway through Task 3.

**Files:** none created; this task does not commit.

- [ ] **Step 1: Confirm extract works**

Run: `uv run python extract.py --limit 2 --force`
Expected: exits 0; `outputs/extractions.jsonl` has 2 JSON lines; `outputs/quality-checks.jsonl` populated.

- [ ] **Step 2: Confirm eval works (no audit, zero LLM cost)**

Run: `uv run python eval.py --no-audit`
Expected: exits 0; prints a programmatic metrics table; `outputs/analysis/eval-report.json` exists.

- [ ] **Step 3: No commit**

This task only confirms a working starting point.

---

## Task 2: Scaffold empty package skeletons (old layout still works)

**Why next:** create every new file and directory without moving anything yet. The old `pipeline/`, `extract.py`, `eval.py` still run exactly as before because we do not touch the root `pyproject.toml`.

**Files:**
- Create: `packages/core/pyproject.toml`
- Create: `packages/core/src/core/__init__.py`
- Create: `packages/core/src/core/schema/__init__.py`
- Create: `packages/layer-1/pyproject.toml`
- Create: `packages/layer-1/src/layer_1/__init__.py`
- Create: `packages/layer-1/src/layer_1/cli/__init__.py`
- Create: `packages/layer-1/src/layer_1/pipeline/__init__.py`
- Create: `packages/layer-1.5/pyproject.toml`
- Create: `packages/layer-1.5/README.md`
- Create: `packages/layer-1.5/src/layer_1_5/__init__.py`

- [ ] **Step 1: Create `packages/core/pyproject.toml`**

```toml
[project]
name = "core"
version = "0.1.0"
description = "Shared library for the extraction pipeline (LLM client, text utilities, Layer 1 output schema)"
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

- [ ] **Step 2: Create empty `__init__.py` files for core**

Both of these are empty files:

- `packages/core/src/core/__init__.py`
- `packages/core/src/core/schema/__init__.py`

- [ ] **Step 3: Create `packages/layer-1/pyproject.toml`**

```toml
[project]
name = "layer-1"
version = "0.1.0"
description = "Layer 1: raw extraction from teacher observations"
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

- [ ] **Step 4: Create empty `__init__.py` files for layer-1**

Two empty files (we intentionally do NOT pre-create `pipeline/__init__.py` — the existing `pipeline/` directory gets moved wholesale in Task 3 and brings its own `__init__.py` with it):

- `packages/layer-1/src/layer_1/__init__.py`
- `packages/layer-1/src/layer_1/cli/__init__.py`

- [ ] **Step 5: Create `packages/layer-1.5/pyproject.toml`**

```toml
[project]
name = "layer-1-5"
version = "0.1.0"
description = "Layer 1.5: student-contextualized extraction (skeleton)"
requires-python = ">=3.13"
dependencies = ["core"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/layer_1_5"]
```

- [ ] **Step 6: Create `packages/layer-1.5/README.md`**

Content:

```markdown
# Layer 1.5 — Student-Contextualized Extraction

Re-interprets Layer 1 signals through what we already know about the student.
Consumes `packages/layer-1/outputs/extractions.jsonl`.

See `docs/framework.md` for the full framework design.
```

- [ ] **Step 7: Create empty `__init__.py` for layer-1.5**

- `packages/layer-1.5/src/layer_1_5/__init__.py`

- [ ] **Step 8: Sanity check — old layout still works**

Run: `uv run python extract.py --limit 1`
Expected: exits 0 (the root `pyproject.toml` has not changed yet, so UV ignores the new `packages/*/pyproject.toml` files).

- [ ] **Step 9: Commit**

```bash
git add packages/
git commit -m "chore(monorepo): scaffold packages/{core,layer-1,layer-1.5}

Creates empty package skeletons with pyproject.toml files. Root
pyproject.toml is not yet converted to a workspace — the old layout
continues to work. This commit is purely additive."
```

---

## Task 3: Migrate Layer 1 into `packages/layer-1/`

**Why this task:** this is the big move. Everything that is Layer-1-specific goes under `packages/layer-1/`, imports get rewritten from `pipeline.*` → `layer_1.pipeline.*`, path resolution is anchored to the package (not CWD), and the root `pyproject.toml` flips to workspace mode. After this task, `uv run --package layer-1 layer-1-extract --limit 2` works end-to-end. `core/` is still empty; that happens in Task 4.

**Files:**
- Move: `pipeline/` → `packages/layer-1/src/layer_1/pipeline/` (using `git mv`)
- Move: `extract.py` → `packages/layer-1/src/layer_1/cli/extract.py`
- Move: `eval.py` → `packages/layer-1/src/layer_1/cli/eval.py`
- Move: `prompts/` → `packages/layer-1/prompts/`
- Move: `scripts/calibration/` → `packages/layer-1/scripts/calibration/`
- Move: `tasks/` → `packages/layer-1/tasks/`
- Modify: `packages/layer-1/src/layer_1/pipeline/models.py` — path resolution
- Modify: `packages/layer-1/src/layer_1/pipeline/loader.py`, `scoring.py`, `report.py`, `analysis.py`, `judge.py` — import rewrites
- Modify: `packages/layer-1/src/layer_1/cli/extract.py`, `eval.py` — import rewrites
- Modify: `pyproject.toml` (root) — convert to workspace
- Delete: root-level `inputs` symlink; recreate under `packages/layer-1/inputs`

- [ ] **Step 1: Move existing Layer 1 files with `git mv`**

Run each command from the repo root. Order matters because `scripts/calibration/` must survive while `scripts/conductor/` stays in place.

```bash
git mv pipeline   packages/layer-1/src/layer_1/pipeline
git mv extract.py packages/layer-1/src/layer_1/cli/extract.py
git mv eval.py    packages/layer-1/src/layer_1/cli/eval.py
git mv prompts    packages/layer-1/prompts
git mv tasks      packages/layer-1/tasks

mkdir -p packages/layer-1/scripts
git mv scripts/calibration packages/layer-1/scripts/calibration
```

Expected: `git status` shows each file as "renamed" (not deleted+added). Run `git log --follow packages/layer-1/src/layer_1/pipeline/llm.py` at the end of the task to verify history tracks back through `pipeline/llm.py`.

- [ ] **Step 2: Move repo-root `README.md` to layer-1**

The Layer-1 README becomes the package README; a new top-level README is added in Task 6.

```bash
git mv README.md packages/layer-1/README.md
```

- [ ] **Step 3: Rewrite `inputs` symlink**

```bash
rm inputs
ln -s /Users/gabrielduarte/Documents/GitHub/Volantis/experiments/layer-1/inputs packages/layer-1/inputs
```

(Absolute target matches the existing symlink target — verify with `readlink packages/layer-1/inputs` before proceeding. If the target is different in your workspace, use whatever the original `readlink inputs` showed before the `rm`.)

- [ ] **Step 4: Fix path resolution in `packages/layer-1/src/layer_1/pipeline/models.py`**

The current file uses CWD-relative paths (`Path("inputs")`, `Path("prompts/extractor.md")`). Once `layer-1-extract` is an installable entry point, CWD is wherever the user runs it from — so paths must resolve against the package itself.

Open `packages/layer-1/src/layer_1/pipeline/models.py` and replace the top block (lines 1–19 in the pre-move version) with:

```python
"""Dataclasses, constants, and paths shared across the Layer 1 pipeline."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# `packages/layer-1/src/layer_1/pipeline/models.py` → `packages/layer-1/`
PACKAGE_ROOT = Path(__file__).resolve().parents[3]

INPUTS_DIR = PACKAGE_ROOT / "inputs"
OUTPUTS_DIR = PACKAGE_ROOT / "outputs"

OBSERVATIONS_PATH = INPUTS_DIR / "observations-stfrancis-2026-04-17.json"

EXTRACTOR_PROMPT_PATH = PACKAGE_ROOT / "prompts" / "extractor.md"
AUDIT_PROMPT_PATH = PACKAGE_ROOT / "prompts" / "judge_reference_free.md"

EXTRACTIONS_PATH = OUTPUTS_DIR / "extractions.jsonl"
QUALITY_CHECKS_PATH = OUTPUTS_DIR / "quality-checks.jsonl"
ANALYSIS_DIR = OUTPUTS_DIR / "analysis"
ANALYSIS_DEFAULT_PATH = ANALYSIS_DIR / "eval-report.json"
AUDIT_CACHE_DIR = OUTPUTS_DIR / "judge-cache" / "reference-free"
```

Everything below line 20 (the `JUDGE_MODEL` constant and all dataclasses) is unchanged.

- [ ] **Step 5: Rewrite `pipeline.*` imports to `layer_1.pipeline.*`**

The files that import from `pipeline.*` are: `extract.py`, `eval.py`, `loader.py`, `scoring.py`, `report.py`, `analysis.py`, `judge.py`. At this stage we rewrite ALL of them (including imports like `pipeline.llm`, `pipeline.text`, `pipeline.schema` that will later move again to `core.*` in Task 4 — doing it in two passes keeps each task independently green).

Run this from the repo root:

```bash
# Rewrite all `from pipeline.X` and `import pipeline.X` references.
find packages/layer-1/src -name "*.py" -print0 \
  | xargs -0 sed -i '' 's/from pipeline\./from layer_1.pipeline./g; s/import pipeline\./import layer_1.pipeline./g'
```

Verify no stragglers:

```bash
grep -rn "from pipeline\." packages/layer-1/src packages/core/src 2>/dev/null
grep -rn "import pipeline\." packages/layer-1/src packages/core/src 2>/dev/null
```

Expected: no matches.

- [ ] **Step 6: Wire `main()` as an entry point**

`extract.py` and `eval.py` already have `def main()` and `if __name__ == "__main__": main()`. Nothing to change in the source. But confirm both files end with:

```python
if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Convert root `pyproject.toml` to workspace config**

Replace the entire contents of `pyproject.toml` (at the repo root) with:

```toml
[project]
name = "extraction-pipeline"
version = "0.1.0"
description = "Layered extraction pipeline for SEL teacher observations"
requires-python = ">=3.13"

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
core      = { workspace = true }
layer-1   = { workspace = true }
layer-1-5 = { workspace = true }

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

- [ ] **Step 8: Temporary shim — `core` must be importable even though empty**

Layer 1 still imports `from layer_1.pipeline.llm` etc. after Step 5 — nothing imports `core` yet, so Task 3 does not need `core` to export anything. But `core`'s `pyproject.toml` declares `openai`, `pydantic`, and `python-dotenv` as its dependencies (Task 2, Step 1). After the workspace flip, those deps will be installed into the shared venv, and `layer_1.pipeline.llm` / `layer_1.pipeline.schema` will import them directly — so they need to be resolvable.

No code action required here — just a sanity assertion. Confirm that `packages/core/pyproject.toml` (from Task 2) declares `openai`, `pydantic`, `python-dotenv`. If not, add them now.

- [ ] **Step 9: Resolve the workspace and install**

```bash
rm -rf .venv uv.lock
uv sync
```

Expected: `uv` builds `core`, `layer-1`, and `layer-1-5` as editable installs into a single `.venv/`; prints a summary including `layer-1-extract` and `layer-1-eval` scripts.

- [ ] **Step 10: Smoke test — the CLI runs**

```bash
uv run --package layer-1 layer-1-extract --limit 2 --force
```

Expected: exits 0; `packages/layer-1/outputs/extractions.jsonl` has 2 JSON lines.

- [ ] **Step 11: Smoke test — eval runs**

```bash
uv run --package layer-1 layer-1-eval --no-audit
```

Expected: exits 0; prints a programmatic metrics table; `packages/layer-1/outputs/analysis/eval-report.json` exists.

- [ ] **Step 12: Typecheck and lint**

```bash
uv run mypy packages/
uv run ruff check packages/
```

Expected: both exit 0. If mypy catches unresolved imports, fix them before committing.

- [ ] **Step 13: Commit**

```bash
git add -A
git commit -m "refactor(monorepo): move Layer 1 into packages/layer-1

- Move pipeline/, extract.py, eval.py, prompts/, scripts/calibration/,
  tasks/, README.md into packages/layer-1/ with git mv.
- Rewrite all 'pipeline.X' imports to 'layer_1.pipeline.X'.
- Anchor path resolution to the package root so CLI entry points work
  from any CWD.
- Convert root pyproject.toml to a UV workspace declaration.
- Recreate inputs/ symlink under packages/layer-1/.

Layer 1 now runs via 'uv run --package layer-1 layer-1-extract'.
core/ is declared but still empty; its extraction is Task 4."
```

---

## Task 4: Extract `core/` modules

**Why this task:** this is where the shared library actually gets content. `llm.py`, `text.py`, the output-schema half of `schema.py`, and a new `io.py` (jsonl helpers factored out of duplicate logic in `extract.py` and `loader.py`) move into `packages/core/src/core/`. After this task, Layer 1 imports `core.llm`, `core.text`, `core.schema.layer1`, and `core.io`; Layer 1.5 will be able to do the same.

**Files:**
- Move: `packages/layer-1/src/layer_1/pipeline/llm.py` → `packages/core/src/core/llm.py`
- Move: `packages/layer-1/src/layer_1/pipeline/text.py` → `packages/core/src/core/text.py`
- Split: `packages/layer-1/src/layer_1/pipeline/schema.py` → keep audit classes in place, move extraction classes to `packages/core/src/core/schema/layer1.py`
- Create: `packages/core/src/core/io.py`
- Modify: `packages/layer-1/src/layer_1/pipeline/{loader,scoring,judge}.py`, `packages/layer-1/src/layer_1/cli/extract.py` — swap imports to `core.*`
- Modify: `packages/layer-1/src/layer_1/cli/extract.py` — use `core.io.append_jsonl` and drop the local `_append_jsonl`

### Step-by-step

- [ ] **Step 1: Move `llm.py` to `core/`**

```bash
git mv packages/layer-1/src/layer_1/pipeline/llm.py packages/core/src/core/llm.py
```

No content changes; `llm.py` has no internal `pipeline.*` imports.

- [ ] **Step 2: Move `text.py` to `core/`**

```bash
git mv packages/layer-1/src/layer_1/pipeline/text.py packages/core/src/core/text.py
```

No content changes.

- [ ] **Step 3: Split `schema.py`**

The Layer 1 output schema (`Signal`, `ExtractionOutput`, `Participant`, and the Literal types they use) moves to `core.schema.layer1`. The audit schema (`AuditCheck`, `AuditChecks`, `AuditSignalEntry`, `AuditResponse`) stays in `layer_1.pipeline.schema`.

Create `packages/core/src/core/schema/layer1.py`:

```python
"""Layer 1 output schema — the contract between Layer 1 and downstream layers.

Lives in `core` because Layer 1.5 (and any future consumer) reads Layer 1's
output and must be able to parse it without importing from layer_1.*.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SignalType = Literal[
    "behavioral_evidence",
    "emotional_indicator",
    "context_marker",
    "concern_flag",
]

Confidence = Literal["high", "medium", "low"]

Valence = Literal["positive", "negative", "mixed", "neutral"]

Target = Literal[
    "self", "peer", "group", "adult", "task", "object", "environment"
]

Agency = Literal["self_initiated", "prompted", "scaffolded", "external"]

TemporalityCue = Literal["first_time", "recurring", "change", "one_time"]

DomainDescriptor = Literal[
    "body", "speech", "task", "peer", "adult", "feeling", "creation", "norm"
]

ParticipantRole = Literal[
    "actor", "recipient", "self", "group_member", "bystander"
]


class Participant(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    role: ParticipantRole | None = None


class Signal(BaseModel):
    model_config = ConfigDict(extra="allow")

    evidence: str
    type: SignalType
    confidence: Confidence
    valence: Valence | None = None
    target: Target | None = None
    agency: Agency | None = None
    temporality_cue: TemporalityCue | None = None
    domain_descriptors: list[DomainDescriptor] = Field(default_factory=list)
    participants: list[Participant] = Field(default_factory=list)
    reasoning: str


class ExtractionOutput(BaseModel):
    """Shape of what the extractor LLM returns *before* post-processing."""

    model_config = ConfigDict(extra="allow")

    language: str
    source_type: Literal["teacher_observation"]
    named_students: list[str]
    signals: list[Signal]
```

Then replace the entirety of `packages/layer-1/src/layer_1/pipeline/schema.py` with the audit-only subset:

```python
"""Pydantic models for the Layer 1 audit LLM's response.

The extractor-side schema (`Signal`, `ExtractionOutput`, `Participant`) lives
in `core.schema.layer1` because it is the public contract between Layer 1 and
downstream consumers (Layer 1.5 reads Layer 1's output).

`extra="allow"` on the top-level models is intentional: if the prompt is
updated to emit an additional field before the schema catches up, we don't
want validation to hard-fail — the extra field just passes through.
"""

from pydantic import BaseModel, ConfigDict, Field


class AuditCheck(BaseModel):
    model_config = ConfigDict(extra="allow")

    passed: bool
    note: str = ""


class AuditChecks(BaseModel):
    model_config = ConfigDict(extra="allow")

    evidence_grounded: AuditCheck
    reasoning_justifies_classification: AuditCheck
    no_over_extraction: AuditCheck


class AuditSignalEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    signal_index: int
    evidence: str
    checks: AuditChecks


class AuditResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    per_signal: list[AuditSignalEntry] = Field(default_factory=list)
    summary: str = ""
```

- [ ] **Step 4: Create `packages/core/src/core/io.py`**

Generic jsonl helpers — `append_jsonl` (lock-safe, factored from `extract.py:_append_jsonl`) and `read_jsonl` (used by both layers in future). Both tolerate truncated trailing lines.

```python
"""Generic JSONL read/write helpers used across layers.

Layer 1 appends extractions to jsonl; Layer 1.5 will read them. Keeping the
primitives here avoids duplicating jsonl handling in each layer.
"""

import json
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any

_DEFAULT_LOCK = threading.Lock()


def append_jsonl(path: Path, record: dict[str, Any], lock: threading.Lock | None = None) -> None:
    """Append one JSON object as a single line, serialized under a lock so
    concurrent workers can't interleave bytes."""
    effective_lock = lock if lock is not None else _DEFAULT_LOCK
    line = json.dumps(record, ensure_ascii=False)
    with effective_lock, path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Yield each valid JSON object in a jsonl file.

    Tolerates a truncated trailing line from a prior crash (skips it).
    Non-dict records are skipped silently.
    """
    if not path.exists():
        return
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec, dict):
                yield rec
```

- [ ] **Step 5: Rewrite Layer 1 imports to pull from `core.*`**

Run from repo root:

```bash
find packages/layer-1/src -name "*.py" -print0 | xargs -0 sed -i '' \
  -e 's|from layer_1\.pipeline\.llm|from core.llm|g' \
  -e 's|from layer_1\.pipeline\.text|from core.text|g'
```

For the schema split, `loader.py` currently imports `Signal` from `layer_1.pipeline.models` (the dataclass, not the Pydantic one) — that import should NOT change. The Pydantic `Signal`/`ExtractionOutput` is used only in `extract.py`:

Open `packages/layer-1/src/layer_1/cli/extract.py` and change:

```python
from layer_1.pipeline.schema import ExtractionOutput
```

to:

```python
from core.schema.layer1 import ExtractionOutput
```

- [ ] **Step 6: Use `core.io.append_jsonl` in `extract.py`**

Open `packages/layer-1/src/layer_1/cli/extract.py` and:

1. Add import near the other `core` imports:
   ```python
   from core.io import append_jsonl
   ```
2. Delete the module-level `_WRITE_LOCK` declaration (`_WRITE_LOCK = threading.Lock()`) and the `_append_jsonl` function body — they are no longer needed.
3. Replace the single call site `_append_jsonl(output_path, output)` with `append_jsonl(output_path, output)`.
4. Remove the unused `import threading` (run `ruff check` to confirm).

- [ ] **Step 7: Verify no stale imports remain**

```bash
grep -rn "from layer_1.pipeline.llm"  packages 2>/dev/null
grep -rn "from layer_1.pipeline.text" packages 2>/dev/null
grep -rn "from pipeline\." packages 2>/dev/null
```

Expected: no matches for any of the three.

- [ ] **Step 8: Resync and run**

```bash
uv sync
uv run --package layer-1 layer-1-extract --limit 2 --force
uv run --package layer-1 layer-1-eval --no-audit
```

Expected: both exit 0; `packages/layer-1/outputs/extractions.jsonl` produced.

- [ ] **Step 9: Typecheck and lint**

```bash
uv run mypy packages/
uv run ruff check packages/
```

Expected: both exit 0.

- [ ] **Step 10: Verify git history survived the move**

```bash
git log --follow packages/core/src/core/llm.py
git log --follow packages/core/src/core/text.py
```

Expected: commit history goes back through `pipeline/llm.py` and `pipeline/text.py`. If `--follow` returns empty, stop and investigate — the move was done as delete+add instead of a rename.

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "refactor(monorepo): extract core/ shared library

- Move pipeline/llm.py and pipeline/text.py into packages/core/.
- Split pipeline/schema.py: extraction schema (Signal, ExtractionOutput,
  Participant + Literal types) moves to core.schema.layer1 as the
  inter-layer contract; audit schema stays in layer_1.pipeline.schema.
- Add core.io with append_jsonl / read_jsonl; collapse the duplicated
  jsonl append logic in extract.py.
- Rewrite Layer 1 imports to pull from core.* where applicable."
```

---

## Task 5: Update Conductor setup + `.gitignore`

**Why this task:** new Conductor workspaces run `setup.sh` on creation. That script currently symlinks `inputs/` at the repo root and copies `.env` — both behaviors need to target the new layout. `.gitignore` also needs a `packages/*/outputs/` pattern so every layer's outputs are ignored.

**Files:**
- Modify: `scripts/conductor/setup.sh`
- Modify: `.gitignore`

- [ ] **Step 1: Update the `inputs/` symlink target in `setup.sh`**

Open `scripts/conductor/setup.sh`. Replace the block that creates the symlink (currently lines 58–69) with one that targets `packages/layer-1/inputs` and sources from either the main repo root's `packages/layer-1/inputs` or from the legacy `inputs/` location (supporting both during transition):

```bash
# Symlink packages/layer-1/inputs if missing (avoid duplicating large data files)
INPUTS_DST="$PWD/packages/layer-1/inputs"
INPUTS_PARENT="$(dirname "$INPUTS_DST")"
if [ ! -e "$INPUTS_DST" ]; then
    mkdir -p "$INPUTS_PARENT"
    if [ -n "$MAIN_REPO_ROOT" ] && [ -d "$MAIN_REPO_ROOT/packages/layer-1/inputs" ]; then
        ln -s "$MAIN_REPO_ROOT/packages/layer-1/inputs" "$INPUTS_DST"
        echo "    Symlinked packages/layer-1/inputs from main repo root ($MAIN_REPO_ROOT)"
    elif [ -n "$MAIN_REPO_ROOT" ] && [ -d "$MAIN_REPO_ROOT/inputs" ]; then
        ln -s "$MAIN_REPO_ROOT/inputs" "$INPUTS_DST"
        echo "    Symlinked packages/layer-1/inputs from legacy main repo inputs/"
    elif [ -d "$CONDUCTOR_ROOT_PATH/packages/layer-1/inputs" ]; then
        ln -s "$CONDUCTOR_ROOT_PATH/packages/layer-1/inputs" "$INPUTS_DST"
        echo "    Symlinked packages/layer-1/inputs from CONDUCTOR_ROOT_PATH"
    elif [ -d "$CONDUCTOR_ROOT_PATH/inputs" ]; then
        ln -s "$CONDUCTOR_ROOT_PATH/inputs" "$INPUTS_DST"
        echo "    Symlinked packages/layer-1/inputs from legacy CONDUCTOR_ROOT_PATH inputs/"
    else
        echo "    Warning: inputs not found — add observation JSON files to packages/layer-1/inputs manually"
    fi
fi
```

- [ ] **Step 2: Update `PROJECT_NAME` in `setup.sh`**

At line 8, change:

```bash
PROJECT_NAME="quality-observations"
```

to:

```bash
# data-harness rule set name. Keeping "quality-observations" until data-harness
# ships a rule set keyed on the new repo name "extraction-pipeline".
PROJECT_NAME="quality-observations"
```

(No behavioral change — just a comment explaining why the old name persists. If `$DATA_HARNESS_PATH/rules/projects/extraction-pipeline.md` exists, change the value to `"extraction-pipeline"` instead and drop the comment.)

- [ ] **Step 3: Update `.gitignore`**

Append these patterns (if not already present):

```
# Per-package outputs
packages/*/outputs/
packages/*/.venv/
```

- [ ] **Step 4: Verify the setup script still runs syntactically**

```bash
bash -n scripts/conductor/setup.sh
```

Expected: no output, exit 0.

- [ ] **Step 5: Commit**

```bash
git add scripts/conductor/setup.sh .gitignore
git commit -m "chore(conductor): point setup.sh at packages/layer-1/inputs

Symlink target moves under packages/layer-1/ to match the new monorepo
layout. The script keeps a fallback for the legacy inputs/ location so
workspaces created from older main repo clones still bootstrap cleanly.
.gitignore gains packages/*/outputs/ so every layer's outputs stay out
of git."
```

---

## Task 6: Top-level README, CLAUDE.md, framework doc

**Why this task:** with the structure in place, the repo needs a top-level entry point for humans (new contributors, future you) and for agents (CLAUDE.md). The existing `CLAUDE.md` is already at the repo root from before the migration — it just needs path updates. A new top-level `README.md` replaces the one that moved under `packages/layer-1/`. And the Analysis Framework doc gets committed so agents can find it at `docs/framework.md`.

**Files:**
- Create: `README.md` (new top-level)
- Modify: `CLAUDE.md` (paths)
- Create: `docs/framework.md`

- [ ] **Step 1: Write the top-level `README.md`**

```markdown
# Extraction Pipeline

Layered extraction pipeline for SEL teacher observations. Free-text classroom
notes in → structured, evidence-grounded signals out → student profiles and
wellness signals downstream.

## Layout

This is a UV-workspace monorepo. Each layer is a self-contained package.

```
packages/
├── core/        shared library (LLM client, text utilities, Layer 1 schema, jsonl helpers)
├── layer-1/     raw extraction — observation text → structured signals (evidence-anchored)
└── layer-1.5/   student-contextualized extraction (in progress)
```

Upcoming layers (Layer 2: profile accumulation; Layer 3: wellness/risk detection) will land as additional packages.

See [`docs/framework.md`](docs/framework.md) for the full architectural framework.

## Run

```
uv sync                                               # installs core + all layers + dev tools
uv run --package layer-1 layer-1-extract --limit 10   # extract (always use --limit until told otherwise)
uv run --package layer-1 layer-1-eval                 # programmatic checks + LLM audit
uv run --package layer-1 layer-1-eval --no-audit      # skip the audit for zero LLM cost
```

## Environment

```
OPENROUTER_API_KEY=...
```

Lives at the repo root `.env`; shared across all layers.

## Per-layer docs

- [`packages/layer-1/README.md`](packages/layer-1/README.md)
- [`packages/layer-1.5/README.md`](packages/layer-1.5/README.md)
```

- [ ] **Step 2: Update `CLAUDE.md` paths**

Open `CLAUDE.md`. In the "Run it" section, replace:

```
uv sync
uv run extract.py --limit 10              # extract (see --help for flags)
uv run eval.py                            # programmatic checks + LLM audit
uv run eval.py --no-audit                 # skip the audit for zero LLM cost
```

with:

```
uv sync
uv run --package layer-1 layer-1-extract --limit 10   # extract (always use --limit until told otherwise)
uv run --package layer-1 layer-1-eval                 # programmatic checks + LLM audit
uv run --package layer-1 layer-1-eval --no-audit      # skip the audit for zero LLM cost
```

In the "Calibration" section, replace:

```
uv run scripts/calibration/export.py                           # flagged rows → CSV
# fill `human_verdict` (flagged / not_flagged) and `human_note` by hand
uv run scripts/calibration/agreement.py outputs/analysis/calibration-{ts}.csv
```

with:

```
uv run python packages/layer-1/scripts/calibration/export.py                           # flagged rows → CSV
# fill `human_verdict` (flagged / not_flagged) and `human_note` by hand
uv run python packages/layer-1/scripts/calibration/agreement.py packages/layer-1/outputs/analysis/calibration-{ts}.csv
```

At the top of CLAUDE.md (right after the first heading), add a short pointer:

```
The full architectural framework — what each layer does, how they compose,
non-goals — lives in [`docs/framework.md`](docs/framework.md). Read it before
touching Layer 1.5 or anything that crosses layer boundaries.
```

- [ ] **Step 3: Write `docs/framework.md`**

Copy the Analysis Framework doc (the content shared at the start of brainstorming; also available at `.context/attachments/pasted_text_2026-04-20_12-41-34.txt`) verbatim into `docs/framework.md`:

```bash
cp .context/attachments/pasted_text_2026-04-20_12-41-34.txt docs/framework.md
```

If the path `.context/attachments/pasted_text_2026-04-20_12-41-34.txt` does not exist in a fresh execution environment, fall back to pasting the framework content from the spec at `docs/superpowers/specs/2026-04-20-monorepo-restructure-design.md` (the "## Reference spec" section points at it).

- [ ] **Step 4: Verify the layer-1 README is the old README**

```bash
head -5 packages/layer-1/README.md
```

Expected: matches the old top-level README's first heading ("# Layer 1: Raw Extraction Pipeline" or similar). If it is wrong, that means Task 3 Step 2 did not run as expected — investigate before committing.

- [ ] **Step 5: Commit**

```bash
git add README.md CLAUDE.md docs/framework.md
git commit -m "docs: add top-level README, framework doc, updated CLAUDE.md

Top-level README orients readers to the monorepo layout and points to the
per-layer READMEs. docs/framework.md captures the full layered pipeline
design (Layer 1 through Layer 3 + quality scoring). CLAUDE.md paths and
run commands updated for the new package-scoped CLIs."
```

---

## Task 7: Final verification

**Why this task:** run through every success criterion from the spec in order, and compare the current `extractions.jsonl` output byte-for-byte with the baseline captured in Task 1. Any drift means the restructure changed behavior and must be investigated.

**Files:** none modified.

- [ ] **Step 1: Clean outputs and re-run end-to-end**

```bash
rm -rf packages/layer-1/outputs
uv sync
uv run --package layer-1 layer-1-extract --limit 2 --force
uv run --package layer-1 layer-1-eval --no-audit
```

Expected: both exit 0.

- [ ] **Step 2: Structural validation of the extraction output**

LLM outputs are not deterministic, so a byte-diff against the Task 1 baseline would fail spuriously. Instead, validate the structural shape: two records, each with the expected top-level fields, each parseable by the Pydantic schema.

```bash
uv run python -c "
import json
from pathlib import Path
from core.schema.layer1 import ExtractionOutput

path = Path('packages/layer-1/outputs/extractions.jsonl')
lines = [l for l in path.read_text().splitlines() if l.strip()]
assert len(lines) == 2, f'expected 2 records, got {len(lines)}'

required_top = {'schema_version', 'source', 'language', 'source_type',
                'observation', 'student_count', 'observation_type',
                'signal_count', 'insight_density', 'meaningful_content',
                'named_students', 'named_students_count', 'signals'}

for i, line in enumerate(lines):
    rec = json.loads(line)
    missing = required_top - rec.keys()
    assert not missing, f'record {i} missing fields: {missing}'
    # Re-parse the extraction subset through the Pydantic contract.
    ExtractionOutput.model_validate({
        'language': rec['language'],
        'source_type': rec['source_type'],
        'named_students': rec['named_students'],
        'signals': rec['signals'],
    })

print('OK: 2 records, all fields present, schema valid')
"
```

Expected: prints `OK: 2 records, all fields present, schema valid` and exits 0. Any assertion failure means the restructure changed behavior — investigate before moving on.

- [ ] **Step 3: Full typecheck and lint**

```bash
uv run mypy packages/
uv run ruff check packages/
```

Expected: both exit 0.

- [ ] **Step 4: Verify git history on moved files**

Run `git log --follow` on one file from each moved group to confirm history survived:

```bash
git log --follow --oneline packages/core/src/core/llm.py                       | head -3
git log --follow --oneline packages/layer-1/src/layer_1/pipeline/judge.py      | head -3
git log --follow --oneline packages/layer-1/src/layer_1/cli/extract.py         | head -3
git log --follow --oneline packages/layer-1/prompts/extractor.md               | head -3
```

Expected: each shows at least one commit predating this plan (i.e., the file's history did not start with the move commit).

- [ ] **Step 5: Verify the Layer 1.5 skeleton installs and imports**

```bash
uv run python -c "import layer_1_5; print(layer_1_5.__file__)"
uv run python -c "from core.schema.layer1 import ExtractionOutput; print(ExtractionOutput.model_fields)"
```

Expected: both print something non-empty. This confirms Layer 1.5 is installable and `core` is importable — the two things future Layer 1.5 work depends on.

- [ ] **Step 6: Verify Conductor `setup.sh` is syntactically valid**

```bash
bash -n scripts/conductor/setup.sh
```

Expected: exits 0 with no output.

- [ ] **Step 7: Confirm `.gitignore` covers the new paths**

```bash
git check-ignore -v packages/layer-1/outputs/extractions.jsonl
```

Expected: prints the matching rule (`packages/*/outputs/`). If it does not, the `.gitignore` update in Task 5 needs to be revisited.

- [ ] **Step 8: Confirm no orphaned old paths remain**

```bash
ls pipeline extract.py eval.py prompts 2>/dev/null
```

Expected: all four return "No such file or directory". If any exist, a `git mv` in Task 3 was incomplete.

- [ ] **Step 9: Final commit (only if anything changed during verification)**

If steps 1–8 all passed without any file modifications, no commit needed. If any file was touched during verification (e.g., a residual typing issue mypy caught), commit:

```bash
git add -A
git commit -m "chore(monorepo): post-migration cleanup"
```

- [ ] **Step 10: Update memory: restructure is complete**

Record a brief project memory that the repo has been restructured, so future sessions don't re-ask what the layout is. (Pointer only; don't inline the whole layout — the top-level README has that.)

---

## Rollback notes

If any task fails verification and the fix is not obvious, `git reset --hard HEAD` back to the last good commit. Tasks 1–7 are each a single commit, so you can drop the most recent and retry.

The one irreversible action is the GitHub repo rename (the manual step outside the agent's scope). GitHub auto-redirects the old URL for years; rollback is a second UI action.
