# Precision Regression: Cornell And Vision-Aid

Date: 2026-07-18

This note records the precision benchmark run used to tune A11yway's
false-positive handling. Live generated artifacts are stored under ignored
report folders and are not committed.

## Cornell Benchmark

Pages:

- `https://www.cornell.edu/`
- `https://admissions.cornell.edu/`
- `https://admissions.cornell.edu/how-to-apply/first-year-international-applicants`
- `https://finaid.cornell.edu/`

Command:

```bash
python -m a11yway.main --batch reports/cornell_precision_regression/cornell_batch_config.json --out-dir reports/cornell_precision_regression --browser --axe --low-vision --html-reports --max-tabs 80 --wait-ms 1500 --verify-runs 3
```

Before the rule changes, the run reported 92 unique findings from 127 raw
occurrences: 45 high, 39 medium, and 8 low.

After the rule changes, the run reported 74 unique findings from 104 raw
occurrences: 32 high, 33 medium, and 9 low. Of those, 58 were native A11yway
findings and 16 were axe-prefixed findings. Compatibility confidence counts:
38 confirmed, 5 likely, 29 needs_review, and 2 informational. Reviewer-facing
confidence levels: 38 strong, 5 likely, 3 confirmed_by_multiple_engines,
13 needs_review, and 15 weak_heuristic. Fourteen clusters had more than one
raw occurrence; the largest had five occurrences.

The human-comparison fixture is
`examples/cornell_human_review_anonymized.json`. The batch comparison reported
3 true positives, 1 partial match, 70 unmatched A11yway findings, and 1 missed
human finding. This is a heuristic comparison against five grouped human
findings, not a fingerprinted verdict application.

## Cornell Issue Groups

| Group | Before | After | Treatment |
| --- | ---: | ---: | --- |
| Search input label | 2 `missing_form_label` | 2 `missing_form_label` | Retained. The admissions search input still relies on placeholder-only prompting and remains high/likely. The trained reviewer confirmed this group. |
| Positive tabindex | 11 high axe findings | 11 medium/needs_review axe findings | Downgraded. Positive values remain visible, but axe-only `tabindex` evidence is review-only unless A11yway proves harmful focus order. |
| Breadcrumb/menu label-in-name | 12 label-in-name findings | 3 label-in-name findings | Suppressed for functional menu controls such as `Up one menu level`. True visible-label replacement patterns still report. |
| Focus obscured | 11 focus-obscured findings | 3 focus-obscured findings | Reduced by the 80% coverage threshold. The remaining three reproduced in 3 of 3 runs, but still deserve human review because the external reviewer could not reproduce the older set. |
| Reflow and text spacing | 12 low-vision reflow/spacing findings | 10 low-vision reflow/spacing findings | Reduced and recalibrated. Small overflow is ignored; bare page-wide overflow is medium/review evidence, while clipped content and overlaps remain reportable. |

## Vision-Aid Benchmark

Pages:

- `https://visionaidindia.org/`
- `https://visionaidindia.org/what-we-do/`
- `https://visionaidindia.org/educate/`
- `https://visionaidindia.org/contact-us/`

Previous four-page subset: 112 raw review points and 112 unique findings.
Severity: 72 high, 39 medium, 1 low. The largest inflation categories were
missing image alt text (33), low-contrast samples (36), generic link text (11),
focus-indicator findings (10), and unnamed focus stops (8).

New command:

```bash
python -m a11yway.main --batch reports/visionaid_precision_regression/visionaid_batch_config.json --out-dir reports/visionaid_precision_regression --browser --axe --low-vision --html-reports --max-tabs 80 --wait-ms 1500 --verify-runs 3
```

New run: 145 unique findings from 158 raw occurrences: 76 high, 63 medium,
and 6 low. Because this regression included axe-core and the older subset did
not, 58 of the new findings are axe-prefixed. The native A11yway set is
87 findings. Compatibility confidence counts: 56 confirmed, 24 likely,
64 needs_review, and 1 informational. Reviewer-facing confidence levels:
56 strong, 20 likely, 5 confirmed_by_multiple_engines, 62 needs_review, and
2 weak_heuristic. Thirteen clusters had more than one raw occurrence; the
largest had two occurrences.

The native drop from 112 to 87 is mainly from image-alt/context handling and
rule confidence calibration. The full count rises only when axe's additional
landmark, ARIA, table-header, frame-title, and region rules are included.

## Rule Changes

- `axe_tabindex` is now review-only evidence: medium severity and
  needs_review confidence unless another check proves harmful focus behavior.
- `label_in_name_mismatch` ignores known functional menu action names such as
  `Up one menu level`, while preserving true visible-label replacement
  failures.
- Focus-obscured findings require at least 80% sampled coverage of the focused
  control; partial lower-coverage overlaps are ignored.
- Reflow findings use both a 24 px and 5% viewport tolerance for document-wide
  overflow. Bare overflow without clipping or overlap is medium and
  needs_review.
- Dynamic browser findings can be repeat-verified with `--verify-runs`.
  Three of three reproductions become strong/confirmed, two of three likely,
  and primary-run-only evidence becomes needs_review.
- Rule reliability profiles are computed from reviewer verdict history and
  can cap historically noisy rules at needs_review with
  `--calibrate-rules-from`.

## Remaining Limitations

- Live public sites vary between runs; repeat verification improves confidence
  but does not replace human testing.
- The Cornell human comparison uses grouped natural-language findings rather
  than exact A11yway fingerprints, so false-positive counts are conservative.
- Reflow and focus-obscured findings can still disagree with a human reviewer
  when sticky UI, animation timing, or viewport state differs.
- Generated report folders are local benchmark artifacts and should stay
  ignored.
