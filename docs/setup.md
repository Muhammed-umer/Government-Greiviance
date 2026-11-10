# Setup & Deployment Guide: Tamil Nadu Government Grievance Portal

## Quickstart with Docker Compose

To start the full stack (Postgres + PostGIS + pgvector, Redis, MinIO, FastAPI Backend, Celery Worker, Next.js Web App):

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Launch all services via Docker Compose
docker compose -f infra/docker-compose.yml up --build -d

# 3. Apply database migrations
docker exec -it tn_grievance_api alembic -c services/api/alembic.ini upgrade head

# 4. Seed demo data (Departments, Categories, Mock Tickets)
docker exec -it tn_grievance_api python -m services.api.src.seed.seed_data
```

---

## Local Development Mode (Without Docker)

### Backend Service (`services/api`)
```bash
# Install dependencies
pip install -r services/api/requirements.txt

# Run migrations
alembic -c services/api/alembic.ini upgrade head

# Run DB Seeder
python -m services.api.src.seed.seed_data

# Start FastAPI server
uvicorn services.api.src.main:app --reload --port 8000
```

### Frontend Application (`apps/web`)
```bash
cd apps/web
npm install
npm run dev
```

---

## Testing Commands

### Backend Pytest Suite
```bash
pytest services/api/tests
```

### Frontend Vitest Suite
```bash
cd apps/web
npm run test
```
