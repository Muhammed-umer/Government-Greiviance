# How to Run: Tamil Nadu Government Grievance Portal

Step-by-step instructions to run the Tamil Nadu Government Grievance Portal on your system.

---

## Option 1: Docker Compose (Recommended)

This runs PostgreSQL (with PostGIS & pgvector), Redis, MinIO, FastAPI Backend, Celery Worker, and Next.js Web App together.

### Step 1: Create Environment File
```powershell
Copy-Item .env.example .env
```

### Step 2: Build & Start All Services
```powershell
docker compose -f infra/docker-compose.yml up --build
```

### Step 3: Run Database Migrations & Seed Demo Data (In a new terminal)
```powershell
# Apply database schema migrations
docker exec -it tn_grievance_api alembic -c services/api/alembic.ini upgrade head

# Seed TN departments, categories, and sample petitions
docker exec -it tn_grievance_api python -m services.api.src.seed.seed_data
```

---

## Option 2: Running Local Development Servers (Without Docker)

### 1. Backend API (FastAPI)

```powershell
# Install Python dependencies (if not already installed)
python -m pip install -r services/api/requirements.txt

# Run DB Seeder (using SQLite or local PostgreSQL)
python -m services.api.src.seed.seed_data

# Start FastAPI server
python -m uvicorn services.api.src.main:app --reload --port 8000
```

- **Backend API URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

### 2. Frontend Web App (Next.js)

```powershell
# Navigate to web application directory
Set-Location apps/web

# Install dependencies (if not already done)
npm install

# Start Next.js development server
npm run dev
```

- **Frontend Web App URL**: `http://localhost:3000`

---

## Running Automated Test Suites

```powershell
# Run Backend Pytest Suite
python -m pytest services/api/tests

# Run Frontend Vitest Suite
Set-Location apps/web; npx vitest run
```

---

## URLs Reference

| Service | Local URL | Description |
| :--- | :--- | :--- |
| **Web Portal** | [http://localhost:3000](http://localhost:3000) | Citizen Filing, Officer Queue, Admin Analytics |
| **FastAPI Backend** | [http://localhost:8000](http://localhost:8000) | REST API & Health check |
| **Swagger API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive API documentation |
