#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "  RevBack — Production Deployment & Bootstrap Initializer  "
echo "=========================================================="

# 1. Check Python & UV
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv is not installed. Installing astral-sh/uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python 3.12 virtual environment..."
    uv venv .venv --python 3.12
fi

source .venv/bin/activate

# 3. Install Python Dependencies
echo "📦 Installing backend dependencies..."
uv pip install -e .
uv pip install celery redis slowapi resend PyJWT bcrypt email-validator prometheus-client langfuse

# 4. Check Environment Configuration
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
fi

# 5. Database Migrations
echo "🗄️ Running Alembic database migrations..."
if alembic upgrade head; then
    echo "✅ Database schema is up to date."
else
    echo "⚠️ Alembic upgrade encountered an issue or DB not yet online."
fi

# 6. Frontend Build Test
if [ -d "frontend" ]; then
    echo "🖥️ Building Next.js production bundle..."
    (cd frontend && npm install && npm run build)
    echo "✅ Next.js production build ready."
fi

echo "=========================================================="
echo "🎉 RevBack initialization complete!"
echo "To run the production stack:"
echo "  docker compose -f docker-compose.prod.yml up -d --build"
echo "Or start backend and worker locally:"
echo "  uvicorn src.main:app --port 8000"
echo "  celery -A src.workers.celery_app.celery_app worker --loglevel=info"
echo "=========================================================="
