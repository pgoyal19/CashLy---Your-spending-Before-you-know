# CashLy – Your Spending Before You Know

CashLy is an AI-powered personal finance application designed to help users understand spending habits, forecast upcoming costs, and keep their financial goals on track before problems appear.

## Features

- Secure user authentication flow
- Expense tracking and category-based summaries
- Budget visibility and goal progress tracking
- Spending insights and anomaly detection
- AI-powered financial assistant interface
- OCR-ready receipt intake workflow
- Responsive dashboard built for desktop and mobile

## Stack

- Frontend: React + Vite
- Backend: Python + FastAPI
- AI service: Python + FastAPI
- Database: PostgreSQL-ready for future integration

## Quick start

```bash
cp .env.example .env
cd frontend && npm install
cd ../backend && python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run locally

```bash
# Terminal 1 - backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - frontend
cd frontend
npm run dev
```

### AI service

```bash
cd ai-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker

```bash
docker compose up --build
```

## Project status

The project has been aligned to the requested stack: a Python FastAPI backend and a React + Vite frontend. The current build includes a CashLy landing page, real API endpoints, and a dashboard summary flow that connects to the backend.
