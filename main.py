from fastapi import Body, FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()

tasks = [
    {"id": 1, "title": "Learn HTTP basics", "done": False},
    {"id": 2, "title": "Build a FastAPI endpoint", "done": False},
    {"id": 3, "title": "Test the API", "done": True},
]


@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )


@app.post("/tasks")
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

    next_id = max((task["id"] for task in tasks), default=0) + 1

    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False
    }

    tasks.append(new_task)

    return JSONResponse(
        status_code=201,
        content=new_task
    )

@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: dict | None = Body(default=None)):
    task = None

    for existing_task in tasks:
        if existing_task["id"] == task_id:
            task = existing_task
            break

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )

    if not payload or ("title" not in payload and "done" not in payload):
        return JSONResponse(
            status_code=400,
            content={"error": "Provide title and/or done"}
        )

    if "title" in payload:
        title = payload["title"]

        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title must be a non-empty string"}
            )

        task["title"] = title.strip()

    if "done" in payload:
        done = payload["done"]

        if not isinstance(done, bool):
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be true or false"}
            )

        task["done"] = done

    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )