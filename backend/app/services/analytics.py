from datetime import datetime, timezone


def build_summary():
    return {
        "totalSpending": 24680,
        "averageDaily": 820,
        "remainingBudget": 13200,
        "savingsProgress": 15200,
        "financialHealthScore": 78,
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def list_expenses():
    return [
        {
            "id": "exp-1001",
            "title": "Groceries",
            "category": "Food",
            "amount": 2200,
            "date": "2026-09-01",
            "source": "manual",
        },
        {
            "id": "exp-1002",
            "title": "Metro card reload",
            "category": "Transport",
            "amount": 780,
            "date": "2026-08-30",
            "source": "ocr",
        },
        {
            "id": "exp-1003",
            "title": "Utility bill",
            "category": "Bills",
            "amount": 1800,
            "date": "2026-08-29",
            "source": "manual",
        },
    ]


def list_budgets():
    return [
        {"category": "Food", "limit": 9000, "spent": 6200, "currency": "INR"},
        {"category": "Transport", "limit": 4000, "spent": 2300, "currency": "INR"},
        {"category": "Shopping", "limit": 7000, "spent": 5700, "currency": "INR"},
    ]


def list_goals():
    return [
        {"name": "Emergency fund", "target_amount": 120000, "saved_amount": 72000, "deadline": "2027-03-31"},
        {"name": "Vacation", "target_amount": 60000, "saved_amount": 26000, "deadline": "2026-12-15"},
    ]


def list_insights():
    return [
        {
            "title": "Food spending trending upward",
            "description": "Your dining and groceries costs are 18% above your typical monthly average.",
            "severity": "medium",
        },
        {
            "title": "Savings pace is healthy",
            "description": "You are on track to hit your emergency fund target with a 12% surplus this month.",
            "severity": "low",
        },
        {
            "title": "Budget warning",
            "description": "Shopping is consuming 81% of its budget and may overshoot before month end.",
            "severity": "high",
        },
    ]
