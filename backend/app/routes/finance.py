from uuid import uuid4

from fastapi import APIRouter

from app.models.schemas import Expense, ExpenseCreate
from app.services.analytics import (
    build_summary,
    list_budgets,
    list_expenses,
    list_goals,
    list_insights,
)

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok", "app": "CashLy backend"}


@router.get("/api/summary")
def summary():
    return build_summary()


@router.get("/api/expenses")
def expenses():
    return {"expenses": list_expenses()}


@router.post("/api/expenses", response_model=Expense)
def create_expense(payload: ExpenseCreate):
    expense_payload = {
        "id": f"exp-{uuid4().hex[:8]}",
        "user_id": "demo-user",
        **payload.model_dump(),
    }
    return Expense(**expense_payload)


@router.get("/api/budgets")
def budgets():
    return {"budgets": list_budgets()}


@router.get("/api/goals")
def goals():
    return {"goals": list_goals()}


@router.get("/api/insights")
def insights():
    return {"insights": list_insights()}


@router.get("/api/dashboard")
def dashboard():
    return {
        "summary": build_summary(),
        "expenses": list_expenses(),
        "budgets": list_budgets(),
        "goals": list_goals(),
        "insights": list_insights(),
    }


@router.get("/api/assistant")
def assistant():
    return {
        "advice": "Your shopping spending is the largest risk to your monthly plan. Consider reducing discretionary purchases by 12% to stay under budget.",
        "recommendations": [
            "Pause non-essential subscriptions for 30 days.",
            "Set a higher grocery cap to avoid impulse spending.",
            "Move 10% of your income to your emergency fund this month.",
        ],
    }


@router.get("/api/health-check")
def legacy_health_check():
    return health_check()
