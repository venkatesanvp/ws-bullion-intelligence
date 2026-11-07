FROM docker.io/library/python:3.13-slim@sha256:09a17cad02668ae61ece136b4fd36ac3849e14f670ebedb637ea3e15580525bc
WORKDIR /app
# Runtime uses uv and the locked project venv; inherited global pip is unnecessary.
RUN python -m pip uninstall --yes pip
COPY --from=ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 /uv /uvx /usr/local/bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY backend ./backend
ENV PYTHONPATH=/app/backend
RUN useradd --uid 10001 --create-home app && chown -R app:app /app
USER app
EXPOSE 8000
CMD ["uv","run","--frozen","--no-dev","uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--no-access-log"]
