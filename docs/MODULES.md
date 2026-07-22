# Modules

A11yway keeps optional checks separate so reports can say which evidence actually ran.

## Static

Static checks inspect the provided HTML source. They cover names, labels, headings, language, image alt text, tables, forms, media markup, and several WCAG review points.

## Browser

Browser mode uses Chromium to inspect the rendered page, walk keyboard focus, collect accessibility-tree output, and find rendered-DOM issues. It is one browser run, not a screen-reader certification.

## Low Vision

Low-vision checks inspect rendered contrast, zoom, reflow, text spacing, target size, focus visibility, and focus obstruction. Findings can be affected by layout timing and should be reviewed.

## Forms and Components

Form checks look at labels, required state, grouping, autocomplete, errors, and repeated-entry evidence. Component checks look at ARIA patterns such as dialogs, tabs, menus, comboboxes, sliders, and carousels.

## Language, Media, and Documents

Language checks cover page language, Indic-script boundaries, and mixed-script evidence. Media checks inspect captions, transcripts, controls, autoplay, and animation clues. Document checks inspect metadata and structure evidence for PDF and Office files when the optional parsers are available.

## Workflow and Task Execution

Task execution uses declared browser steps and keyboard-only interaction. Safe workflow mode blocks public form submission, login, upload, payment, destructive actions, and private workflows.

## AI Scout

AI Scout summarizes deterministic evidence when enabled. It can suggest review points, but it does not verify findings or establish failures by itself.
