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
- Rule: Link text is too generic
- Category: Interactive Elements
- Severity: medium
- Why it matters: Students who navigate by a list of links hear 'click here' with no context and cannot tell links apart.
- Suggested fix: Use descriptive link text like "Download scholarship guidelines" instead of "click here."
- Manual review: Surrounding text may add context visually, but the link should still make sense on its own.
- Static check limitation: The check only matches a small list of common generic phrases.

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
- Rule: Image missing useful alt text
- Category: Images
- Severity: medium
- Why it matters: Students using screen readers miss the image content entirely, which can hide instructions, diagrams, or required information.
- Suggested fix: Add alt text that describes the image purpose, or mark decorative images as presentation.
- Manual review: Confirm whether the image is informative or decorative; only a human can judge if existing alt text is actually useful.
- Static check limitation: Static checks cannot judge alt text quality, only whether it exists.

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
- Rule: Video missing captions
- Category: Media
- Severity: high
- Why it matters: Deaf and hard-of-hearing students cannot access spoken lesson content without captions or subtitles.
- Suggested fix: Add captions or subtitles for education video content.
- Manual review: Captions may be provided by an embedded player or platform instead of a track element.
- Static check limitation: The check only sees <track> elements; player-level or burned-in captions are invisible to static HTML.

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
- Rule: Audio missing a transcript
- Category: Media
- Severity: high
- Why it matters: Deaf and hard-of-hearing students need a text alternative to use audio lessons or instructions.
- Suggested fix: Add a transcript near audio lessons or instructions.
- Manual review: A transcript may exist on a linked page; confirm it is easy to find.
- Static check limitation: The check only looks for the word "transcript" in visible page text, which is a rough heuristic.

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
