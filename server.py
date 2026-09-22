import os
import time
from pathlib import Path
from collections import defaultdict

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

import storage

load_dotenv(Path(__file__).parent / ".env")  # reads .env into this program's environment variables

mcp = MCPServer("task-tracker")
storage.init_db()

# --- Rate limiting: max calls per rolling 60-second window ---
_MAX_CALLS_PER_MINUTE = 5
_call_timestamps: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    timestamps = _call_timestamps[tool_name]
    timestamps[:] = [t for t in timestamps if now - t < 60]  # drop old entries
    if len(timestamps) >= _MAX_CALLS_PER_MINUTE:
        raise ValueError(
            f"Rate limit exceeded for '{tool_name}': "
            f"max {_MAX_CALLS_PER_MINUTE} calls per minute."
        )
    timestamps.append(now)


@mcp.tool()
def add_task(description: str, priority: str = "medium") -> dict:
    """Add a new task to the tracker."""
    _check_rate_limit("add_task")
    if not description or not description.strip():
        raise ValueError("Task description cannot be empty.")
    if priority not in ("low", "medium", "high"):
        raise ValueError("Priority must be one of: low, medium, high.")
    task_id = storage.add_task(description.strip(), priority)
    return {"id": task_id, "description": description.strip(), "priority": priority}


@mcp.tool()
def complete_task(task_id: int) -> dict:
    """Mark a task as completed by its id."""
    found = storage.complete_task(task_id)
    if not found:
        raise ValueError(f"No task found with id {task_id}.")
    return {"id": task_id, "status": "completed"}


@mcp.tool()
def reset_all_tasks(admin_token: str) -> dict:
    """Delete every task. Requires the admin token stored in .env."""
    expected_token = os.environ.get("ADMIN_RESET_TOKEN")
    if not expected_token or admin_token != expected_token:
        raise ValueError("Invalid admin token.")
    storage.reset_all_tasks()
    return {"status": "all tasks deleted"}


@mcp.prompt()
def daily_summary() -> str:
    """A prompt template that asks the assistant to summarize open tasks."""
    tasks = storage.list_open_tasks()
    if not tasks:
        return "There are no open tasks right now. Let the user know they're all caught up."
    task_lines = "\n".join(
        f"- [{t['priority']}] {t['description']} (id: {t['id']})" for t in tasks
    )
    return (
        "Here are the user's current open tasks:\n\n"
        f"{task_lines}\n\n"
        "Summarize these tasks in a short, friendly paragraph, "
        "and call out anything marked high priority."
    )


if __name__ == "__main__":
    mcp.run()