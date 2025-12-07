from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any

@dataclass
class User:
    email: str
    full_name: str
    id: Optional[int] = None
    password_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Account:
    user_id: int
    name: str
    id: Optional[int] = None
    balance: float = 0.0
    currency: str = 'RUB'
    last_updated: Optional[datetime] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "balance": self.balance,
            "currency": self.currency,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }

@dataclass
class Transaction:
    user_id: int
    amount: float
    type: str
    category: str
    description: str
    date: date
    id: Optional[int] = None
    account_id: Optional[int] = None
    is_manual: bool = False
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_id": self.account_id,
            "amount": self.amount,
            "type": self.type,
            "category": self.category,
            "description": self.description,
            "date": self.date.isoformat(),
            "is_manual": self.is_manual
        }

@dataclass
class FinancialGoal:
    user_id: int
    name: str
    target_amount: float
    id: Optional[int] = None
    current_amount: float = 0.0
    deadline: Optional[date] = None
    priority: str = "medium"
    created_at: Optional[datetime] = None
    
    @property
    def amount_left(self):
        return max(0, self.target_amount - self.current_amount)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "amount_left": self.amount_left,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
