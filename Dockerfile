# Use a lightweight Python base
FROM python:3.12-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install dependencies first (better caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application
COPY . .

# Final stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/main.py /app/main.py

# Place the venv on the PATH so 'python' and 'uvicorn' work automatically
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port Render expects
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]