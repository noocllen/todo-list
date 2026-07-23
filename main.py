from uuid import uuid4
from fastapi import FastAPI, status
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


tasks: list[Task] = []


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



class Book(BaseModel):
    name: str


book: Book


@app.get("/book")
def get_book():
    try:
        return f"Любимая книга {book.name}"
    except Exception:
        return "Книги нет"


@app.post("/book", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(payload: Book):
    global book
    book = Book(name=payload.name)
    return book
