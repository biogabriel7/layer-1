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
uv sync --all-packages                                # installs core + all layers + dev tools
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
