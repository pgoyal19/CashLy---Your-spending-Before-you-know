from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database import Expense, Budget, Goal
from app.models.schemas import Expense as ExpenseSchema, ExpenseCreate, Budget as BudgetSchema, Goal as GoalSchema
from app.services.analytics import (
    build_summary,
    list_budgets,
    list_expenses,
    list_goals,
    list_insights,
)
from app.services.auth import decode_token, get_user_by_id

router = APIRouter()


def get_user_id_from_token(authorization: str | None = Header(None)) -> str:
    """Extract user_id from JWT token in Authorization header"""
    if not authorization:
        # For demo purposes, use a default user if no auth provided
        return "demo-user"
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/health")
def health_check():
    return {"status": "ok", "app": "CashLy backend"}


@router.get("/api/summary")
def summary(user_id: str = Depends(get_user_id_from_token), db: Session = Depends(get_db)):
    return build_summary(user_id, db)


@router.get("/api/expenses")
def expenses(user_id: str = Depends(get_user_id_from_token), db: Session = Depends(get_db)):
    return {"expenses": list_expenses(user_id, db)}


@router.post("/api/expenses", response_model=ExpenseSchema)
def create_expense(
    payload: ExpenseCreate,
    user_id: str = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    expense = Expense(
        id=f"exp-{uuid4().hex[:8]}",
        user_id=user_id,
        title=payload.title,
        category=payload.category,
        amount=payload.amount,
        date=payload.date,
        source=payload.source,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    return ExpenseSchema(
        id=expense.id,
        user_id=expense.user_id,
        title=expense.title,
        category=expense.category,
        amount=expense.amount,
        date=expense.date,
        source=expense.source,
    )


@router.get("/api/budgets")
def budgets(user_id: str = Depends(get_user_id_from_token), db: Session = Depends(get_db)):
    return {"budgets": list_budgets(user_id, db)}


@router.post("/api/budgets")
def create_budget(
    payload: dict,
    user_id: str = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    """Create a budget for a category and month"""
    from datetime import datetime
    
    category = payload.get("category")
    limit = payload.get("limit")
    month = payload.get("month", datetime.today().strftime("%Y-%m"))
    
    if not category or not limit:
        raise HTTPException(status_code=400, detail="Missing category or limit")
    
    # Check if budget exists for this category/month
    existing = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category == category,
        Budget.month == month,
    ).first()
    
    if existing:
        existing.limit = limit
    else:
        budget = Budget(
            id=f"bud-{uuid4().hex[:8]}",
            user_id=user_id,
            category=category,
            limit=limit,
            month=month,
        )
        db.add(budget)
    
    db.commit()
    return {"status": "ok", "budget": {"category": category, "limit": limit, "month": month}}


@router.get("/api/goals")
def goals(user_id: str = Depends(get_user_id_from_token), db: Session = Depends(get_db)):
    return {"goals": list_goals(user_id, db)}


@router.post("/api/goals")
def create_goal(
    payload: dict,
    user_id: str = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    """Create a financial goal"""
    name = payload.get("name")
    target_amount = payload.get("target_amount")
    deadline = payload.get("deadline")
    
    if not name or not target_amount or not deadline:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    goal = Goal(
        id=f"goal-{uuid4().hex[:8]}",
        user_id=user_id,
        name=name,
        target_amount=target_amount,
        saved_amount=0,
        deadline=deadline,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    return GoalSchema(
        name=goal.name,
        target_amount=goal.target_amount,
        saved_amount=goal.saved_amount,
        deadline=goal.deadline,
    )


@router.put("/api/goals/{goal_id}")
def update_goal(
    goal_id: str,
    payload: dict,
    user_id: str = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    """Update goal saved amount"""
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if "saved_amount" in payload:
        goal.saved_amount = payload["saved_amount"]
    
    db.commit()
    return {"status": "ok", "goal": {"name": goal.name, "saved_amount": goal.saved_amount}}


@router.get("/api/insights")
def insights(user_id: str = Depends(get_user_id_from_token), db: Session = Depends(get_db)):
    return {"insights": list_insights(user_id, db)}


@router.get("/api/dashboard")
def dashboard(user_id: str = Depends(get_user_id_from_token), db: Session = Depends(get_db)):
    return {
        "summary": build_summary(user_id, db),
        "expenses": list_expenses(user_id, db),
        "budgets": list_budgets(user_id, db),
        "goals": list_goals(user_id, db),
        "insights": list_insights(user_id, db),
    }


@router.get("/api/assistant")
def assistant(user_id: str = Depends(get_user_id_from_token), db: Session = Depends(get_db)):
    """AI-powered financial assistant"""
    insights_list = list_insights(user_id, db)
    
    # Generate advice based on insights
    recommendations = []
    
    if insights_list:
        for insight in insights_list:
            if "exceeded" in insight["title"].lower():
                category = insight["title"].replace("Budget alert: ", "").replace(" exceeded", "")
                recommendations.append(f"Reduce spending on {category} to stay within budget.")
            elif "approaching" in insight["title"].lower():
                category = insight["title"].split("for ")[-1]
                recommendations.append(f"Be careful with {category} spending as it's approaching your budget limit.")
    
    # Add general recommendations
    if not recommendations:
        recommendations.append("Keep tracking your expenses to build good financial habits.")
        recommendations.append("Set up budgets for each category to better manage your spending.")
    
    recommendations.append("Review your spending regularly to identify saving opportunities.")
    
    return {
        "advice": recommendations[0] if recommendations else "Your spending looks good!",
        "recommendations": recommendations[:3],
    }


@router.get("/api/health-check")
def legacy_health_check():
    return health_check()

