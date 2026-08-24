from fastapi import Body, FastAPI
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