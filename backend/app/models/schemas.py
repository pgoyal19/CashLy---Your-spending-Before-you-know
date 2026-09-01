from typing import Literal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., min_length=2, max_length=50)
    amount: float = Field(..., gt=0)
    date: str
    source: str = "manual"


class Expense(ExpenseCreate):
    id: str
    user_id: str = "demo-user"


class Budget(BaseModel):
    category: str
    limit: float
    spent: float
    currency: str = "INR"


class Goal(BaseModel):
    name: str
    target_amount: float
    saved_amount: float
    deadline: str


class Insight(BaseModel):
    title: str
    description: str
    severity: Literal["low", "medium", "high"]
