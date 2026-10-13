#!/usr/bin/env bash
set -e
uvicorn app.main:app --port 8000 &
BACK=$!
trap 'kill $BACK' EXIT
if [ -f frontend/package.json ]; then
  (cd frontend && npm run dev)
else
  wait $BACK
fi
