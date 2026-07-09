# A11yway Web Demo

This demo adds a simple local website for running A11yway against one public page at a time. It is for accessibility stress-testing, workflow accessibility testing, public-interest accessibility testing, web quality review, and deterministic accessibility review.

A11yway is not a security scanner. Do not use the web demo for hacking, vulnerability scanning, auth bypass, pentesting, scraping private data, login flows, payment flows, or destructive actions.

## Run Locally

From the repo root:

```powershell
cd C:\Users\Asus\Desktop\A11yway

& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pip install -r requirements-web.txt
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m playwright install chromium
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m a11yway.web_app
```

Open `http://127.0.0.1:5000`.

The web demo writes the current single-target batch config here:

```text
reports/web_demo_batch_config.json
```

Each run is stored in a unique subfolder under:

```text
reports/web_demo_runs
```

## Run From The Terminal

After creating a run in the web UI, the same config can be used from the CLI:

```powershell
cd C:\Users\Asus\Desktop\A11yway

& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m a11yway.main --batch reports/web_demo_batch_config.json --out-dir reports/web_demo_runs --browser --low-vision --html-reports --ai-scout --max-tabs 60 --wait-ms 1500
```

For static-only fallback, remove `--browser --low-vision`.

## Review Types

- Quick accessibility review: static deterministic checks.
- Full accessibility + low-vision review: browser focus traversal plus low-vision checks when Playwright is available.
- Keyboard/focus review: browser focus traversal when Playwright is available.
- AI-assisted report summary: static deterministic checks plus suggest-only AI Scout.
- Full public workflow review: browser, low-vision, and suggest-only AI Scout when available.

If browser mode is unavailable in a deployment, the app falls back and shows: `Browser evidence unavailable in this deployment.`

## Environment Variables

```env
GROQ_MODEL=llama-3.3-70b-versatile
A11YWAY_AI_SCOUT_ENABLED=true
A11YWAY_REQUIRE_PERMISSION_NOTICE=true
A11YWAY_AI_SCOUT_MODE=suggest_only
GROQ_API_KEY=your_key_here
A11YWAY_WEB_BROWSER_ENABLED=true
A11YWAY_WEB_SECRET=change_this_for_shared_deployments
```

Do not commit `.env`. The Groq API key is not shown in the UI, reports, or error output by the AI Scout helpers.

## Deploy On Render

The included `render.yaml` uses Docker because browser mode needs Playwright/Chromium system dependencies.

1. Push this repo to GitHub.
2. In Render, create a new Blueprint or Web Service from the repo.
3. Use the included `render.yaml` or choose Docker as the environment.
4. Add `GROQ_API_KEY` as a secret environment variable if AI Scout should run.
5. Confirm these environment variables:
   - `A11YWAY_AI_SCOUT_ENABLED=true`
   - `A11YWAY_REQUIRE_PERMISSION_NOTICE=true`
   - `A11YWAY_AI_SCOUT_MODE=suggest_only`
   - `GROQ_MODEL=llama-3.3-70b-versatile`
   - `A11YWAY_WEB_BROWSER_ENABLED=true`
6. Deploy.

The Docker service starts:

```bash
gunicorn a11yway.web_app:app --bind 0.0.0.0:10000
```

If the deployment plan cannot run browser mode reliably, set:

```env
A11YWAY_WEB_BROWSER_ENABLED=false
```

The demo will still run static checks and clearly mark browser evidence as unavailable.

## Safety Guardrails

The web demo validates URLs before running A11yway. It blocks:

- localhost, `127.0.0.1`, `0.0.0.0`, private IP ranges, link-local ranges, reserved IPs, and metadata IPs such as `169.254.169.254`
- file, FTP, JavaScript, data, and other non-http(s) schemes
- URLs with embedded credentials
- obvious internal/private hostnames and short intranet-style hostnames
- hostnames that resolve to private, local, metadata, or reserved addresses

The demo only runs one URL per review. It does not log in, submit forms, create accounts, send emails, create support tickets, test payments, bypass authentication, scrape private data, or run vulnerability scans.

## Scoring

The score is an issue-volume and severity indicator for normal readers. It is not a WCAG conformance score.

Weights:

- critical: 20
- high: 10
- medium: 4
- low: 1

Classifications:

- `Looks mostly clear`
- `Minor review points`
- `Needs review`
- `Serious review recommended`
- `Workflow may be blocked`

The app also groups top risk areas such as keyboard/focus, low vision/contrast, reflow/zoom, accessible names/labels, headings/structure, alt text/media, forms/errors, generic links, AI-assisted observations, and basic page quality.

## Limitations

- A11yway does not claim a page is accessible, inaccessible, WCAG compliant, or illegal.
- Browser mode approximates keyboard interaction and does not simulate a full screen reader.
- AI Scout is suggest-only and may be unavailable without a Groq API key.
- Static checks cannot see all JavaScript-rendered state.
- The web demo stores run files locally and does not use a database.
- Render filesystems may be ephemeral, so past runs may not persist across redeploys unless storage is added.
