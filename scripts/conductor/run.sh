#!/usr/bin/env bash
#
# Conductor run script — launches the dev server or tests from the Run button.
#
# Uses $CONDUCTOR_PORT to avoid port conflicts between parallel workspaces.
# Customize the command below for your project's stack.
#

set -euo pipefail

PORT="${CONDUCTOR_PORT:-8000}"

echo "==> Starting dev server on port $PORT..."

# — Uncomment the line that matches your stack —

# Python (Django)
# uv run python manage.py runserver "0.0.0.0:$PORT"

# Python (FastAPI)
# uv run uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload

# Node.js (Next.js)
# PORT=$PORT npm run dev

# Elixir (Phoenix)
# PORT=$PORT mix phx.server

# Ruby (Rails)
# bin/rails server -p "$PORT"

echo "Error: No run command configured. Edit scripts/conductor-run.sh for your stack."
exit 1
