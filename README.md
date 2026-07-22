# A11yway

An open-source accessibility stress-testing toolkit for essential public web workflows.

A11yway audits rendered websites, follows keyboard workflows, checks zoom and reflow, inspects accessibility-tree output, and saves evidence for human review.

## Checks

- Keyboard navigation and focus
- Accessible names, roles, and states
- Zoom, reflow, and text spacing
- Forms, language, tables, and media
- WCAG 2.2 A and AA review points
- Repeated component and template issues

## Evidence

Reports can include selectors, screenshots, focus paths, accessibility-tree output, reproduction data, confidence labels, and suggested fixes.

A11yway separates stronger findings from observations that still need manual review. It does not certify WCAG conformance.

## Run

```bash
a11yway https://example.com --browser --axe --html report.html
```

Use only public pages or pages you have permission to review. Browser checks do not submit forms.

## Web interface

```bash
python -m a11yway.web_app
```

## Tests

```bash
pytest
```

## Vibe coding

Used AI for the UI.

## License

No license is declared in this repository.
