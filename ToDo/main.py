from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette import status

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

from auth import get_current_user, get_user_exception

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ToDo(BaseModel):
    title: str = ...
    description: str = ...
    priority: int = Field(..., ge=1, le=5, description="Priority must be between 1 and 5")
    completed: bool


def http_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)


@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@app.get("/todo/user")
async def get_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    print(dir(user))
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.id).all()


@app.get("/{todo_id}")
async def read_one(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model:
        return todo_model
    raise http_exception(404, "Todo not found")


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: ToDo, db: Session = Depends(get_db)):
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.completed = todo.completed

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return {'status': 201, 'message': 'Todo created successfully'}


@app.put("/{todo_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_todo(todo_id: int, todo: ToDo, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model:
        todo_model.title = todo.title
        todo_model.description = todo.description
        todo_model.priority = todo.priority
        todo_model.completed = todo.completed

        db.add(todo_model)
        db.commit()
        db.refresh(todo_model)
        return {'status': 200, 'message': 'Todo updated successfully'}
    raise http_exception(404, "Todo not found")


@app.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model:
        db.delete(todo_model)
        db.commit()
        return {'status': 204, 'message': 'Todo deleted successfully'}
    raise http_exception(404, "Todo not found")
