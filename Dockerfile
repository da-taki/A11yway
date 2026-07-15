FROM python:3.12-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=10000

COPY requirements-web.txt requirements-browser.txt requirements-ai.txt ./
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements-web.txt && \
    python -m playwright install --with-deps chromium

COPY . .

EXPOSE 10000

CMD ["sh", "-c", "gunicorn a11yway.web_app:app --bind 0.0.0.0:${PORT:-10000}"]
