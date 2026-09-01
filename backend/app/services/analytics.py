from datetime import datetime, timedelta, timezone
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.database import Expense, Budget, Goal


def build_summary(user_id: str, db: Session) -> dict:
    """Build financial summary for a user"""
    # Get current month's expenses
    today = datetime.today()
    month_start = today.replace(day=1)
    
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= month_start.strftime("%Y-%m-%d")
    ).all()
    
    total_spending = sum(exp.amount for exp in expenses)
    
    # Calculate average daily
    days_in_month = (today - month_start).days + 1
    average_daily = total_spending / days_in_month if days_in_month > 0 else 0
    
    # Get budgets for this month
    current_month = today.strftime("%Y-%m")
    budgets = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.month == current_month
    ).all()
    
    total_budget = sum(b.limit for b in budgets)
    remaining_budget = total_budget - total_spending
    
    # Get goals progress
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    savings_progress = sum(g.saved_amount for g in goals)
    
    # Calculate financial health score (0-100)
    # Based on budget adherence, savings progress, etc
    health_score = 50  # baseline
    
    if total_budget > 0:
        budget_ratio = total_spending / total_budget
        if budget_ratio <= 0.7:
            health_score += 30
        elif budget_ratio <= 1.0:
            health_score += 15
        elif budget_ratio <= 1.2:
            health_score -= 10
        else:
            health_score -= 25
    
    if goals:
        total_target = sum(g.target_amount for g in goals)
        if total_target > 0:
            savings_ratio = savings_progress / total_target
            if savings_ratio >= 0.5:
                health_score += 15
            elif savings_ratio >= 0.25:
                health_score += 5
    
    health_score = max(0, min(100, health_score))
    
    return {
        "totalSpending": round(total_spending, 2),
        "averageDaily": round(average_daily, 2),
        "remainingBudget": round(remaining_budget, 2),
        "savingsProgress": round(savings_progress, 2),
        "financialHealthScore": round(health_score),
        "lastUpdated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def list_expenses(user_id: str, db: Session, limit: int = 10) -> list:
    """Get recent expenses for a user"""
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id
    ).order_by(Expense.date.desc()).limit(limit).all()
    
    return [
        {
            "id": exp.id,
            "title": exp.title,
            "category": exp.category,
            "amount": exp.amount,
            "date": exp.date,
            "source": exp.source,
        }
        for exp in expenses
    ]


def list_budgets(user_id: str, db: Session) -> list:
    """Get budgets with spending for a user"""
    today = datetime.today()
    current_month = today.strftime("%Y-%m")
    
    budgets = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.month == current_month
    ).all()
    
    result = []
    for budget in budgets:
        # Calculate spent for this category this month
        month_start = f"{current_month}-01"
        spent_expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.category == budget.category,
            Expense.date >= month_start
        ).all()
        spent = sum(exp.amount for exp in spent_expenses)
        
        result.append({
            "category": budget.category,
            "limit": budget.limit,
            "spent": spent,
            "currency": "INR",
        })
    
    return result


def list_goals(user_id: str, db: Session) -> list:
    """Get financial goals for a user"""
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    
    return [
        {
            "name": goal.name,
            "target_amount": goal.target_amount,
            "saved_amount": goal.saved_amount,
            "deadline": goal.deadline,
        }
        for goal in goals
    ]


def list_insights(user_id: str, db: Session) -> list:
    """Generate insights for a user"""
    today = datetime.today()
    month_start = today.replace(day=1)
    
    # Get this month's expenses
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= month_start.strftime("%Y-%m-%d")
    ).all()
    
    if not expenses:
        return []
    
    # Categorize spending
    category_totals = defaultdict(float)
    for exp in expenses:
        category_totals[exp.category] += exp.amount
    
    insights = []
    
    # Find top spending category
    if category_totals:
        top_category = max(category_totals.items(), key=lambda x: x[1])
        insights.append({
            "title": f"Highest spending category: {top_category[0]}",
            "description": f"You spent ₹{top_category[1]:.0f} on {top_category[0]} this month.",
            "severity": "low",
        })
    
    # Check budget overages
    current_month = today.strftime("%Y-%m")
    budgets = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.month == current_month
    ).all()
    
    for budget in budgets:
        spent = category_totals.get(budget.category, 0)
        ratio = spent / budget.limit if budget.limit > 0 else 0
        
        if ratio > 1.0:
            insights.append({
                "title": f"Budget alert: {budget.category} exceeded",
                "description": f"You've spent ₹{spent:.0f} out of ₹{budget.limit:.0f} for {budget.category}.",
                "severity": "high",
            })
        elif ratio > 0.8:
            insights.append({
                "title": f"Approaching budget limit for {budget.category}",
                "description": f"You've spent {int(ratio*100)}% of your {budget.category} budget.",
                "severity": "medium",
            })
    
    # Check goals progress
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    for goal in goals:
        if goal.target_amount > 0:
            progress = (goal.saved_amount / goal.target_amount) * 100
            if progress >= 100:
                insights.append({
                    "title": f"Goal achieved: {goal.name}",
                    "description": f"You've reached your {goal.name} target of ₹{goal.target_amount:.0f}!",
                    "severity": "low",
                })
            elif progress >= 75:
                insights.append({
                    "title": f"Goal almost reached: {goal.name}",
                    "description": f"You're {int(progress)}% towards your {goal.name} goal.",
                    "severity": "low",
                })
    
    return insights

