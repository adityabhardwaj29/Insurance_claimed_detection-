# 🚀 Production Deployment & Go-Live Guide

This document provides a step-by-step walkthrough to deploy the **FraudShield Enterprise Insurance Fraud Intelligence Platform** to the public internet for free or low-cost cloud hosting.

---

## 🏗️ Architecture Overview

The platform consists of three core components:
1. **React Web Frontend (Vite + TypeScript)**: Interactive officer console with route authentication.
2. **FastAPI Backend Gateway (Python 3.12)**: Supervised XGBoost, Isolation Forest anomaly scoring, and SQLite/PostgreSQL data layer.
3. **Streamlit Analytics Console**: Forensic graph visualizer, SHAP breakdown, and SIU triage queues.

---

## 🏆 Recommended Easiest & 100% Free Setup

| Component | Recommended Cloud Host | Free Tier Benefits |
|---|---|---|
| **Frontend** | **Vercel** (`vercel.com`) | Free global CDN, automatic SSL, zero config for Vite |
| **Backend API** | **Render** (`render.com`) | Free Web Service with automated GitHub CD pipeline |
| **Streamlit Console** | **Streamlit Cloud** (`share.streamlit.io`)| Official free hosting for Streamlit Python apps |
| **Database** | **SQLite (Built-in)** or **Supabase** | Zero configuration needed for demo / persistent relational |

---

### Step 1: Deploy Backend API on Render.com

1. Sign up or log in at [render.com](https://render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository: `adityabhardwaj29/Insurance_claimed_detection-`.
4. Configure the service:
   - **Name:** `fraudshield-api`
   - **Region:** Any (e.g. Frankfurt / Singapore / Oregon)
   - **Branch:** `main`
   - **Root Directory:** *(leave blank)*
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. In **Advanced** -> **Environment Variables**, add:
   - `PYTHONPATH`: `.`
   - `JWT_SECRET_KEY`: `your-production-secret-jwt-key`
   - `CORS_ORIGINS`: `*`
6. Click **Deploy Web Service**.
7. Once deployed, copy your API URL: `https://fraudshield-api.onrender.com`.

---

### Step 2: Deploy Frontend on Vercel

1. Sign up or log in at [vercel.com](https://vercel.com/).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository: `Insurance_claimed_detection-`.
4. Configure Project Settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click edit and select `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Expand **Environment Variables** and add:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://fraudshield-api.onrender.com/api` *(your Render API URL with `/api`)*
6. Click **Deploy**.
7. In ~60 seconds, your React web application is live with free HTTPS:
   `https://insurance-claimed-detection.vercel.app`

---

### Step 3: Deploy Streamlit Console on Streamlit Community Cloud

1. Log in at [share.streamlit.io](https://share.streamlit.io/).
2. Click **Create app** -> **I already have an app**.
3. Fill in the repository details:
   - **Repository:** `adityabhardwaj29/Insurance_claimed_detection-`
   - **Branch:** `main`
   - **Main file path:** `dashboard/app.py`
4. Expand **Advanced settings** -> **Python version**: Select `3.11` or `3.12`.
5. Click **Deploy!**
6. Your interactive forensic console is live:
   `https://insurance-fraud-analytics.streamlit.app`

---

## 🏢 Alternative Option: Single VPS Server Deployment (Docker)

If you prefer deploying everything on a single Linux server (AWS EC2, DigitalOcean, or Hetzner):

```bash
# 1. SSH into your Ubuntu 24.04 server
ssh root@your-server-ip

# 2. Install Docker & Git
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

# 3. Clone Repository
git clone https://github.com/adityabhardwaj29/Insurance_claimed_detection-.git
cd Insurance_claimed_detection-

# 4. Launch all 3 services
docker compose up -d --build
```
Your services will be immediately accessible on:
- Frontend: `http://your-server-ip:3000`
- API Swagger Docs: `http://your-server-ip:8000/docs`
- Streamlit Console: `http://your-server-ip:8501`
