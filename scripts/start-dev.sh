#!/usr/bin/env bash
# ============================================
# CampusConnect - Bash Dev Launcher
# ============================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

echo "================================================"
echo " CampusConnect — Starting Local Dev Environment "
echo "================================================"

# Start backend
echo "Starting Backend on http://localhost:8000..."
cd "$DIR/backend"
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting Frontend on http://localhost:5173..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

echo ""
echo "CampusConnect is running:"
echo "  Backend API:  http://localhost:8000"
echo "  Swagger Docs: http://localhost:8000/docs"
echo "  Frontend UI:  http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services."

wait
