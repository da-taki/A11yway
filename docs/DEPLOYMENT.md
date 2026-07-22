# Deployment

A11yway's Render deployment uses Docker.

## Files

- `Dockerfile` builds the Python 3.12 image, installs web and browser requirements, installs Chromium, copies the app, and starts Gunicorn.
- `render.yaml` defines the Render web service, `/health` check, browser mode, permission notice, and AI Scout environment names.
- `.github/workflows/ci.yml` builds the same image and runs the Render smoke script.

## Verified commands

```bash
docker build -t a11yway-render-smoke .
docker run --rm a11yway-render-smoke python scripts/render_docker_smoke.py
```

The smoke script checks Flask imports, Playwright, Chromium launch, `/health`, landing-form structure, browser reports, axe reports, report downloads, and AI Scout missing-key fallback.
