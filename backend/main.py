import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import Base, engine, get_db
import models
import schemas
import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo App API")

# Comma-separated list in env var, e.g. "https://your-app.vercel.app,http://localhost:5173"
origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok"}


# ---------- Auth routes ----------


@app.post("/auth/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = models.User(
        email=user_in.email,
        hashed_password=auth.get_password_hash(user_in.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses "username" field for the identifier (we treat it as email)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# ---------- Todo routes ----------


@app.get("/todos", response_model=list[schemas.TodoOut])
def list_todos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Todo)
        .filter(models.Todo.owner_id == current_user.id)
        .order_by(models.Todo.created_at.desc())
        .all()
    )


@app.post("/todos", response_model=schemas.TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo_in: schemas.TodoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    todo = models.Todo(title=todo_in.title, owner_id=current_user.id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def _get_owned_todo(todo_id: int, db: Session, current_user: models.User) -> models.Todo:
    todo = (
        db.query(models.Todo)
        .filter(models.Todo.id == todo_id, models.Todo.owner_id == current_user.id)
        .first()
    )
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.patch("/todos/{todo_id}", response_model=schemas.TodoOut)
def update_todo(
    todo_id: int,
    todo_in: schemas.TodoUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    todo = _get_owned_todo(todo_id, db, current_user)
    if todo_in.title is not None:
        todo.title = todo_in.title
    if todo_in.completed is not None:
        todo.completed = todo_in.completed
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    todo = _get_owned_todo(todo_id, db, current_user)
    db.delete(todo)
    db.commit()
    return None
