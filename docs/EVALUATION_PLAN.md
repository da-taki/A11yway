# Evaluation Plan

This plan describes how A11yway could be evaluated once the prototype has enough real behavior to test pages and produce reports.

## Phase 1: Benchmark Public Education Pages

Test a small set of public school, NGO, and education resource pages. Choose common workflows such as finding homework, submitting a form, downloading a PDF, or watching a lesson video.

The goal is to see whether the agents can identify realistic barriers in common education tasks.

## Phase 2: Send Reports for Feedback

Share generated reports with NGOs, schools, or education teams. Ask whether the reports are understandable, useful, and practical.

Feedback questions:

- Are the reported barriers believable?
- Are the suggested fixes practical?
- Is the severity level useful?
- Is any important context missing?

## Phase 3: Expert Review

Ask accessibility reviewers, developers, or technology teams to review selected reports. They should check whether findings are accurate and whether the suggested fixes match good accessibility practice.

## Phase 4: Compare Automated Findings With Human Feedback

Compare A11yway findings with feedback from students, teachers, accessibility experts, and developers.

The goal is not to replace human review. The goal is to learn where automated task-based testing helps and where it misses real barriers.

## Metrics

- Usefulness: do users find the report helpful for improving the site?
- Accuracy: are findings technically and practically correct?
- Clarity: can non-experts understand the issue and fix?
- False positives: how often does the tool report problems that are not real barriers?
- Missed barriers: what important problems did the tool fail to report?
- Task completion failure rate: how often does an agent fail to complete the task because of accessibility barriers?
