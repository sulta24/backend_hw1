# 📝 Todo List Application

A simple, full-stack Todo List application built with **FastAPI**, **PostgreSQL**, and **Docker**, showcasing backend principles such as CRUD operations, JWT-based user authentication, and CI/CD pipelines.

---

## 🚀 Features

### 🔐 User Management:
- ✅ User registration
- ✅ JWT login authentication
- ✅ Protected API endpoints
- ✅ User-specific tasks

### 📋 Task Management (CRUD):
- 🆕 Create tasks
- 🔍 View tasks
- ✏️ Update task details
- 🗑️ Delete tasks

### 🗄️ Database:
- PostgreSQL for persistence
- SQLAlchemy ORM

### 🐳 Containerization:
- Dockerfile for FastAPI backend
- Docker Compose for backend + database

### ⚙️ CI/CD:
- GitHub Actions workflow for Docker image build on push

### 🌐 Frontend:
- Vanilla HTML + JS interface to interact with the backend

---

## 🛠️ Technologies Used

**Backend**:
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- python-jose, passlib
- Uvicorn

**Frontend**:
- HTML
- CSS
- JavaScript

**DevOps**:
- Docker, Docker Compose
- GitHub Actions

---

## 🚀 Getting Started

### ✅ Prerequisites

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (or Docker + Docker Compose on Linux)

---

### 📦 Installation

```bash
git clone https://github.com/your-username/your-todo-app.git  # 🔁 Replace with your repository
cd your-todo-app
Then, to build and run the application:


docker-compose up --build
⚠️ Important: Reset the DB (if needed)
If schema errors occur (like missing columns), clean old volumes:


docker-compose down -v  # ⚠️ This deletes ALL data!
docker-compose up --build
👨‍💻 Usage
🌐 Access the Frontend:
Open frontend/index.html in your browser.

Example:
file:///your/path/to/frontend/index.html

👥 Register / Login
Register with a new username and password.

Login with those credentials.

The app section will appear showing "Logged in as: [username]".

✅ Manage Tasks
Create Task: Fill out title/description and click "Add Task".

View Tasks: All tasks for the user are listed.

Toggle Completion: Click button to mark as complete/incomplete.

Delete Task: Click "Delete" → Confirm in browser dialog.

🔓 Logout
Click the Logout button to clear the session and return to login screen.

📂 Project Structure

.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app
│   │   ├── database.py       # DB setup
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic models
│   │   ├── crud.py           # CRUD logic
│   │   └── auth.py           # Auth logic
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   └── script.js
├── .github/
│   └── workflows/
│       └── ci-cd.yml
└── docker-compose.yml
