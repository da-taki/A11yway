# A11yway Batch Accessibility Index

## Summary

- Total pages tested: 6
- Total issues: 167
- CSV index: reports/email_verified_outreach/index.csv
- Evaluation summary: reports/email_verified_outreach/evaluation_summary.md

### Counts By Severity

- high: 108
- medium: 59

### Counts By Issue Type

- missing_image_alt: 81
- low_contrast_text: 57
- zoom_fixed_width_content: 18
- focus_indicator_missing: 4
- generic_link_text: 6
- skipped_heading_level: 1

## Sources Tested

| ID | Name | Source | Task | Status | Issues | Task blockers | AI Scout | Reports | Error |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| level_access_contact | Level Access | https://www.levelaccess.com/contact/ |  | passed | 84 | 0 | ok | json: reports/email_verified_outreach/level_access_contact.json, markdown: reports/email_verified_outreach/level_access_contact.md, html: reports/email_verified_outreach/level_access_contact.html, ai_scout_json: reports/email_verified_outreach/level_access_contact_ai_scout.json, ai_scout_markdown: reports/email_verified_outreach/level_access_contact_ai_scout.md |  |
| fable_contact | Fable | https://makeitfable.com/contact-fable/ |  | passed | 35 | 0 | ok | json: reports/email_verified_outreach/fable_contact.json, markdown: reports/email_verified_outreach/fable_contact.md, html: reports/email_verified_outreach/fable_contact.html, ai_scout_json: reports/email_verified_outreach/fable_contact_ai_scout.json, ai_scout_markdown: reports/email_verified_outreach/fable_contact_ai_scout.md |  |
| abilitynet_contact | AbilityNet | https://abilitynet.org.uk/how-to-contact-us |  | passed | 9 | 0 | ok | json: reports/email_verified_outreach/abilitynet_contact.json, markdown: reports/email_verified_outreach/abilitynet_contact.md, html: reports/email_verified_outreach/abilitynet_contact.html, ai_scout_json: reports/email_verified_outreach/abilitynet_contact_ai_scout.json, ai_scout_markdown: reports/email_verified_outreach/abilitynet_contact_ai_scout.md |  |
| digital_accessibility_centre_home | Digital Accessibility Centre | https://digitalaccessibilitycentre.org/ |  | passed | 9 | 0 | ok | json: reports/email_verified_outreach/digital_accessibility_centre_home.json, markdown: reports/email_verified_outreach/digital_accessibility_centre_home.md, html: reports/email_verified_outreach/digital_accessibility_centre_home.html, ai_scout_json: reports/email_verified_outreach/digital_accessibility_centre_home_ai_scout.json, ai_scout_markdown: reports/email_verified_outreach/digital_accessibility_centre_home_ai_scout.md |  |
| coursera_contact | Coursera | https://www.coursera.org/about/contact |  | passed | 15 | 0 | ok | json: reports/email_verified_outreach/coursera_contact.json, markdown: reports/email_verified_outreach/coursera_contact.md, html: reports/email_verified_outreach/coursera_contact.html, ai_scout_json: reports/email_verified_outreach/coursera_contact_ai_scout.json, ai_scout_markdown: reports/email_verified_outreach/coursera_contact_ai_scout.md |  |
| rnib_home | RNIB | https://www.rnib.org.uk/ |  | passed | 15 | 0 | ok | json: reports/email_verified_outreach/rnib_home.json, markdown: reports/email_verified_outreach/rnib_home.md, html: reports/email_verified_outreach/rnib_home.html, ai_scout_json: reports/email_verified_outreach/rnib_home_ai_scout.json, ai_scout_markdown: reports/email_verified_outreach/rnib_home_ai_scout.md |  |

## Limitations

- This prototype only runs static HTML checks.
- It does not replace a full human accessibility audit.
- It does not yet perform browser-based interaction testing.
