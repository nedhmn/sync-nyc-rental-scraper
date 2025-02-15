FROM python:3.12-slim-bookworm

# No virtual environment (https://github.com/astral-sh/uv/pull/6834)
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

# No cache (https://github.com/astral-sh/uv/pull/1383)
ENV UV_NO_CACHE=true 

# Pip install uv
RUN pip install uv==0.5.14

WORKDIR /app

# Sync dependencies
COPY .env uv.lock pyproject.toml ./
RUN uv sync --frozen --no-dev

# Copy app
RUN mkdir data
COPY scripts ./scripts
COPY nycrental ./nycrental
