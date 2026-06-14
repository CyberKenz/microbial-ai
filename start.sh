#!/usr/bin/env bash
# =============================================================================
# start.sh - Launch the Microbial AI Segmentation API and Svelte frontend.
#
# Usage:
#   chmod +x start.sh
#   ./start.sh
#
# The API server starts on http://localhost:8000 (with Swagger UI at /docs).
# The Svelte dev server starts on http://localhost:5173.
#
# NOTE: Since the project lives on a VFAT partition (no symlink support),
# the frontend runs from ~/microbial_ai_fe on the native Linux partition.
# Source files are synced automatically on each start.
#
# Press Ctrl+C to stop both servers.
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$HOME/venvs/ai_plate_reader"
FE_DIR="$HOME/microbial_ai_fe"

# ---------------------------------------------------------------------------
# Check venv exists
# ---------------------------------------------------------------------------
if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "[ERROR] Virtual environment not found at $VENV_DIR"
  echo "Create it with: python3 -m venv $VENV_DIR && $VENV_DIR/bin/pip install -r requirements.txt"
  exit 1
fi

# ---------------------------------------------------------------------------
# Sync and setup frontend on native Linux partition
# ---------------------------------------------------------------------------
echo "[INFO] Syncing frontend source to $FE_DIR ..."
mkdir -p "$FE_DIR/src/lib"

# Copy source files from VFAT project to home partition
cp "$SCRIPT_DIR/frontend/src/App.svelte"          "$FE_DIR/src/App.svelte"
cp "$SCRIPT_DIR/frontend/src/app.css"              "$FE_DIR/src/app.css"
cp "$SCRIPT_DIR/frontend/src/main.js"              "$FE_DIR/src/main.js"
cp "$SCRIPT_DIR/frontend/src/lib/api.js"           "$FE_DIR/src/lib/api.js"
cp "$SCRIPT_DIR/frontend/src/lib/ImageUploader.svelte"    "$FE_DIR/src/lib/ImageUploader.svelte"
cp "$SCRIPT_DIR/frontend/src/lib/CameraCapture.svelte"    "$FE_DIR/src/lib/CameraCapture.svelte"
cp "$SCRIPT_DIR/frontend/src/lib/CfuSettings.svelte"      "$FE_DIR/src/lib/CfuSettings.svelte"
cp "$SCRIPT_DIR/frontend/src/lib/ColonyCharts.svelte"     "$FE_DIR/src/lib/ColonyCharts.svelte"
cp "$SCRIPT_DIR/frontend/src/lib/ResultsView.svelte"      "$FE_DIR/src/lib/ResultsView.svelte"

# Copy config files
cp "$SCRIPT_DIR/frontend/vite.config.js"           "$FE_DIR/vite.config.js" 2>/dev/null || true
cp "$SCRIPT_DIR/frontend/svelte.config.js"         "$FE_DIR/svelte.config.js" 2>/dev/null || true
cp "$SCRIPT_DIR/frontend/index.html"               "$FE_DIR/index.html" 2>/dev/null || true
cp "$SCRIPT_DIR/frontend/package.json"             "$FE_DIR/package.json"

# Install dependencies if needed
if [ ! -d "$FE_DIR/node_modules" ]; then
  echo "[INFO] Installing frontend dependencies..."
  cd "$FE_DIR"
  npm install
fi

# ---------------------------------------------------------------------------
# Trap Ctrl+C to kill both processes
# ---------------------------------------------------------------------------
API_PID=""
FE_PID=""

cleanup() {
  echo ""
  echo "[INFO] Shutting down..."
  [ -n "$API_PID" ] && kill "$API_PID" 2>/dev/null
  [ -n "$FE_PID" ]  && kill "$FE_PID"  2>/dev/null
  wait 2>/dev/null
  echo "[INFO] Done."
  exit 0
}

trap cleanup SIGINT SIGTERM

# ---------------------------------------------------------------------------
# Start FastAPI backend
# ---------------------------------------------------------------------------
echo "[INFO] Starting FastAPI server on http://localhost:8000 ..."
echo "[INFO] Swagger docs available at http://localhost:8000/docs"

cd "$SCRIPT_DIR"
"$VENV_DIR/bin/python" -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload &
API_PID=$!

# ---------------------------------------------------------------------------
# Wait for API to be ready
# ---------------------------------------------------------------------------
echo "[INFO] Waiting for API to load model..."
sleep 5

# ---------------------------------------------------------------------------
# Start Svelte frontend
# ---------------------------------------------------------------------------
echo "[INFO] Starting Svelte dev server on http://localhost:5173 ..."

cd "$FE_DIR"
npx --yes vite --host 0.0.0.0 --port 5173 &
FE_PID=$!

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================"
echo "  Microbial AI App is running!"
echo "============================================"
echo ""
echo "  Frontend (UI):  http://localhost:5173"
echo "  API Server:     http://localhost:8000"
echo "  API Docs:       http://localhost:8000/docs"
echo "  API Health:     http://localhost:8000/api/health"
echo ""
echo "  Press Ctrl+C to stop both servers."
echo "============================================"
echo ""

# Wait for both background processes
wait
