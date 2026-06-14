#!/usr/bin/env bash
set -e

PORT="${PORT:-8000}"

echo "[INFO] Starting server on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
