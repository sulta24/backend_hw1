from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship # Import relationship for defining relationships
from .database import Base

# SQLAlchemy model for the 'users' table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) # Primary key, auto-incrementing
    username = Column(String, unique=True, index=True) # Unique username, indexed for quick lookups
    hashed_password = Column(String) # Stores the hashed password

    # Define a relationship with the Task model.
    # This allows you to access tasks related to a user (e.g., user.tasks).
    tasks = relationship("Task", back_populates="owner")

# SQLAlchemy model for the 'tasks' table
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True) # Primary key, auto-incrementing
    title = Column(String, index=True) # Task title, indexed
    description = Column(String, nullable=True) # Optional description
    completed = Column(Boolean, default=False) # Completion status, defaults to False
    user_id = Column(Integer, ForeignKey("users.id")) # Foreign key linking to the users table

    # Define a relationship with the User model.
    # This allows you to access the owner of a task (e.g., task.owner).
    owner = relationship("User", back_populates="tasks")