# MCP Task Tracker

A Model Context Protocol (MCP) server for tracking personal tasks, built for
[course assignment name]. Domain: **Personal Productivity**.

## What it does

- **Tool `add_task(description, priority)`** — adds a new task (priority: low/medium/high)
- **Tool `complete_task(task_id)`** — marks a task as completed
- **Tool `reset_all_tasks(admin_token)`** — deletes all tasks; requires the admin token in `.env`
- **Prompt `daily_summary`** — generates a natural-language summary of open tasks

## Best practices implemented

1. **Input Sanitization** — all database queries in `storage.py` use parameterized
   SQL (`?` placeholders) instead of string interpolation, preventing SQL injection.
   Proof: `exploits/test_sql_injection.py`
2. **Rate Limiting** — `add_task` is capped at 5 calls per rolling 60-second window
   per tool. Proof: `exploits/test_rate_limit.py`

## Setup

1. Install [uv](https://docs.astral.sh/uv/) if you don't have it.
2. Clone this repo and `cd` into it.
3. Create the virtual environment and install dependencies:
```bash
   uv venv --python 3.12
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   uv sync
```
4. Create a `.env` file in the project root: