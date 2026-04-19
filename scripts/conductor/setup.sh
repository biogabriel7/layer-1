#!/usr/bin/env bash
#
# Conductor setup script — syncs team conventions on workspace creation.
# Requires DATA_HARNESS_PATH env var (add to ~/.zshrc).
#
set -euo pipefail

PROJECT_NAME="quality-observations"

if [ -z "${DATA_HARNESS_PATH:-}" ]; then
    echo "Error: DATA_HARNESS_PATH is not set."
    echo "Set it to your local data-harness clone, e.g.:"
    echo "  export DATA_HARNESS_PATH=\"\$HOME/path/to/data-harness\""
    exit 1
fi

if [ ! -d "$DATA_HARNESS_PATH" ]; then
    echo "Error: DATA_HARNESS_PATH does not exist: $DATA_HARNESS_PATH"
    exit 1
fi

echo "==> Checking environment..."
# Resolve the main repo root via git (works in worktrees)
MAIN_REPO_ROOT=""
if command -v git &>/dev/null; then
    GIT_COMMON_DIR="$(git rev-parse --git-common-dir 2>/dev/null || true)"
    if [ -n "$GIT_COMMON_DIR" ]; then
        MAIN_REPO_ROOT="$(cd "$GIT_COMMON_DIR/.." && pwd)"
    fi
fi

# Copy .env if missing
if [ ! -f "$PWD/.env" ]; then
    if [ -n "$MAIN_REPO_ROOT" ] && [ -f "$MAIN_REPO_ROOT/.env" ]; then
        cp "$MAIN_REPO_ROOT/.env" "$PWD/.env"
        echo "    Copied .env from main repo root ($MAIN_REPO_ROOT)"
    elif [ -f "$CONDUCTOR_ROOT_PATH/.env" ]; then
        cp "$CONDUCTOR_ROOT_PATH/.env" "$PWD/.env"
        echo "    Copied .env from CONDUCTOR_ROOT_PATH"
    else
        echo "    Warning: .env not found — create with OPENROUTER_API_KEY"
    fi
fi

# Copy .env.local if missing
if [ ! -f "$PWD/.env.local" ]; then
    if [ -n "$MAIN_REPO_ROOT" ] && [ -f "$MAIN_REPO_ROOT/.env.local" ]; then
        cp "$MAIN_REPO_ROOT/.env.local" "$PWD/.env.local"
        echo "    Copied .env.local from main repo root ($MAIN_REPO_ROOT)"
    elif [ -f "$CONDUCTOR_ROOT_PATH/.env.local" ]; then
        cp "$CONDUCTOR_ROOT_PATH/.env.local" "$PWD/.env.local"
        echo "    Copied .env.local from CONDUCTOR_ROOT_PATH"
    else
        echo "    Warning: .env.local not found — copy from template or create with secrets"
    fi
fi

# Symlink inputs/ if missing (avoid duplicating large data files)
if [ ! -d "$PWD/inputs" ]; then
    if [ -n "$MAIN_REPO_ROOT" ] && [ -d "$MAIN_REPO_ROOT/inputs" ]; then
        ln -s "$MAIN_REPO_ROOT/inputs" "$PWD/inputs"
        echo "    Symlinked inputs/ from main repo root ($MAIN_REPO_ROOT)"
    elif [ -d "$CONDUCTOR_ROOT_PATH/inputs" ]; then
        ln -s "$CONDUCTOR_ROOT_PATH/inputs" "$PWD/inputs"
        echo "    Symlinked inputs/ from CONDUCTOR_ROOT_PATH"
    else
        echo "    Warning: inputs/ not found — add observation JSON files manually"
    fi
fi

if [ -f "$PWD/pyproject.toml" ]; then
    echo "==> Installing dependencies with uv..."
    uv sync
fi

echo "==> Syncing harness rules..."
if [ -n "$PROJECT_NAME" ]; then
    "$DATA_HARNESS_PATH/scripts/sync.sh" "$PWD" "$PROJECT_NAME"
else
    "$DATA_HARNESS_PATH/scripts/sync.sh" "$PWD"
fi
echo "==> Setup complete."
