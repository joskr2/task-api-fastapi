from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from jose import JWTError, jwt

from .database import get_db, engine, Base
from .schemas import UserCreate, User, Token, Task, TaskCreate, TaskUpdate
from .models import User as UserModel, Task as TaskModel
from .oauth2_config import settings
from .security import (
    verify_password, get_password_hash, create_access_token,
    oauth2_scheme
)
from .oauth2 import router as oauth2_router

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS.split(","),
    allow_headers=settings.CORS_HEADERS.split(","),
)

# Include OAuth routes
app.include_router(oauth2_router, prefix="/auth", tags=["OAuth2"])

# Función de utilidad para obtener el usuario actual
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Endpoints de autenticación
@app.post("/register", response_model=User, tags=["Users"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario"""
    # Verificar si el usuario ya existe
    db_user = db.query(UserModel).filter(
        (UserModel.username == user.username) | (UserModel.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        name=user.name,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
 
@app.post("/token", response_model=Token, tags=["Users"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login de usuario y generación de token"""
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=User, tags=["Users"])
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Obtiene la información del usuario actual"""
    return current_user   

# Endpoints de tareas
@app.get("/tasks", response_model=List[Task], tags=["Tasks"])
def get_tasks(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtiene todas las tareas del usuario actual"""
    return db.query(TaskModel).filter(TaskModel.owner_id == current_user.id).all()

@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def get_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene una tarea específica del usuario actual"""
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.owner_id == current_user.id
    ).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", response_model=Task, tags=["Tasks"])
def create_task(
    task: TaskCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea una nueva tarea para el usuario actual"""
    # Get the highest task ID for this user
    last_task = db.query(TaskModel).filter(
        TaskModel.owner_id == current_user.id
    ).order_by(TaskModel.id.desc()).first()
    
    # If user has no tasks, start with ID 1, otherwise increment the last ID
    new_task_id = 1 if last_task is None else last_task.id + 1
    
    db_task = TaskModel(
        id=new_task_id,
        name=task.name,
        description=task.description,
        completed=task.completed,
        owner_id=current_user.id
    )
    
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating task")

@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza una tarea existente del usuario actual"""
    db_task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.owner_id == current_user.id
    ).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@app.patch("/tasks/{task_id}/complete", response_model=Task, tags=["Tasks"])
def update_task_status(
    task_id: int,
    completed: bool,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza el estado de completado de una tarea"""
    db_task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.owner_id == current_user.id
    ).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.completed = completed
    db.commit()
    db.refresh(db_task)
    return db_task    

@app.delete("/tasks/{task_id}", tags=["Tasks"])
def delete_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina una tarea del usuario actual"""
    db_task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.owner_id == current_user.id
    ).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": f"Task {task_id} has been deleted successfully"}