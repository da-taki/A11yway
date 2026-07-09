# Email-Verified Outreach Batch

This folder contains a manual A11yway batch setup for public-interest accessibility stress-testing of targets that already have public email/contact routes identified.

No additional emails were searched for or verified while creating this batch.

## Included Targets

The batch includes 6 targets:

1. Level Access - confirmed public email: `info@levelaccess.com`
2. Fable - confirmed public email: `info@makeitfable.com`
3. AbilityNet - confirmed public email: `enquiries@abilitynet.org.uk`
4. Digital Accessibility Centre - confirmed public emails: `info@digitalaccessibilitycentre.org`, `team@daca11y.org`
5. Coursera - confirmed public emails: `press@coursera.org`, `privacy@coursera.org`; lower priority unless strong public-access findings are produced.
6. RNIB - included with `email_status: needs_manual_visual_confirmation`; visually confirm the official helpline email before outreach.

## Safety Rules

A11yway is being used for accessibility stress-testing, workflow accessibility testing, public-interest accessibility testing, and deterministic accessibility review.

Only test public pages. Do not log in, create accounts, submit forms, bypass auth, scrape private data, send messages through contact forms, create support tickets, submit newsletter forms, interact with payment flows, or run destructive actions. If a workflow reaches a form, stop before submission.

AI Scout must remain suggest-only. AI Scout output is not a confirmed finding and needs human review.

## How To Run

From PowerShell, run:

```powershell
cd C:\Users\Asus\Desktop\A11yway

& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m a11yway.main --batch reports/email_verified_batch_config.json --out-dir reports/email_verified_outreach --browser --low-vision --html-reports --ai-scout --max-tabs 60 --wait-ms 1500
```

Or run the helper file:

```powershell
powershell -ExecutionPolicy Bypass -File reports/run_email_verified_batch.ps1
```

## Output Folder

Reports will appear in:

```text
reports/email_verified_outreach
```

Expected outputs include:

- `index.md`
- `index.json`
- `index.csv`
- `evaluation_summary.md`
- per-target `.md`, `.json`, and `.html` reports
- per-target `_ai_scout.md` and `_ai_scout.json` files when AI Scout runs
- screenshot and focus-path files under the visual output folder when browser mode succeeds

## What To Send ChatGPT After The Run

Best option:

```text
reports/email_verified_outreach
```

Send the full zipped folder.

Minimum option:

- `index.md`
- `evaluation_summary.md`
- all per-target `.md` files
- all `_ai_scout.md` files
- screenshots and focus-path files for the strongest targets

ChatGPT can draft outreach emails only after the reports are generated and shared.
