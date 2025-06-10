from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection URL for PostgreSQL.
# When running locally (without Docker Compose directly linking services), use 'localhost'.
# When running with Docker Compose, 'db' refers to the service name in docker-compose.yml.
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:mysecretpassword@db/postgres"
# If running FastAPI directly on your machine and PostgreSQL on localhost, use:
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost/postgres"

# Create the SQLAlchemy engine.
# The 'echo=True' argument prints SQL statements to the console for debugging.
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Create a SessionLocal class. Each instance of this class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for your SQLAlchemy models.
Base = declarative_base()

# Dependency to get a database session.
# This is used with FastAPI's Depends to inject a database session into route functions.
def get_db():
    db = SessionLocal()
    try:
        yield db  # Provide the database session
    finally:
        db.close() # Ensure the session is closed after the request is finished