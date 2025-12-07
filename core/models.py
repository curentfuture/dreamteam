# models.py
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid

class TransactionType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"

class GoalPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class GoalUrgency(str, Enum):
    LONG_TERM = "long_term"
    MEDIUM_TERM = "medium_term"
    SHORT_TERM = "short_term"
    URGENT = "urgent"

@dataclass
class User:
    """Модель пользователя"""
    id: Optional[int] = None
    email: str
    full_name: str
    password_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            id=data.get('id'),
            email=data['email'],
            full_name=data['full_name'],
            password_hash=data.get('password_hash'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )

@dataclass
class Account:
    """Модель счета"""
    id: Optional[int] = None
    user_id: int
    name: str
    balance: float = 0.0
    currency: str = 'RUB'
    last_updated: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "balance": self.balance,
            "currency": self.currency,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        last_updated = data.get('last_updated')
        if last_updated and isinstance(last_updated, str):
            last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            name=data['name'],
            balance=data.get('balance', 0),
            currency=data.get('currency', 'RUB'),
            last_updated=last_updated
        )

@dataclass
class Transaction:
    """Модель транзакции"""
    id: Optional[int] = None
    user_id: int
    account_id: Optional[int] = None
    amount: float
    type: str
    category: str
    description: str
    date: date
    is_manual: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        trans_date = data['date']
        if isinstance(trans_date, str):
            trans_date = date.fromisoformat(trans_date)
        
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            account_id=data.get('account_id'),
            amount=data['amount'],
            type=data['type'],
            category=data['category'],
            description=data['description'],
            date=trans_date,
            is_manual=bool(data.get('is_manual', False))
        )

@dataclass
class FinancialGoal:
    """Модель финансовой цели"""
    id: Optional[int] = None
    user_id: int
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[date] = None
    priority: str = 'medium'
    created_at: Optional[datetime] = None
    
    @property
    def amount_left(self) -> float:
        return max(0, self.target_amount - self.current_amount)
    
    def to_dict(self) -> Dict[str, Any]:
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FinancialGoal':
        deadline = data.get('deadline')
        if deadline and isinstance(deadline, str):
            deadline = date.fromisoformat(deadline)
        
        created_at = data.get('created_at')
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            name=data['name'],
            target_amount=data['target_amount'],
            current_amount=data.get('current_amount', 0),
            deadline=deadline,
            priority=data.get('priority', 'medium'),
            created_at=created_at
        )

@dataclass
class UserProfile:
    """Профиль пользователя с финансовыми метриками"""
    user_id: int
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0
    average_savings_rate: float = 0.0
    risk_tolerance: float = 0.5
    
    def update_from_transactions(self, transactions: List[Transaction]):
        monthly_data = self._aggregate_monthly(transactions)
        self.monthly_income = monthly_data.get("income", 0)
        self.monthly_expenses = monthly_data.get("expense", 0)
        
        if self.monthly_income > 0:
            self.average_savings_rate = (
                (self.monthly_income - self.monthly_expenses) / self.monthly_income
            )
    
    def _aggregate_monthly(self, transactions: List[Transaction]) -> Dict[str, float]:
        from collections import defaultdict
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_totals = defaultdict(float)
        
        for t in transactions:
            if t.date.year == current_year and t.date.month == current_month:
                monthly_totals[t.type] += t.amount
        
        return monthly_totals

@dataclass
class Recommendation:
    """Рекомендация для пользователя"""
    id: str
    title: str
    description: str
    category: str
    estimated_impact: float
    confidence: float
    actions: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "estimated_impact": self.estimated_impact,
            "confidence": self.confidence,
            "actions": self.actions
        }