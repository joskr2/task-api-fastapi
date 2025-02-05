from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class TaskStatusUpdate(BaseModel):
    completed: bool

class TaskCreate(BaseModel):
    name: str
    description: str | None = None
    completed: bool = False

class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    completed: bool | None = None

class Task(BaseModel):
    id: int
    name: str
    description: str | None = None
    completed: bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

tasks = [
    Task(id=1, name="Task 1", description="Description 1", completed=False, created_at=datetime.now(), updated_at=datetime.now()),
    Task(id=2, name="Task 2", description="Description 2", completed=False, created_at=datetime.now(), updated_at=datetime.now()),
    Task(id=3, name="Task 3", description="Description 3", completed=False, created_at=datetime.now(), updated_at=datetime.now()),
    Task(id=4, name="Task 4", description="Description 4", completed=False, created_at=datetime.now(), updated_at=datetime.now()),
]

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task_by_id(task_id: int):
    task = next((task for task in tasks if task.id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task    

@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    new_task_id = max(task.id for task in tasks) + 1
    new_task = Task(
        id=new_task_id,
        name=task.name,
        description=task.description,
        completed=task.completed
    )
    tasks.append(new_task)
    return new_task    

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate):
    task = next((task for task in tasks if task.id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.now()
    return task    

@app.patch("/tasks/{task_id}/status", response_model=Task)
def update_task_status(task_id: int, status_update: TaskStatusUpdate):
    task = next((task for task in tasks if task.id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.completed = status_update.completed
    task.updated_at = datetime.now()
    return task    

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    task_index = next((index for index, task in enumerate(tasks) if task.id == task_id), None)
    if task_index is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    deleted_task = tasks.pop(task_index)
    return {"message": f"Task {task_id} has been deleted successfully"}    