from fastapi import FastAPI
from schemas.task_schema import Task, TaskListOrSingle

app = FastAPI()

@app.post('/tasks', response_model=TaskListOrSingle)
async def create_tasks(task: Task):
    return {
        **task.model_dump(), "id": 0
    }