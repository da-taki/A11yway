# Workflow Testing

`--workflow --workflow-config <file> --safe-public-mode` runs a structured safe workflow.

Supported actions include safe navigation, activating links, opening/closing menus or dialogs, selecting tabs, expanding disclosures, assertions, back, and reload. Public safe mode blocks form submission, account creation, login, payment, upload, chat messages, destructive actions, CAPTCHA interaction, and private workflows.

Workflow results record step completion, blockers, and abandonment points. Submitting workflows should be tested only against local fixtures or explicitly permitted targets.
