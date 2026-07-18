# Reviewer Guide

This guide explains how to read an A11yway report.

## What The Summary Means

The summary shows the tested source, total issues found, raw occurrences, unique root issues, checks run, and counts by severity, issue type, and confidence level.

Use the summary to understand the overall shape of the report, not as a final accessibility score.

## What Issue Severity Means

Severity is an early prototype estimate.

- High: likely to block or seriously affect a student task.
- Medium: likely to create confusion, extra effort, or partial access problems.
- Low: worth reviewing, but may not block the task by itself.

Severity should be reviewed by a human. If a severity rating feels too high or too low, please note that in feedback.

## How To Read Evidence Snippets

Each issue may include:

- The HTML tag involved.
- Attributes such as `id`, `name`, `href`, or `src`.
- A short HTML snippet.
- An approximate line number.
- A reason the element was flagged.
- Confidence and verification fields such as `confidence_level`, `verification_status`, and `human_review_reason`.
- Occurrence and clustering fields such as `occurrence_count`, `affected_page_count`, and `component_signature`.

Line numbers are approximate. They are meant to help locate the issue, not to be exact source-code references.

## What Task Blockers Mean

Task blockers explain how a static finding may affect a specific education workflow.

For example, an unlabeled form field may matter more in a task where a student must submit an application form.

Task blockers are deterministic explanations. They are not yet based on real browser interaction or student simulation.

## How To Mark False Positives

Mark a finding as a false positive if:

- The issue is not actually present.
- The page has a valid accessible alternative that A11yway missed.
- The finding does not affect the tested task.
- The evidence points to the wrong element.

Please include the issue number and a short explanation.

Reviewer verdict files can mark findings as:

- `confirmed`
- `false_positive`
- `partially_confirmed`
- `needs_review`
- `fixed`
- `missed_issue`
- `duplicate`
- `not_applicable`
- `unable_to_reproduce`

Verdicts may also include reviewer role, testing environment, browser, operating system, assistive technology, manual testing method, notes, related WCAG criteria, severity adjustment, and corrected evidence. These verdicts help measure report accuracy. They should not be used to publicly name reviewers or organizations unless permission was granted.

## How To Report Missed Issues

Report a missed issue if the page has an accessibility barrier that A11yway did not detect.

Useful details include:

- What the barrier is.
- Who it affects.
- Which task step it affects.
- How a student or reviewer noticed it.

## Current Limitations

A11yway currently has important limits:

- No full screen reader simulation.
- Document checks are evidence-only and do not certify PDF/UA or Office conformance.
- No crawling, no logins, and no private portal testing without permission.
- Low-vision checks are browser heuristics, not certification.
- No full WCAG certification.
- No replacement for disabled-user testing or expert review.
