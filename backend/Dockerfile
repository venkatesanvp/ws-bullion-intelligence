FROM python:3.13-slim
WORKDIR /app
RUN pip install --no-cache-dir uv==0.11.29
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY backend ./backend
ENV PYTHONPATH=/app/backend
EXPOSE 8000
CMD ["uv","run","--frozen","--no-dev","uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--no-access-log"]
