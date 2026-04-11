from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import AuthDep

todo_router = APIRouter(tags=["Todo Management"])


@todo_router.get('/todos', response_model=list[TodoResponse])
def get_todos(db: SessionDep, user: AuthDep):
    return user.todos


@todo_router.get('/todo/{id}', response_model=TodoResponse)
def get_todo_by_id(id: int, db: SessionDep, user: AuthDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return todo


@todo_router.post('/todos', response_model=TodoResponse)
def create_todo(db: SessionDep, user: AuthDep, todo_data: TodoCreate):
    todo = Todo(text=todo_data.text, user_id=user.id)
    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Error creating todo"
        )


@todo_router.put('/todo/{id}', response_model=TodoResponse)
def update_todo(id: int, db: SessionDep, user: AuthDep, todo_data: TodoUpdate):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()

    if not todo:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if todo_data.text is not None:
        todo.text = todo_data.text

    if todo_data.done is not None:
        todo.done = todo_data.done

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


@todo_router.delete('/todo/{id}')
def delete_todo(id: int, db: SessionDep, user: AuthDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()

    if not todo:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.delete(todo)
    db.commit()

    return {"message": "Deleted"}


@todo_router.post('/category', response_model=CategoryResponse)
def create_category(db: SessionDep, user: AuthDep, category_data: CategoryResponse):
    category = Category(text=category_data.text, user_id=user.id)

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@todo_router.post('/todo/{todo_id}/category/{cat_id}')
def add_category_to_todo(todo_id: int, cat_id: int, db: SessionDep, user: AuthDep):

    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)).one_or_none()
    category = db.exec(select(Category).where(Category.id == cat_id, Category.user_id == user.id)).one_or_none()

    if not todo or not category:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if category not in todo.categories:
        todo.categories.append(category)

    db.add(todo)
    db.commit()

    return {"message": "Category added"}


@todo_router.delete('/todo/{todo_id}/category/{cat_id}')
def remove_category_from_todo(todo_id: int, cat_id: int, db: SessionDep, user: AuthDep):

    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)).one_or_none()
    category = db.exec(select(Category).where(Category.id == cat_id, Category.user_id == user.id)).one_or_none()

    if not todo or not category:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if category in todo.categories:
        todo.categories.remove(category)

    db.add(todo)
    db.commit()

    return {"message": "Category removed"}


@todo_router.get('/category/{cat_id}/todos', response_model=list[TodoResponse])
def get_todos_for_category(cat_id: int, db: SessionDep, user: AuthDep):

    category = db.exec(select(Category).where(Category.id == cat_id, Category.user_id == user.id)).one_or_none()

    if not category:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return category.todos
