# Passive Security

`--passive-security` is separate and opt-in. It is never enabled by `--all-accessibility-modules`.

Allowed checks inspect only provided HTML, source URLs, and normal response metadata for HTTPS usage, mixed content, security-header evidence, insecure form actions, external scripts without integrity metadata, and sensitive-looking public HTML comments.

Passive security observations do not constitute a penetration test or a determination that a system is secure. A11yway does not inject payloads, fuzz, brute force, bypass access controls, enumerate accounts, exploit vulnerabilities, or download private data.
