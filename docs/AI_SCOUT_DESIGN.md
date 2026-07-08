# AI Scout Design

This is a design document only. A11yway does not make AI calls yet, does not require API keys, and does not include an AI SDK.

## Purpose

Future AI scout mode may help reviewers identify likely workflows and accessibility risks on public-interest pages. The scout should make review planning faster, not replace deterministic checks or human judgment.

## Why AI Scout Is Optional

- Deterministic static, browser, and task execution audits work without AI.
- Some reviewers cannot use hosted AI services because of policy, privacy, cost, or connectivity.
- AI output can be wrong or incomplete.
- A11yway should remain useful as a small, inspectable accessibility review toolkit.

## Deterministic Verification Remains Central

AI scout suggestions are planning inputs. A report should not call a finding confirmed unless static checks, browser checks, task execution, or reviewer verification supports it.

Safe architecture:

```
Website/page
  -> static/browser/task checks
  -> AI proposes workflows/risks
  -> deterministic verification confirms or rejects
  -> report marks findings as confirmed/suggested
```

## Possible Providers

- Groq
- OpenAI-compatible APIs
- Local models later

## Environment Variables

Future optional configuration may use:

- `A11YWAY_AI_PROVIDER`
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `A11YWAY_AI_SCOUT_ENABLED`
- `A11YWAY_AI_SCOUT_MODE`

`A11YWAY_AI_SCOUT_MODE=suggest_only` should be the safest default. A local `.env` file should never be committed.

## Proposed Scout Agents

- Keyboard-only agent
- Low-vision agent
- Dyslexia/cognitive-load agent
- Hearing-impaired agent
- Motor-impaired agent
- AI product accessibility agent

## Safety Boundaries

- No vulnerability testing
- No private data
- No authenticated testing without permission
- No mass crawling
- No public shaming
- No claims without deterministic evidence

## Output Distinction

Reports should distinguish:

- Suggested risk: a workflow pack or future AI scout says a risk is worth checking
- Deterministic finding: static, browser, or task execution evidence supports the issue
- Reviewer-confirmed finding: a human reviewer has verified the issue or impact

This distinction keeps the tool practical and honest. AI can help decide where to look; deterministic verification and human review decide what is confirmed.
