# Deployment & Operational Guide

## 1. Prerequisites

- Python 3.11+ (Python 3.13 recommended)
- Node.js 18+ (Node 20+ recommended)
- Docker & Docker Compose (optional for containerized deployment)
- Supabase account (or local PostgreSQL / SQLite)

---

## 2. Environment Variables Setup

Create a `.env` file in the project root:

```ini
# Database Connection (Leave empty to use local SQLite fallback)
DATABASE_URL=postgresql://postgres.yourproject:yourpassword@aws-0-region.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-role-key

# JWT Security
JWT_SECRET_KEY=enterprise-fraudshield-ai-key-secret-2024
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Server Binding
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000
STREAMLIT_PORT=8501
```

---

## 3. Deployment Options

### Option A: Direct Local Execution (Recommended for Dev/Testing)
FraudShield AI includes a single master startup CLI (`run.py`):

```powershell
# 1. Run all services concurrently (Frontend on 3000, Backend API on 8000, Streamlit on 8501):
python run.py --platform

# 2. Or run only the modern React Frontend and FastAPI Backend:
python run.py --all

# 3. Or launch individual components:
python run.py --frontend    # React Vite app on http://localhost:3000
python run.py --api         # FastAPI backend on http://localhost:8000
python run.py --dashboard   # Streamlit research console on http://localhost:8501
python run.py --test        # Execute pytest test suite
```

### Option B: Docker Compose Multi-Container Orchestration
```bash
# Build and launch all containerized microservices:
docker-compose -f deployment/docker-compose.yml up --build
```
This launches:
- `frontend`: Multi-stage Nginx container serving React SPA on port `3000`.
- `api`: FastAPI backend container on port `8000`.
- `research-console`: Streamlit research dashboard on port `8501`.

---

## 4. Supabase Database Migration

To run migrations against your Supabase instance:
```powershell
# 1. Execute SQL migrations in Supabase SQL editor or run the migration CLI:
python database/migrate_to_supabase.py
```
The CLI verifies row counts across all 20+ tables and outputs a detailed validation report.
