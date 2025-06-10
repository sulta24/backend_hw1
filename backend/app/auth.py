from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

# Secret key to sign the JWT token.
# !!! IMPORTANT: In a real application, load this from environment variables (e.g., using python-dotenv or Docker secrets).
SECRET_KEY = "super-secret-jwt-key-change-this-in-production" # Replace with a strong, random key!
ALGORITHM = "HS256" # Hashing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token expiration time

# Cryptography context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer is a FastAPI utility to extract tokens from headers.
# 'tokenUrl' points to the endpoint where clients can obtain a token (e.g., '/token').
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    # Verify a plain password against a hashed one
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    # Hash a plain password
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # Create a JWT access token
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # Add expiration time to the payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Encode the token
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Dependency to get the current authenticated user from a JWT token.
    # If authentication fails, it raises an HTTPException.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # 'sub' claim usually contains the subject (username here)
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username) # Validate the username
    except JWTError:
        raise credentials_exception # Raise exception if token is invalid or expired

    # Fetch the user from the database
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception # Raise exception if user not found

    return user # Return the authenticated user object