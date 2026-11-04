import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskRead

logger = logging.getLogger("taskflow.tasks")

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# The largest number a Postgres "integer" column can hold.
MAX_INT = 2_147_483_647


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
)
def create_task(
    payload: TaskCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> Task:
    """Create a new task and return it, including its generated id."""
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)

    response.headers["Location"] = f"/tasks/{task.id}"
    logger.info("Created task id=%s", task.id)
    return task


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get one task",
    responses={404: {"description": "Task not found"}},
)
def get_task(
    task_id: int = Path(ge=1, le=MAX_INT, description="The task's id"),
    db: Session = Depends(get_db),
) -> Task:
    """Return a single task by its id."""
    task = db.get(Task, task_id)
    if task is None:
        logger.info("Task id=%s not found", task_id)
        raise HTTPException(status_code=404, detail="Task not found")
    return task