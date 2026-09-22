import sqlite3
from pathlib import Path

# Database file lives next to this script, so it works regardless of
# what folder you run the server from.
DB_PATH = Path(__file__).parent / "tasks.db"


def init_db():
    """Create the tasks table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def add_task(description: str, priority: str) -> int:
    """Insert a new task. Returns the new task's id."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "INSERT INTO tasks (description, priority) VALUES (?, ?)",
        (description, priority),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def complete_task(task_id: int) -> bool:
    """Mark a task as completed. Returns True if a task was actually found."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "UPDATE tasks SET completed = 1 WHERE id = ?",
        (task_id,),
    )
    conn.commit()
    found = cursor.rowcount > 0
    conn.close()
    return found


def list_open_tasks() -> list[dict]:
    """Return all tasks that aren't completed yet."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, description, priority FROM tasks WHERE completed = 0"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def reset_all_tasks():
    """Delete every task. Destructive — gated by an admin token in server.py."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM tasks")
    conn.commit()
    conn.close()
    