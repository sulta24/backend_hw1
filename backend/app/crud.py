from sqlalchemy.orm import Session
from . import models, schemas

# --- User CRUD Operations ---

def get_user_by_username(db: Session, username: str):
    # Retrieve a user by their username
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    # Create a new user record in the database
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # Refresh the instance to get any new database-generated data (like ID)
    return db_user

# --- Task CRUD Operations ---

def get_task(db: Session, task_id: int, user_id: int):
    # Retrieve a single task by its ID, ensuring it belongs to the specified user
    return db.query(models.Task).filter(models.Task.id == task_id, models.Task.user_id == user_id).first()

def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # Retrieve a list of tasks for a specific user with pagination
    return db.query(models.Task).filter(models.Task.user_id == user_id).offset(skip).limit(limit).all()

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    # Create a new task record in the database and assign it to a user
    db_task = models.Task(**task.dict(), user_id=user_id) # Assign user_id
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, user_id: int, task_update: schemas.TaskCreate):
    # Update an existing task, ensuring it belongs to the specified user
    db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.user_id == user_id).first()
    if db_task:
        # Update attributes from the Pydantic schema
        for key, value in task_update.dict(exclude_unset=True).items(): # exclude_unset=True only updates provided fields
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, user_id: int):
    # Delete a task by its ID, ensuring it belongs to the specified user
    db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.user_id == user_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task
