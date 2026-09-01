# CashLy Architecture Overview

The CashLy application is structured as a modular monorepo with a React + Vite frontend, a Python FastAPI backend, and a Python AI service.

```text
                    ┌─────────────────┐
                    │  React + Vite   │
                    │    Frontend     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ FastAPI Backend │
                    │  /api routes    │
                    └───────┬─────────┘
                            │
                ┌───────────┴────────────┐
                ▼                        ▼
        ┌───────────────┐        ┌──────────────────┐
        │  Business     │        │  Python AI       │
        │  Logic / Auth │        │  Service         │
        │  + Analytics  │        │  Forecasting     │
        └───────┬───────┘        └────────┬─────────┘
                │                         │
                │                ┌────────▼────────┐
                │                │  Categorization │
                │                │  + Anomaly      │
                │                │  detection      │
                │                └─────────────────┘
                │
                ▼
        ┌────────────────────┐
        │ PostgreSQL-ready    │
        │ data layer / storage│
        └────────────────────┘
```

## Frontend responsibilities

- Landing page and app shell
- Authentication screens and user flow
- Dashboard and analytics panels
- Expense overview and budget visualizations
- AI-powered recommendations display
- Responsive experience for mobile and desktop

## Backend responsibilities

- JWT auth and protected routes
- Expense CRUD and validation
- Budget, goal, and insight APIs
- Dashboard aggregation for summary cards
- AI service orchestration and fallback logic
- User-specific business logic for financial planning

## AI service responsibilities

- Merchant/category classification
- Forecasting from historical values
- Anomaly detection using pattern-based rules
- Deterministic fallback logic when no external model is configured
- Receipt and OCR-ready future integrations

## Current implementation status

- React frontend has a dashboard landing page connected to the backend
- FastAPI app exposes health, summary, dashboard, auth, expenses, budgets, goals, insights, and AI assistant routes
- AI service contains rule-based categorization and forecasting endpoints
- Docker and devcontainer setup is aligned with the final Python + React architecture
