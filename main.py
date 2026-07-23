from uuid import uuid4
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


class Task(BaseModel):
    """Pydantic-модель(схема) объекта задачи"""
    id: str
    title: str
    completed: bool    


class TaskCreate(BaseModel):
    """Pydantic-модель(схема) запроса на создание задачи"""
    title: str


class TaskUpdate(BaseModel):
    """Pydantic-модель(схема) запроса на редактирование задачи"""
    title: str | None = None
    completed: bool | None = None


tasks: list[Task] = []


class Category(BaseModel):
    id: str
    name: str


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str


categories: list[Category] = []



@app.get("/tasks", response_model=list[Task])
def read_tasks():
    """Получение списка задач"""
    return tasks


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    """Создание задачи"""
    task = Task(id=str(uuid4()), title=payload.title, completed=False)
    tasks.append(task)
    return task


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, payload: TaskUpdate):
    """Редактирование задачи"""
    for task in tasks:
        if task.id == task_id:
            if payload.title is not None:
                task.title = payload.title
            if payload.completed is not None:
                task.completed = payload.completed
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")


@app.delete("/tasks/{task_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")



@app.get("/categories", response_model=list[Category])
def get_categories():
    return categories


@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate):
    category = Category(id=str(uuid4()), name=payload.name)
    categories.append(category)
    return category


@app.patch("/categories/{category_id}", response_model=Category)
def update_category(category_id: str, payload: CategoryUpdate):
    for category in categories:
        if category.id == category_id:
            category.name = payload.name
        return category
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str):
    for category in categories:
        if category.id == category_id:
            categories.remove(category)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
