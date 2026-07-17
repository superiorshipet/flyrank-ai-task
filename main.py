from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI(title="Task Management API")

DEFAULT_TASKS = [
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

tasks = [task.copy() for task in DEFAULT_TASKS]
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, examples=["Buy Milk"])


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def get_next_id():
    return max((task["id"] for task in tasks), default=0) + 1
@app.get(
    "/",
    summary="API Information",
    description="Returns general information about the API."
)
def root():
    return {
        "name": "Task API",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/tasks",
            "/stats",
            "/reset"
        ]
    }
@app.get(
    "/health",
    summary="Health Check",
    description="Checks whether the API is running."
)
def health():
    return {
        "status": "ok"
    }
@app.get(
    "/tasks",
    summary="Get All Tasks",
    description="Returns all tasks with optional filtering and searching."
)
def get_tasks(
    done: Optional[bool] = Query(
        default=None,
        description="Filter by completed status"
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search by title"
    )
):
    result = tasks

    if done is not None:
        result = [task for task in result if task["done"] == done]

    if search:
        result = [
            task
            for task in result
            if search.lower() in task["title"].lower()
        ]

    return result


@app.get(
    "/tasks/{task_id}",
    summary="Get Task",
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

    new_task = {
        "id": get_next_id(),
        "title": title,
        "done": False
    }

    tasks.append(new_task)

    return new_task

@app.put(
    "/tasks/{task_id}",
    summary="Update Task",
    description="Updates the title and/or completion status of a task."
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
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="Deletes a task."
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


# ------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------

@app.get(
    "/stats",
    summary="Task Statistics",
    description="Returns statistics about the current tasks."
)
def get_stats():

    total = len(tasks)
    completed = sum(task["done"] for task in tasks)

    return {
        "total": total,
        "done": completed,
        "open": total - completed
    }


# ------------------------------------------------------------------
# Reset Tasks
# ------------------------------------------------------------------

@app.post(
    "/reset",
    summary="Reset Tasks",
    description="Restores the original sample tasks."
)
def reset_tasks():

    tasks.clear()

    for task in DEFAULT_TASKS:
        tasks.append(task.copy())

    return {
        "message": "Tasks reset successfully.",
        "tasks": tasks
    }