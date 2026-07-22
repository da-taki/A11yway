# AI Scout

AI Scout is optional and suggest-only.

It reads deterministic A11yway findings and can produce a short review summary or suggested observations. It must not create confirmed failures without deterministic evidence.

## Rules

- Keep deterministic findings separate from AI Scout text.
- Mark AI Scout output as review-only.
- Fail closed when the provider key or client is unavailable.
- Do not send private pages, credentials, or secrets.

The web app reports missing provider configuration as a failed or unavailable AI Scout status while the audit itself continues.
