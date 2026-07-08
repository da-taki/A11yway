# Sample Accessibility Task Report

This is a fictional sample report. It reflects the kind of static HTML findings
the current prototype can begin to produce, but it is not a complete audit.

## Site

Riverside Learning Portal

## Tested Task

Submit a scholarship application form.

## Agents Used

- Keyboard-only student.
- Low-vision student.
- Dyslexia/reading-difficulty student.
- Hearing-impaired student.

## Issues Found

### 1. Form Field Has No Visible Label

Severity: High

Agent: Keyboard-only student

Evidence: The "Guardian income" input is announced only as "edit field" in the placeholder test notes. A keyboard user may not know what information is required.

Suggested fix: Add a visible text label connected to the input with the `for` and `id` attributes.

### 2. Focus Indicator Is Hard To See

Severity: Medium

Agent: Keyboard-only student

Evidence: The current focus outline is faint and difficult to see on the application form buttons.

Suggested fix: Add a strong visible focus style with enough contrast around links, buttons, and form controls.

### 3. Instructions Are Too Dense

Severity: Medium

Agent: Dyslexia/reading-difficulty student

Evidence: Scholarship eligibility instructions are written as one long paragraph with several conditions.

Suggested fix: Break instructions into short sections, use bullet points, and add a plain-language summary.

### 4. Intro Video Has No Transcript

Severity: High

Agent: Hearing-impaired student

Evidence: The application page includes an intro video, but no captions or transcript are linked near the video.

Suggested fix: Add synchronized captions and a text transcript that includes all spoken instructions.

### 5. Link Text Is Too Generic

Severity: Medium

Agent: Page Analyzer

Evidence: A help link uses the text "click here", which does not explain the destination when read out of context.

Suggested fix: Use descriptive link text such as "Read scholarship application help".

## Retest Checklist

- Confirm all form inputs have visible labels.
- Confirm every interactive element has a visible keyboard focus state.
- Confirm instructions are split into short, clear steps.
- Confirm video captions are available.
- Confirm a transcript is available next to the video.
- Rerun the same scholarship application task with all agents.
