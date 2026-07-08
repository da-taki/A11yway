"""CLI-style pseudocode entry point for A11yway.

This file shows the intended flow without implementing real browser,
PDF, or AI integrations yet.
"""

from pathlib import Path

from a11yway.agents.dyslexia_agent import DyslexiaAgent
from a11yway.agents.hearing_agent import HearingAgent
from a11yway.agents.keyboard_agent import KeyboardOnlyAgent
from a11yway.agents.low_vision_agent import LowVisionAgent
from a11yway.core.task_runner import TaskRunner


def main() -> None:
    """Run a small pseudocode demo using the sample tasks."""
    sample_tasks_path = Path("examples/sample_tasks.json")

    agents = [
        KeyboardOnlyAgent(),
        LowVisionAgent(),
        DyslexiaAgent(),
        HearingAgent(),
    ]

    runner = TaskRunner(agents=agents)
    tasks = runner.load_tasks(sample_tasks_path)

    # For the scaffold, only run the first sample task.
    report = runner.run_task(tasks[0])

    print("A11yway pseudocode run complete")
    print(f"Task: {report.task.title}")
    print(f"Agents used: {', '.join(report.agents_used)}")
    print(f"Issues found: {len(report.issues)}")


if __name__ == "__main__":
    main()
