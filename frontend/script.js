// Base URL for your FastAPI backend.
// When running with Docker Compose, 'localhost:8000' will map to the 'web' service.
const API_BASE_URL = 'http://localhost:8000';

// Global variable to store the access token
let accessToken = null;
let currentUsername = null;

// DOM elements for messages
const messageBox = document.getElementById('message-box');
const successBox = document.getElementById('success-box');

// Function to display messages
function showMessage(element, message, isError = true) {
    element.textContent = message;
    element.style.display = 'block';
    element.style.backgroundColor = isError ? '#e74c3c' : '#2ecc71';
    setTimeout(() => {
        element.style.display = 'none';
        element.textContent = '';
    }, 5000); // Hide after 5 seconds
}

// Function to show error messages
function showErrorMessage(message) {
    showMessage(messageBox, message, true);
}

// Function to show success messages
function showSuccessMessage(message) {
    showMessage(successBox, message, false);
}

// Function to update UI based on login status
function updateUI() {
    const authSection = document.getElementById('auth-section');
    const appSection = document.getElementById('app-section');
    const userInfo = document.getElementById('user-info');

    if (accessToken) {
        authSection.style.display = 'none';
        appSection.style.display = 'block';
        userInfo.textContent = currentUsername;
        fetchTasks(); // Fetch tasks once logged in
    } else {
        authSection.style.display = 'block';
        appSection.style.display = 'none';
        userInfo.textContent = '';
    }
}

// --- Authentication Functions ---

async function registerUser() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    if (!username || !password) {
        showErrorMessage('Username and password are required for registration.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Registration failed');
        }

        const data = await response.json();
        showSuccessMessage(`User "${data.username}" registered successfully! You can now log in.`);
        console.log('Registration successful:', data);
        // Clear registration fields
        document.getElementById('register-username').value = '';
        document.getElementById('register-password').value = '';

    } catch (error) {
        console.error('Registration error:', error);
        showErrorMessage(`Registration error: ${error.message}`);
    }
}

async function loginUser() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    if (!username || !password) {
        showErrorMessage('Username and password are required for login.');
        return;
    }

    // FastAPI's OAuth2PasswordRequestForm expects data in application/x-www-form-urlencoded
    const formBody = new URLSearchParams();
    formBody.append('username', username);
    formBody.append('password', password);

    try {
        const response = await fetch(`${API_BASE_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formBody.toString(),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Login failed');
        }

        const data = await response.json();
        accessToken = data.access_token;
        currentUsername = username; // Store current username
        localStorage.setItem('access_token', accessToken); // Persist token
        localStorage.setItem('current_username', currentUsername); // Persist username
        showSuccessMessage('Logged in successfully!');
        console.log('Login successful:', data);
        updateUI();
        // Clear login fields
        document.getElementById('login-username').value = '';
        document.getElementById('login-password').value = '';

    } catch (error) {
        console.error('Login error:', error);
        showErrorMessage(`Login error: ${error.message}`);
    }
}

function logoutUser() {
    accessToken = null;
    currentUsername = null;
    localStorage.removeItem('access_token'); // Remove token from storage
    localStorage.removeItem('current_username'); // Remove username from storage
    showSuccessMessage('Logged out successfully!');
    updateUI();
}

// --- Task Management Functions ---

async function fetchTasks() {
    if (!accessToken) {
        showErrorMessage('Please log in to view tasks.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/get_tasks/`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`, // Include JWT token
            },
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch tasks');
        }

        const tasks = await response.json();
        const tasksList = document.getElementById('tasks-list');
        tasksList.innerHTML = ''; // Clear existing tasks

        if (tasks.length === 0) {
            tasksList.innerHTML = '<p>No tasks yet. Create one!</p>';
            return;
        }

        tasks.forEach(task => {
            const taskDiv = document.createElement('div');
            taskDiv.className = `task-item ${task.completed ? 'completed' : ''}`;
            taskDiv.innerHTML = `
                <div class="task-details">
                    <strong>${task.title}</strong>
                    <p>${task.description || 'No description'}</p>
                </div>
                <div class="task-actions">
                    <button onclick="toggleTaskCompletion(${task.id}, ${task.completed})">
                        ${task.completed ? 'Mark as Incomplete' : 'Mark as Complete'}
                    </button>
                    <button onclick="deleteTask(${task.id})">Delete</button>
                </div>
            `;
            tasksList.appendChild(taskDiv);
        });
    } catch (error) {
        console.error('Error fetching tasks:', error);
        showErrorMessage(`Error fetching tasks: ${error.message}`);
        // If error is due to invalid token, force logout
        if (error.message.includes('Could not validate credentials') || error.message.includes('Not authenticated')) {
            logoutUser();
        }
    }
}

async function createTask() {
    if (!accessToken) {
        showErrorMessage('Please log in to create tasks.');
        return;
    }

    const title = document.getElementById('task-title').value;
    const description = document.getElementById('task-description').value;

    if (!title) {
        showErrorMessage('Task title cannot be empty!');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/create_task/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`,
            },
            body: JSON.stringify({ title, description, completed: false }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create task');
        }

        const newTask = await response.json();
        console.log('Task created:', newTask);
        showSuccessMessage('Task created successfully!');
        document.getElementById('task-title').value = '';
        document.getElementById('task-description').value = '';
        fetchTasks(); // Refresh the list
    } catch (error) {
        console.error('Error creating task:', error);
        showErrorMessage(`Error creating task: ${error.message}`);
        if (error.message.includes('Could not validate credentials') || error.message.includes('Not authenticated')) {
            logoutUser();
        }
    }
}

async function toggleTaskCompletion(taskId, currentStatus) {
    if (!accessToken) {
        showErrorMessage('Please log in to update tasks.');
        return;
    }

    try {
        // First, fetch the existing task to get its current title and description
        const fetchResponse = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });
        if (!fetchResponse.ok) {
            const errorData = await fetchResponse.json();
            throw new Error(errorData.detail || 'Failed to fetch task for update');
        }
        const taskToUpdate = await fetchResponse.json();

        const updatedTask = {
            title: taskToUpdate.title, // Keep existing title
            description: taskToUpdate.description, // Keep existing description
            completed: !currentStatus // Toggle the completion status
        };

        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`,
            },
            body: JSON.stringify(updatedTask),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update task');
        }

        console.log('Task updated:', taskId);
        showSuccessMessage('Task updated successfully!');
        fetchTasks(); // Refresh the list
    } catch (error) {
        console.error('Error updating task:', error);
        showErrorMessage(`Error updating task: ${error.message}`);
        if (error.message.includes('Could not validate credentials') || error.message.includes('Not authenticated')) {
            logoutUser();
        }
    }
}

async function deleteTask(taskId) {
    if (!accessToken) {
        showErrorMessage('Please log in to delete tasks.');
        return;
    }

    // Custom confirmation dialog
    const confirmDelete = window.confirm("Are you sure you want to delete this task?");
    if (!confirmDelete) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete task');
        }

        console.log('Task deleted:', taskId);
        showSuccessMessage('Task deleted successfully!');
        fetchTasks(); // Refresh the list
    } catch (error) {
        console.error('Error deleting task:', error);
        showErrorMessage(`Error deleting task: ${error.message}`);
        if (error.message.includes('Could not validate credentials') || error.message.includes('Not authenticated')) {
            logoutUser();
        }
    }
}

// Initial check when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Attempt to retrieve token and username from localStorage
    accessToken = localStorage.getItem('access_token');
    currentUsername = localStorage.getItem('current_username');
    updateUI(); // Update UI based on token presence
});

