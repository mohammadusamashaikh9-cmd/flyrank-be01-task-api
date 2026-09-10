import sqlite3
from fastapi import Body, FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()

DB_PATH = "tasks.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]

        if task_count == 0:
            seed_tasks = [
                ("Learn HTTP basics", 0),
                ("Build a FastAPI endpoint", 0),
                ("Test the API", 1),
            ]

            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                seed_tasks,
            )

        conn.commit()


init_db()


@app.get("/", summary="API information")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Health check")
def health_check():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def get_tasks():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, title, done FROM tasks ORDER BY id"
        ).fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"]),
        }
        for row in rows
    ]


@app.get("/tasks/{task_id}", summary="Get a task by ID")
def get_task(task_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


@app.post("/tasks", summary="Create a task")
def create_task(payload: dict | None = Body(default=None)):
    if payload is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    title = payload.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    clean_title = title.strip()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (clean_title, 0),
        )
        new_id = cursor.lastrowid
        conn.commit()

    new_task = {
        "id": new_id,
        "title": clean_title,
        "done": False,
    }

    return JSONResponse(
        status_code=201,
        content=new_task,
    )


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, payload: dict | None = Body(default=None)):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if row is None:
            return JSONResponse(
                status_code=404,
                content={"error": f"Task {task_id} not found"},
            )

        if not payload or ("title" not in payload and "done" not in payload):
            return JSONResponse(
                status_code=400,
                content={"error": "Provide title and/or done"},
            )

        new_title = row["title"]
        new_done = bool(row["done"])

        if "title" in payload:
            title = payload["title"]

            if not isinstance(title, str) or not title.strip():
                return JSONResponse(
                    status_code=400,
                    content={"error": "Title must be a non-empty string"},
                )

            new_title = title.strip()

        if "done" in payload:
            done = payload["done"]

            if not isinstance(done, bool):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Done must be true or false"},
                )

            new_done = done

        conn.execute(
            """
            UPDATE tasks
            SET title = ?, done = ?
            WHERE id = ?
            """,
            (new_title, int(new_done), task_id),
        )

        conn.commit()

    return {
        "id": task_id,
        "title": new_title,
        "done": new_done,
    }


@app.delete("/tasks/{task_id}", summary="Delete a task")
def delete_task(task_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        if cursor.rowcount == 0:
            return JSONResponse(
                status_code=404,
                content={"error": f"Task {task_id} not found"},
            )

        conn.commit()

    return Response(status_code=204)