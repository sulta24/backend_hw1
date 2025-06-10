# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
# Copy only requirements.txt first to leverage Docker's caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application directory into the container at /app/app
COPY ./app /app/app

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run uvicorn when the container launches
# --host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
