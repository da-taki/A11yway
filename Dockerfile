FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

WORKDIR /app

COPY requirements-web.txt requirements-browser.txt requirements-ai.txt ./
RUN pip install --no-cache-dir -r requirements-web.txt

COPY . .

ENV HOST=0.0.0.0
ENV PORT=10000
EXPOSE 10000

CMD ["gunicorn", "a11yway.web_app:app", "--bind", "0.0.0.0:10000"]
