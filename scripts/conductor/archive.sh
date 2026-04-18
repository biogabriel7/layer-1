#!/usr/bin/env bash
#
# Conductor archive script — runs when a workspace is archived.
# Use this for cleanup tasks (stop services, remove temp files, etc.).
#

set -euo pipefail

echo "==> Archiving workspace..."

# — Add cleanup tasks below —

# Kill any background processes started by the run script
# kill $(cat .server.pid 2>/dev/null) 2>/dev/null || true

# Remove temporary build artifacts
# rm -rf .next/ __pycache__/ node_modules/.cache/

echo "==> Archive complete."
