# A11yway Accessibility Report

## Summary

- Source: examples/sample_resource_page.html
- Source type: file
- Issues found: 4
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility

### Counts By Severity

- medium: 2
- high: 2

### Counts By Issue Type

- generic_link_text: 1
- missing_image_alt: 1
- missing_video_captions: 1
- missing_audio_transcript: 1

## Task Context

- Task name: Access learning resources
- Student profile: Hearing-impaired student

### Required Actions

- Find the resource section
- Open scholarship guidelines
- Understand instructions
- Access video lesson

### Likely Blockers

- Link text is too generic
  - Issue type: generic_link_text
  - Severity: medium
  - Task impact: Link text may not clearly explain the destination or action.
- Image is missing useful alt text
  - Issue type: missing_image_alt
  - Severity: medium
  - Task impact: Image content may be unavailable to students who need text alternatives.
- Video is missing captions
  - Issue type: missing_video_captions
  - Severity: high
  - Task impact: Video content may be inaccessible to students who need captions.
- Audio is missing a transcript
  - Issue type: missing_audio_transcript
  - Severity: high
  - Task impact: Audio content may be inaccessible to students who need a transcript.

## Issues Found

### 1. Link text is too generic

- Issue type: generic_link_text
- Severity: medium
- Suggested fix: Use descriptive link text like "Download scholarship guidelines" instead of "click here."

Evidence:

- tag: a
- href: /resources/help
- text: learn more
- line: 14
- reason: Link text is generic and does not explain the destination or action.

```html
<a href="/resources/help">learn more</a>
```

### 2. Image is missing useful alt text

- Issue type: missing_image_alt
- Severity: medium
- Suggested fix: Add alt text that describes the image purpose, or mark decorative images as presentation.

Evidence:

- tag: img
- src: resource-library.png
- line: 17
- reason: Image is missing useful alt text.

```html
<img src="resource-library.png">
```

### 3. Video is missing captions

- Issue type: missing_video_captions
- Severity: high
- Suggested fix: Add captions or subtitles for education video content.

Evidence:

- tag: video
- src: lesson-overview.mp4
- line: 20
- reason: Video has no captions or subtitles track.

```html
<video controls src="lesson-overview.mp4">
```

### 4. Audio is missing a transcript

- Issue type: missing_audio_transcript
- Severity: high
- Suggested fix: Add a transcript near audio lessons or instructions.

Evidence:

- tag: audio
- src: assignment-instructions.mp3
- line: 22
- reason: Audio element has no visible document text containing "transcript".

```html
<audio controls src="assignment-instructions.mp3">
```

## Limitations

- This prototype only runs static HTML checks.
- It does not replace a full human accessibility audit.
- It does not yet perform browser-based interaction testing.
