from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей таблиц в БД"""
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))


class TaskORM(Base):
    """Модель для таблицы задачи в БД"""
    __tablename__ = "tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)


class CategoryORM(Base):
    """Модель для таблицы категорий в БД"""
    __tablename__ = "categories"

    name: Mapped[str]


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def get_db():
    """"Зависимость для БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(lifespan=lifespan)
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


class Category(BaseModel):
    id: str
    name: str


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str


categories: list[Category] = []


def task_to_model(task: TaskORM) -> Task:
    """Конвертация ORM в Pydantic"""
    return Task(id=task.id, title=task.title, completed=task.completed)


@app.get("/tasks", response_model=list[Task])
def get_tasks(db: Session = Depends(get_db)) -> list[Task]:
    """Получение списка задач"""
    tasks = db.scalars(select(TaskORM)).all()
    return tasks


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    """
    Создание задачи
    task_id приходит из url    
    payload из тела запроса
    """
    task = TaskORM(title=payload.title, completed=False)

    db.add(task)
    db.commit()
    return task_to_model(task)


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    """
    Редактирование задачи
    task_id приходит из url    
    payload из тела запроса
    """
    task = db.get(TaskORM, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    task.title = payload.title if payload.title is not None else task.title
    task.completed = payload.completed if payload.completed is not None else task.completed
    db.commit()
    return task_to_model(task)


@app.delete("/tasks/{task_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.get(TaskORM, task_id)
    if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    db.delete(task)
    db.commit()


def category_to_model(category: CategoryORM) -> Category:
    """Конвертация ORM в Pydantic"""
    return Category(id=category.id, name=category.name)


@app.get("/categories", response_model=list[Category])
def get_categories(db: Session = Depends(get_db)):
    categories = db.scalars(select(CategoryORM)).all()
    return categories


@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = CategoryORM(name=payload.name)

    db.add(category)
    db.commit()
    return category_to_model(category)


@app.patch("/categories/{category_id}", response_model=Category)
def update_category(category_id: str, payload: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.get(CategoryORM, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    category.name = payload.name if payload.name is not None else category.name
    db.commit()
    return category_to_model(category)

@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, db: Session = Depends(get_db)):
    category = db.get(CategoryORM, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    db.delete(category)
    db.commit()
