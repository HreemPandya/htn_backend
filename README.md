# HTN Backend

A **FastAPI-based backend** with authentication and **role-based access control** for managing users, scans, and connections. Info on the endpoints and how to use them (which ones are protected etc. are at the end)

- To use the endpoints, simply click on them, click "Try it out", enter the needed info (if any) and then click Execute.


## 🚀 Setup Guide

### 1️⃣ Prerequisites

Ensure you have the following installed:

- **Docker & Docker Compose** (for PostgreSQL)
- **Python 3.9+**
- **pip** (Python package manager)
- **Git** (to clone the repo)

---

### 2️⃣ Installation Steps

#### **Step 1: Clone the Repository**
```powershell
git clone https://github.com/HreemPandya/htn_backend.git
cd htn_backend
```

#### **Step 2: Create and Activate Virtual Environment**
```powershell
python -m venv venv
venv\Scripts\activate
```

#### **Step 3: Install Dependencies**
```powershell
pip install -r requirements.txt
```
---

### 3️⃣ Run PostgreSQL Database Using Docker

#### **Start PostgreSQL using Docker**
```powershell
docker compose up -d
```
Note: Ensure Docker is running before executing the above command.

---

### 4️⃣ Create Database Tables

#### **Enter the PostgreSQL Database**
```powershell
docker exec -it htnb-db psql -U admin -d hackathon
```

#### **Run SQL Commands to Create Tables**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50) NOT NULL,
    badge_code VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE scans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_name VARCHAR(255) NOT NULL,
    activity_category VARCHAR(255) NOT NULL,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE connections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    connected_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

```

#### **Exit PostgreSQL**
```sql
\q
```
---

### 5️⃣ Load Users from users.json

Now that the database is set up, load the initial user data:

```powershell
python -m backend.load_data
```
---

### 6️⃣ Run the API Server
```powershell
uvicorn backend.main:app --reload
```
This will start the API server

---

### 🔒 Authentication & Admin Role
- The first user manually added to users.json will be the admin.
- To authenticate, log in using the /login endpoint and retrieve a JWT token.
- This token must be used to access protected admin endpoints.

### 7️⃣ API Endpoints 

#### **🔐 Authentication**

Login (Obtain Token)
- Endpoint: POST /login
- Request Body:
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

Response:
```json
{
  "access_token": "your-jwt-token",
  "token_type": "bearer"
}
```

#### How to Use the Token:
- Copy the JWT Token from the /login response.
- Click Authorize in Swagger UI.
- Paste the token and authenticate.

### 🔄 Restarting the Database & Importing Users

To reset the database and reload users from users.json, follow these steps:

#### **Step 1: Enter PostgreSQL**
```powershell
docker exec -it htnb-db psql -U admin -d hackathon
```

#### **Step 2: Truncate Tables**
```sql
TRUNCATE scans, users RESTART IDENTITY CASCADE;
TRUNCATE connections RESTART IDENTITY CASCADE;
```

#### **Step 3: Exit PostgreSQL**
```sql
\q
```

#### **Step 4: Reload Users**
```powershell
python -m backend.load_data
```

#### **Step 5: Restart the API Server**
```powershell
uvicorn backend.main:app --reload
```

### 👤 User Management

#### 🗑️ Delete a User (Admin Only)
- Endpoint: DELETE /users/{user_id}
- Description: Removes the user from the database and updates users.json.
- Authorization: Requires Admin Token.

#### ⭐ Promote a User to Admin (Admin Only)
- Endpoint: POST /users/{user_id}/promote
- Description: Upgrades a normal user to admin.
- Authorization: Requires Admin Token.

### 📂 Protected Routes (For Logged-in Users)

Any logged-in user can access this:

#### 🔄 Protected Route (Miscallenous Info that you SHOULD only see when logged in)
- Endpoint: GET /protected
- Authorization: Requires JWT Token.
