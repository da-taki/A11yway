# A11yway Batch Accessibility Index

## Summary

- Total pages tested: 10
- Total issues: 196
- CSV index: reports/outreach_ai_scout/index.csv
- Evaluation summary: reports/outreach_ai_scout/evaluation_summary.md

### Counts By Severity

- high: 126
- medium: 68
- low: 2

### Counts By Issue Type

- missing_form_label: 3
- missing_image_alt: 32
- browser_focused_control_missing_name: 11
- zoom_fixed_width_content: 21
- focus_indicator_missing: 44
- missing_button_name: 1
- low_contrast_text: 44
- multiple_h1: 2
- missing_h1: 1
- browser_repeated_focus: 1
- generic_link_text: 4
- missing_link_name: 21
- skipped_heading_level: 4
- browser_focus_on_hidden_element: 7

## Sources Tested

| ID | Name | Source | Task | Status | Issues | Task blockers | AI Scout | Reports | Error |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| webaim_contact | WebAIM | https://webaim.org/contact/ |  | passed | 50 | 0 | ok | json: reports/outreach_ai_scout/webaim_contact.json, markdown: reports/outreach_ai_scout/webaim_contact.md, html: reports/outreach_ai_scout/webaim_contact.html, ai_scout_json: reports/outreach_ai_scout/webaim_contact_ai_scout.json, ai_scout_markdown: reports/outreach_ai_scout/webaim_contact_ai_scout.md |  |
| knowbility_contact | Knowbility | https://knowbility.org/contact/ |  | passed | 3 | 0 | ok | json: reports/outreach_ai_scout/knowbility_contact.json, markdown: reports/outreach_ai_scout/knowbility_contact.md, html: reports/outreach_ai_scout/knowbility_contact.html, ai_scout_json: reports/outreach_ai_scout/knowbility_contact_ai_scout.json, ai_scout_markdown: reports/outreach_ai_scout/knowbility_contact_ai_scout.md |  |
| w3c_wai_contacting | W3C WAI | https://www.w3.org/WAI/about/contacting/ |  | passed | 23 | 0 | ok | json: reports/outreach_ai_scout/w3c_wai_contacting.json, markdown: reports/outreach_ai_scout/w3c_wai_contacting.md, html: reports/outreach_ai_scout/w3c_wai_contacting.html, ai_scout_json: reports/outreach_ai_scout/w3c_wai_contacting_ai_scout.json, ai_scout_markdown: reports/outreach_ai_scout/w3c_wai_contacting_ai_scout.md |  |
| us_access_board_contact | U.S. Access Board | https://www.access-board.gov/contact/ |  | passed | 4 | 0 | ok | json: reports/outreach_ai_scout/us_access_board_contact.json, markdown: reports/outreach_ai_scout/us_access_board_contact.md, html: reports/outreach_ai_scout/us_access_board_contact.html, ai_scout_json: reports/outreach_ai_scout/us_access_board_contact_ai_scout.json, ai_scout_markdown: reports/outreach_ai_scout/us_access_board_contact_ai_scout.md |  |
| doit_center_home | DO-IT Center, University of Washington | https://www.washington.edu/doit/ |  | failed | 0 | 0 |  |  | HTTP error 502:  |
| cast_home | CAST | https://www.cast.org/ |  | passed | 29 | 0 | ok | json: reports/outreach_ai_scout/cast_home.json, markdown: reports/outreach_ai_scout/cast_home.md, html: reports/outreach_ai_scout/cast_home.html, ai_scout_json: reports/outreach_ai_scout/cast_home_ai_scout.json, ai_scout_markdown: reports/outreach_ai_scout/cast_home_ai_scout.md |  |
| iaap_home | IAAP / Accessibility Association | https://www.accessibilityassociation.org/ |  | passed | 19 | 0 | ok | json: reports/outreach_ai_scout/iaap_home.json, markdown: reports/outreach_ai_scout/iaap_home.md, html: reports/outreach_ai_scout/iaap_home.html, ai_scout_json: reports/outreach_ai_scout/iaap_home_ai_scout.json, ai_scout_markdown: reports/outreach_ai_scout/iaap_home_ai_scout.md |  |
| ahead_home | AHEAD | https://www.ahead.org/ |  | passed | 54 | 0 | ok | json: reports/outreach_ai_scout/ahead_home.json, markdown: reports/outreach_ai_scout/ahead_home.md, html: reports/outreach_ai_scout/ahead_home.html, ai_scout_json: reports/outreach_ai_scout/ahead_home_ai_scout.json, ai_scout_markdown: reports/outreach_ai_scout/ahead_home_ai_scout.md |  |
| ace_home | American Council on Education | https://www.acenet.edu/ |  | passed | 14 | 0 | ok | json: reports/outreach_ai_scout/ace_home.json, markdown: reports/outreach_ai_scout/ace_home.md, html: reports/outreach_ai_scout/ace_home.html, ai_scout_json: reports/outreach_ai_scout/ace_home_ai_scout.json, ai_scout_markdown: reports/outreach_ai_scout/ace_home_ai_scout.md |  |
| washington_post_accessibility | Washington Post accessibility page | https://www.washingtonpost.com/information/2023/03/01/accessibility/ |  | failed | 0 | 0 |  |  | The read operation timed out |

## Limitations

- This prototype only runs static HTML checks.
- It does not replace a full human accessibility audit.
- It does not yet perform browser-based interaction testing.
