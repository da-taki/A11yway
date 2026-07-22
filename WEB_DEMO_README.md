# Web Interface

The web interface is a small Flask app for running public-page audits and reading generated reports.

## Run

```bash
python -m a11yway.web_app
```

## What it exposes

- `/` renders the audit form.
- `/audit` accepts a permitted public URL and selected checks.
- `/audits/<run_id>` shows current run status.
- `/runs/<run_id>` shows a report summary.
- `/runs` lists recent local runs.
- `/health` returns service health and browser availability.

## Safety

The form requires confirmation that the target is public or permitted. URL validation blocks local hosts, private addresses, unsafe schemes, credentials in URLs, and unsafe redirects. Browser checks do not submit public forms.

## Render

Render uses `Dockerfile` and `render.yaml`. The container starts Gunicorn on `${PORT:-10000}` and uses `/health` as the health check.
