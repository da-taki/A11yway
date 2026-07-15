# A11yway Public Web Audit Demo

A11yway includes a Flask website for running the existing deterministic audit engine against one safe public URL at a time. The web flow is designed for public competition demos and Render deployment:

1. Enter a public `http://` or `https://` URL.
2. Select an audit preset or individual A11yway modules.
3. Confirm the page is public or authorized for review.
4. Watch live progress while the server validates, fetches, audits, asks AI Scout when selected, and writes reports.
5. Review the results dashboard and download generated reports.

A11yway is not a security scanner and does not claim legal compliance certification. Reports require human review.

## Local Development

From the repository root:

```powershell
cd C:\Users\Asus\Desktop\A11yway

& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pip install -r requirements-web.txt
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m playwright install chromium
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m a11yway.web_app
```

Open `http://127.0.0.1:5000`.

The web app writes the current single-target batch config to:

```text
reports/web_demo_batch_config.json
```

Each run is isolated under:

```text
reports/web_demo_runs/<run-id>
```

Those generated run artifacts are ignored by Git.

## Audit Modules

The web UI exposes existing A11yway capabilities. Presets only select combinations of these modules; they do not create fake capabilities.

- Static HTML analysis
- Browser-rendered analysis
- Keyboard navigation
- Keyboard trap and focus-loop detection
- axe-core
- Chromium accessibility-tree evidence
- Low-vision and reflow checks
- Mobile emulation
- Forms
- Components
- Media
- Language and cognitive checks
- Indic-language checks
- Screenshots
- Focus-path overlays
- AI Scout

Document auditing and video proof remain CLI-oriented for this one-page public URL flow and are shown as unavailable when applicable.

Passive security observations are opt-in, visually separate, and stored separately. They are not included in the accessibility score.

## AI Scout

AI Scout runs server-side only. The Groq key is read from environment variables or local `.env`; it is never placed in HTML, JavaScript, generated reports, or user-facing errors.

Required AI Scout behavior:

```env
A11YWAY_AI_SCOUT_MODE=suggest_only
A11YWAY_REQUIRE_PERMISSION_NOTICE=true
```

If `GROQ_API_KEY` is missing or the provider is unavailable, deterministic auditing still completes and the results page marks AI Scout as unavailable or failed.

## Required Environment Variables

For a shared deployment:

```env
A11YWAY_WEB_SECRET=change_this_for_shared_deployments
A11YWAY_REQUIRE_PERMISSION_NOTICE=true
A11YWAY_AI_SCOUT_MODE=suggest_only
```

For AI Scout:

```env
A11YWAY_AI_SCOUT_ENABLED=true
GROQ_API_KEY=your_render_secret
GROQ_MODEL=llama-3.3-70b-versatile
```

For browser evidence:

```env
A11YWAY_WEB_BROWSER_ENABLED=true
```

Set `A11YWAY_WEB_BROWSER_ENABLED=false` if the host cannot run Chromium reliably. Static, forms, language, media, components, and AI Scout fallback behavior still work.

## Render Deployment

The repository includes:

- `Dockerfile`
- `render.yaml`
- `Procfile`
- `requirements-web.txt`

The Docker setup uses the Playwright Python image so Chromium dependencies are available.

Render build command:

```bash
docker build .
```

Render start command:

```bash
gunicorn a11yway.web_app:app --bind 0.0.0.0:$PORT
```

The included Docker `CMD` uses the same app target and binds to Render's `$PORT`.

Health check:

```text
/health
```

Expected response:

```json
{"ok": true, "service": "a11yway-web", "browser_available": true}
```

## Safety Guardrails

The web app validates URLs before auditing and rejects:

- localhost and loopback addresses
- private, link-local, reserved, multicast, and metadata IPs
- internal-looking hostnames and short intranet names
- non-http(s) schemes
- embedded usernames or passwords
- unusually long URLs
- unsafe non-web ports
- unsafe redirect targets

The demo only reviews one public page per run. It does not log in, submit forms, create accounts, send messages, test payments, bypass authentication, scrape private data, run exploit checks, scan ports, or crawl private systems.

## Generated Reports

When successfully generated, the results dashboard links to:

- HTML
- Markdown
- JSON
- CSV
- SARIF
- JUnit XML
- AI Scout sidecars
- Passive security sidecar, when selected

Browser evidence can include screenshots and focus-path overlays.

## Verification

Useful local checks:

```powershell
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m a11yway.web_app
```

Production-style startup smoke:

```powershell
$env:PORT="5000"
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m gunicorn a11yway.web_app:app --bind 127.0.0.1:5000
```

Then verify:

```text
http://127.0.0.1:5000/health
```
