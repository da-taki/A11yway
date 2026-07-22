# Production Readiness

A11yway is a beta accessibility evidence tool. It is suitable for public-page review runs where findings will be checked by a human.

## Ready

- Static audits run without optional browser adapters.
- Browser mode reports unavailable dependencies instead of crashing when possible.
- Render Docker smoke checks exercise Flask, Chromium, axe, report downloads, and AI Scout fallback.
- CI runs package, workflow, documentation, registry, and report tests.
- URL validation blocks private hosts, unsafe schemes, credentials, and unsafe redirects in the web interface.

## Limits

- A11yway does not certify WCAG conformance.
- Browser evidence is one Chromium run.
- Screen-reader evidence is Chromium accessibility-tree output unless a native adapter actually runs.
- Workflow mode needs explicit safe task definitions.
- Passive security checks are not penetration tests.

Use reports as evidence for review, not as final compliance decisions.
