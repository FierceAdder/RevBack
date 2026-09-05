#!/usr/bin/env bash
set -e

# RevBack Unified Development Launcher
# Starts both FastAPI backend and Next.js frontend with unified graceful shutdown

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================================="
echo "  🚀 Starting RevBack Development Environment...          "
echo "=========================================================="

# 1. Activate Python virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "⚠️ .venv not found. Running scripts/setup.sh first..."
    bash scripts/setup.sh
    source .venv/bin/activate
fi

# 2. Check and clean up orphaned backend/frontend on port 8000
BACKEND_PID=$(lsof -ti:8000 || true)
if [ -n "$BACKEND_PID" ]; then
    echo "ℹ️  Port 8000 is already in use by PID $BACKEND_PID. Reusing or stopping..."
fi

# Function to clean up child processes on Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Shutting down RevBack services..."
    if [ -n "$FASTAPI_PID" ] && kill -0 "$FASTAPI_PID" 2>/dev/null; then
        kill "$FASTAPI_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    wait 2>/dev/null || true
    echo "✅ All services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 3. Start FastAPI Backend in background
echo "📦 [1/2] Starting FastAPI Backend on http://localhost:8000..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
FASTAPI_PID=$!

# Wait briefly for FastAPI to initialize
sleep 2

# 4. Start Next.js Frontend
echo "🖥️  [2/2] Starting Next.js Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "=========================================================="
echo "  ✨ RevBack is running!"
echo "  - Web Dashboard:    http://localhost:3000 (or 3001)"
echo "  - REST API & Docs:  http://localhost:8000/docs"
echo "  - Health Check:     http://localhost:8000/health"
echo "  - Metrics:          http://localhost:8000/metrics"
echo "  Press Ctrl+C to stop all services."
echo "=========================================================="

# Wait for both processes
wait $FASTAPI_PID $FRONTEND_PID
