# A11yway

A11yway is an early pseudocode scaffold for an agentic accessibility testing tool focused on education websites, forms, PDFs, and learning portals.

The idea is simple: instead of only scanning a page for technical accessibility rules, A11yway will eventually simulate how students with different accessibility needs complete real education tasks. Example tasks include finding an assignment, submitting a form, reading instructions, accessing a video, or downloading a resource.

## Why Education Accessibility Testing Matters

Education websites often contain forms, documents, videos, assignments, portals, and deadlines. If any of those are inaccessible, students can be blocked from learning or from completing required school tasks.

Accessibility testing in education should answer practical questions:

- Can a keyboard-only student complete the task?
- Can a low-vision student read and use the page after zooming?
- Are instructions clear for a student with reading difficulty?
- Are captions or transcripts available for audio and video content?

## What "Agentic Accessibility Testing" Means Here

In this project, an agent is a small simulated student profile. Each agent has a specific accessibility need and tries to complete a task from that point of view.

For this first draft, agents only contain placeholder logic and readable pseudocode. Later, they could use browser automation, PDF analysis, accessibility APIs, and human feedback to produce stronger results.

## MVP Scope

The first MVP should stay small:

- Load a task description.
- Run a few student accessibility agents.
- Collect barriers found by each agent.
- Suggest practical fixes.
- Build a simple report.

This scaffold does not include real AI integrations, browser automation, PDF parsing, or production APIs yet.

## Try the Prototype

Run the sample HTML form check:

```bash
python -m a11yway.main examples/sample_form.html
```

If no file path is provided, the command tries `examples/sample_form.html`.

The current prototype only checks basic HTML form labels. It can flag common unlabeled `input`, `textarea`, and `select` controls, while ignoring hidden and submit inputs. This is the first real check, not a complete accessibility audit.

## Example Use Case

A school wants to test whether students can submit a scholarship application form. A11yway runs several student agents against that task and reports problems such as missing form labels, confusing errors, weak focus indicators, or instructions that are only available in audio.

## Current Status

This repository is currently a lightweight pseudocode scaffold. It is meant to be readable for a student developer and easy to grow into a Python, Flask, or FastAPI project later.
