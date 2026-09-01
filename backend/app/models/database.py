from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD format
    source = Column(String(50), default="manual")  # manual, ocr, etc
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    user = relationship("User", back_populates="expenses")


class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)
    limit = Column(Float, nullable=False)
    month = Column(String, nullable=False)  # YYYY-MM format
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    user = relationship("User", back_populates="budgets")


class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    target_amount = Column(Float, nullable=False)
    saved_amount = Column(Float, default=0)
    deadline = Column(String, nullable=False)  # YYYY-MM-DD format
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    user = relationship("User", back_populates="goals")
