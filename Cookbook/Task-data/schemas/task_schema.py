from enum import Enum
from pydantic import BaseModel, constr

class TaskStatus(str, Enum):
    completed = "Completed"
    incomplete = "Incompleted"

class Task(BaseModel):
    title: constr(min_length=1, max_length=255) # type: ignore
    description: constr(min_length=1) # type: ignore
    status: TaskStatus

class TaskListOrSingle(Task):
    id: int