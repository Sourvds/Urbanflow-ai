# UrbanFlow AI

[![Live Demo](https://img.shields.io/badge/demo-localhost-00d4ff)](http://localhost:5173)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](http://localhost:8000/docs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

AI-powered Smart City Resource Optimization Platform — production-grade full-stack application with ML forecasting, anomaly detection, optimization engines, and a futuristic command-center UI.

**Repository:** [github.com/Sourvds/Urbanflow-ai](https://github.com/Sourvds/Urbanflow-ai)

## Features

- **JWT Authentication** with role-based access (Admin, City Operator, Analyst)
- **Real-time Dashboard** — electricity, traffic, water, air quality, efficiency scores
- **ML Pipeline** — XGBoost forecasting, Isolation Forest anomalies, K-Means clustering, scipy optimization
- **Interactive City Map** — React Leaflet with zone overlays
- **Modules** — Electricity, Traffic, Water analytics with predictions
- **Alert System** — priority levels, resolve workflow
- **AI Chatbot** — operator assistant for natural language queries
- **Admin Panel** — users, SQL analytics, system health, ML job triggers
- **PostgreSQL** — normalized schema with indexes and analytics queries

## Quick Start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

In another terminal, seed the database:

```bash
docker compose exec backend python scripts/seed_data.py
```

Open **http://localhost:5173**

### Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@urbanflow.ai | UrbanFlow2026! | Admin |
| operator@urbanflow.ai | UrbanFlow2026! | City Operator |
| analyst@urbanflow.ai | UrbanFlow2026! | Analyst |

API docs: **http://localhost:8000/docs**

## Local Development

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
# Start PostgreSQL and set DATABASE_URL in .env
uvicorn app.main:app --reload --port 8000
python scripts/seed_data.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL=http://localhost:8000` in `frontend/.env`

## Deployment

| Service | Target |
|---------|--------|
| Frontend | Vercel (`frontend/`, build: `npm run build`) |
| Backend | Render (Dockerfile in `backend/`) |
| Database | Render PostgreSQL or managed Postgres |

Environment variables: see `.env.example`

## Project Structure

```
SmartCity/
├── backend/          # FastAPI + SQLAlchemy + ML
│   ├── app/
│   │   ├── api/v1/   # REST endpoints
│   │   ├── ml/       # Forecasting, anomaly, optimization
│   │   ├── models/   # PostgreSQL ORM
│   │   └── services/ # Analytics business logic
│   └── scripts/      # Demo data seeder
├── frontend/         # React + Vite + Tailwind
└── docker-compose.yml
```

## Tech Stack

React, Vite, Tailwind CSS, Framer Motion, Recharts, React Leaflet, FastAPI, PostgreSQL, Scikit-learn, XGBoost, Docker

## License

MIT
