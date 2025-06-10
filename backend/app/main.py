from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware

# Import necessary modules from your application
from . import models, schemas, crud, auth
from .database import engine, get_db

# Create all database tables defined in models.py if they don't exist.
# This runs once when the application starts.
models.Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application
app = FastAPI(
    title="Todo List API",
    description="A simple Todo List application with JWT authentication.",
    version="1.0.0",
)

# --- CORS Middleware ---
# This section configures Cross-Origin Resource Sharing (CORS).
# It allows your frontend (e.g., served from file:// or a different origin)
# to make requests to your backend API.
origins = [
    "http://localhost",
    "http://localhost:8000", # Your backend's host and port
    "http://localhost:8080", # Example for a development server
    "file://", # Allow requests from local files (for index.html opened directly)
    "null", # Some browsers send "null" origin for local files or certain scenarios
    "http://127.0.0.1:8000", # Another common localhost address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of origins that are allowed to make requests
    allow_credentials=True, # Allow cookies, authorization headers, etc.
    allow_methods=["*"], # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"], # Allow all headers
)

# --- Authentication Endpoints ---

@app.post("/register/", response_model=schemas.User, summary="Register a new user")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.
    - **username**: Unique username for the new user.
    - **password**: Password for the new user.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # Hash the password before storing it
    hashed_password = auth.get_password_hash(user.password)
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)

@app.post("/token", response_model=schemas.Token, summary="Login and get an access token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a JWT access token.
    - **username**: User's username.
    - **password**: User's password.
    """
    user = crud.get_user_by_username(db, username=form_data.username)
    # Verify username and password
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create an access token that expires in ACCESS_TOKEN_EXPIRE_MINUTES
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me/", response_model=schemas.User, summary="Get current user information (secured)")
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """
    Retrieves the information of the current authenticated user.
    Requires a valid JWT token in the Authorization header (Bearer token).
    """
    return current_user

# --- Secured Task Endpoints ---

@app.post("/create_task/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED, summary="Create a new task (secured)")
def create_task_for_current_user(
    task: schemas.TaskCreate,
    current_user: models.User = Depends(auth.get_current_user), # Dependency to get the authenticated user
    db: Session = Depends(get_db)
):
    """
    Creates a new task associated with the current authenticated user.
    Requires a valid JWT token.
    - **title**: The title of the task.
    - **description**: Optional description of the task.
    - **completed**: Optional, defaults to false.
    """
    # Pass the current_user's ID to the CRUD function
    return crud.create_task(db=db, task=task, user_id=current_user.id)

@app.get("/get_tasks/", response_model=list[schemas.Task], summary="Get all tasks for the current user (secured)")
def get_all_tasks_for_current_user(
    current_user: models.User = Depends(auth.get_current_user), # Dependency to get the authenticated user
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of all tasks for the current authenticated user.
    Requires a valid JWT token.
    Supports pagination with `skip` and `limit` query parameters.
    """
    # Filter tasks by the current_user's ID
    tasks = crud.get_tasks(db, user_id=current_user.id, skip=skip, limit=limit)
    return tasks

@app.get("/tasks/{task_id}", response_model=schemas.Task, summary="Get a specific task by ID (secured)")
def get_task_by_id(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_user), # Secure this endpoint
    db: Session = Depends(get_db)
):
    """
    Retrieves a single task by its ID, ensuring it belongs to the current user.
    Requires a valid JWT token.
    """
    # Fetch task by ID and user_id to ensure ownership
    db_task = crud.get_task(db, task_id=task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found or you do not have permission to access it")
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.Task, summary="Update a task by ID (secured)")
def update_task_by_id(
    task_id: int,
    task_update: schemas.TaskCreate,
    current_user: models.User = Depends(auth.get_current_user), # Secure this endpoint
    db: Session = Depends(get_db)
):
    """
    Updates an existing task, ensuring it belongs to the current user.
    Requires a valid JWT token.
    - **task_id**: The ID of the task to update.
    - **title**: New title (optional).
    - **description**: New description (optional).
    - **completed**: New completion status (optional).
    """
    # Update task by ID and user_id to ensure ownership
    db_task = crud.update_task(db, task_id, current_user.id, task_update)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found or you do not have permission to update it")
    return db_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task by ID (secured)")
def delete_task_by_id(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_user), # Secure this endpoint
    db: Session = Depends(get_db)
):
    """
    Deletes a task by its ID, ensuring it belongs to the current user.
    Requires a valid JWT token.
    """
    # Delete task by ID and user_id to ensure ownership
    db_task = crud.delete_task(db, task_id, current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found or you do not have permission to delete it")
    return # Return no content for 204 status
