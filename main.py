from typing import Optional

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Task Management API")

# -----------------------------
# In-memory database
# -----------------------------
tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False
    },
    {
        "id": 2,
        "title": "Build CRUD API",
        "done": False
    },
    {
        "id": 3,
        "title": "Submit Assignment",
        "done": True
    }
]


# -----------------------------
# Request Models
# -----------------------------
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, examples=["Buy milk"])


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# -----------------------------
# Helper Function
# -----------------------------
def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get(
    "/",
    summary="API Information",
    description="Returns general information about the API."
)
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": [
            "/tasks",
            "/health"
        ]
    }


# -----------------------------
# Health Check
# -----------------------------
@app.get(
    "/health",
    summary="Health Check",
    description="Checks whether the API is running."
)
def health():
    return {
        "status": "ok"
    }


# -----------------------------
# Get All Tasks
# -----------------------------
@app.get(
    "/tasks",
    summary="Get All Tasks",
    description="Returns all tasks."
)
def get_tasks():
    return tasks


# -----------------------------
# Get Single Task
# -----------------------------
@app.get(
    "/tasks/{task_id}",
    summary="Get Task by ID",
    description="Returns a task using its ID."
)
def get_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task


# -----------------------------
# Create Task
# -----------------------------
@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    summary="Create Task",
    description="Creates a new task."
)
def create_task(task: TaskCreate):

    title = task.title.strip()

    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    next_id = max([t["id"] for t in tasks], default=0) + 1

    new_task = {
        "id": next_id,
        "title": title,
        "done": False
    }

    tasks.append(new_task)

    return new_task


# -----------------------------
# Update Task
# -----------------------------
@app.put(
    "/tasks/{task_id}",
    summary="Update Task",
    description="Updates an existing task."
)
def update_task(task_id: int, updated_task: TaskUpdate):

    task = find_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if updated_task.title is None and updated_task.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nothing to update"
        )

    if updated_task.title is not None:
        title = updated_task.title.strip()

        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty"
            )

        task["title"] = title

    if updated_task.done is not None:
        task["done"] = updated_task.done

    return task


# -----------------------------
# Delete Task
# -----------------------------
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="Deletes a task by its ID."
)
def delete_task(task_id: int):

    task = find_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    tasks.remove(task)

    return Response(status_code=status.HTTP_204_NO_CONTENT)