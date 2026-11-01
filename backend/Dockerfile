FROM docker.io/library/python:3.13-slim@sha256:2d44738ebf4ce5f63b9d9ea871e9c7cfdc0426f7b0c97cac915fd88ded1d86bb
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.11.29@sha256:eb2843a1e56fd9e30c7276ce1a52cba86e64c7b385f5e3279a0e08e02dd058fc /uv /uvx /usr/local/bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY backend ./backend
ENV PYTHONPATH=/app/backend
EXPOSE 8000
CMD ["uv","run","--frozen","--no-dev","uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--no-access-log"]
