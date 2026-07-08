# A11yway Evaluation Protocol

## Goal

Evaluate whether A11yway reports are accurate, useful, clear, and relevant for education organizations reviewing websites, forms, and learning resources.

The goal is to improve the prototype through feedback. The goal is not to claim that A11yway replaces a full accessibility audit.

## What Is Being Evaluated

- Static HTML accessibility findings.
- Task-based explanations for education workflows.
- JSON and Markdown report usefulness.
- Evidence quality, including snippets and approximate locations.
- Suggested fixes and severity levels.

## What Is Not Being Claimed

A11yway is not currently claiming:

- Full WCAG certification.
- Full screen reader simulation.
- JavaScript-rendered page coverage.
- Complete browser-based interaction testing.
- Replacement of disabled-user testing or expert review.

## Participant Types

- NGO technology teams.
- School administrators.
- Accessibility reviewers.
- Teachers using digital forms or resources.
- Education program staff who maintain public pages.

## Process

1. Select a public page, form, or learning resource, or get permission to test a specific page.
2. Run the A11yway static audit.
3. Generate a Markdown report.
4. Send the report and feedback form to the reviewer.
5. Collect ratings and comments.
6. Identify false positives, missed barriers, and unclear explanations.
7. Revise analyzer checks, report wording, and suggested fixes.
8. Repeat with a small set of different education workflows.

## Metrics

- Report usefulness: would the report help the team improve the page?
- Issue accuracy: are findings correct?
- False positives: which findings were not real barriers?
- Missed barriers: what important issues did A11yway fail to detect?
- Clarity: can reviewers understand the issue, evidence, and suggested fix?
- Task relevance: do likely blockers match the education workflow?
- Severity quality: do severity levels match practical impact?

## Ethical Notes

- Test public pages or pages where permission has been given.
- Do not use private student data.
- Do not perform security testing.
- Do not shame organizations publicly for findings.
- Disclose that A11yway is a prototype.
- Share reports as feedback material, not as final audit certification.
- Let organizations decide whether their names or feedback can be quoted.

## Output

Evaluation work should produce:

- Internal evaluation summary.
- Improved analyzer checks and fix suggestions.
- Improved report templates.
- Possible anonymized benchmark data.
- Notes on which barriers require human or browser-based testing.
