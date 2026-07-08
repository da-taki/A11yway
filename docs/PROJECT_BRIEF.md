# Project Brief

## Problem

Many education websites and learning portals are difficult for disabled students to use. A page can pass some automated checks and still block a student from completing a real task, such as submitting a form, finding homework, reading instructions, or watching a lesson.

## Target Users

- Schools and universities that manage online forms, portals, and resources.
- NGOs and education programs that publish learning material.
- Accessibility testers who need task-based evidence.
- Developers who want practical guidance instead of only rule names.
- Student teams learning how accessibility testing works.

## Why This Is Not Just a Normal WCAG Checker

Traditional automated accessibility tools usually inspect page markup and report technical rule failures. That is useful, but it does not always show whether a student can complete an actual education task.

A11yway focuses on task completion. It asks what happens when a specific student profile tries to complete a realistic workflow.

For example:

- Can the student find the correct file?
- Can the student understand what the form is asking?
- Can the student complete the task without a mouse?
- Can the student access the same information in a video or PDF?

## Core Idea

A11yway uses disabled-student agents that try to complete real education tasks. Each agent observes the page, checks for barriers related to its profile, and returns findings that can be turned into a report.

This first version is only a scaffold. The agent behavior is written as pseudocode so the project can later add real page analysis and browser automation.

## Initial Agents

- Keyboard-only student: checks keyboard navigation, focus order, focus visibility, and form completion without a mouse.
- Low-vision student: checks contrast, zoom behavior, small text, and layout overflow.
- Dyslexia/reading-difficulty student: checks dense instructions, confusing error messages, long paragraphs, and missing plain-language alternatives.
- Hearing-impaired student: checks captions, transcripts, and audio-only instructions.

## Future Agents

- Screen reader student.
- Motor-impaired student.
- Cognitive-load agent.
- Mobile-only student.
