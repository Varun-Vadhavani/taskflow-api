from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.models import TaskStatus

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class TaskCreate(BaseModel):
    """Body of POST /tasks."""

    model_config = ConfigDict(extra="forbid")

    title: Title
    description: str | None = Field(default=None, max_length=500)
    status: TaskStatus = TaskStatus.todo
    due_date: date | None = None


class TaskUpdate(BaseModel):
    """Body of PATCH /tasks/{id}. Every field is optional."""

    model_config = ConfigDict(extra="forbid")

    title: Title | None = None
    description: str | None = Field(default=None, max_length=500)
    status: TaskStatus | None = None
    due_date: date | None = None

    @model_validator(mode="after")
    def check_update(self) -> "TaskUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        for name in ("title", "status"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class TaskRead(BaseModel):
    """What the API returns for a task."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    due_date: date | None
    created_at: datetime
    updated_at: datetime