# A11yway Batch Evaluation Summary

## Overview

- Batch config used: examples/sample_low_vision_batch.json
- Pages tested: 1
- Successful pages: 1
- Failed pages: 0
- Total issues: 7
- Total task blockers: 0
- HTML reports: 1
- Low-vision issues: 7

## Top Issue Types

- zoom_fixed_width_content: 3
- low_contrast_text: 2
- focus_indicator_missing: 1
- zoom_horizontal_overflow: 1

## Severity Breakdown

- High: 4
- Medium: 3
- Low: 0

## Sources With Most Issues

| Name | Source | Task | Issues | Blockers | Report | HTML report |
| --- | --- | --- | ---: | ---: | --- | --- |
| Low Vision Sample Page | examples/sample_low_vision_page.html |  | 7 | 0 | reports/low_vision_batch/low_vision_sample.md | reports/low_vision_batch/low_vision_sample.html |

## High Priority Findings

### Low Vision Sample Page

- low_contrast_text: Rendered text may have low contrast
- low_contrast_text: Rendered text may have low contrast
- zoom_horizontal_overflow: Page has horizontal overflow in a narrow viewport
- focus_indicator_missing: Focused element may not show a visible focus indicator
- Full report: reports/low_vision_batch/low_vision_sample.md

## Recommended Review Process

1. Review high severity issues first.
2. Confirm evidence snippets against the actual page.
3. Mark false positives.
4. Note barriers the static checks missed.
5. Decide which fixes are feasible for the organization.

## Limitations

- This prototype only runs static HTML checks.
- It does not replace a full human accessibility audit.
- It does not yet perform browser-based interaction testing.
