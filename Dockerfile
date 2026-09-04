FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

# Copy dependencies definitions
COPY pyproject.toml README.md ./

# Install python packages into system environment
RUN uv pip install --system -e .

# Copy source code and migrations
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini* ./

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
