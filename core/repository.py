from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from .database import Database
from .models import Transaction, FinancialGoal, User, Account
import random

class Repository:
    """Репозиторий для работы с базой данных"""
    
    def __init__(self, db: Database):
        self.db = db
    
    # ========== ПОЛЬЗОВАТЕЛИ ==========
    
    def create_user(self, email: str, full_name: str, password_hash: str = None) -> Optional[User]:
        query = """
            INSERT INTO users (email, full_name, password_hash)
            VALUES (?, ?, ?)
        """
        # Вставляем пользователя
        self.db.execute_query(query, (email, full_name, password_hash))
        
        # Получаем созданного пользователя
        query = "SELECT id, email, full_name, created_at FROM users WHERE email = ?"
        result = self.db.execute_query(query, (email,))
        
        if result and len(result) > 0:
            return User(
                email=email,
                full_name=full_name,
                id=result[0][0],
                password_hash=password_hash,
                created_at=datetime.fromisoformat(result[0][3]) if result[0][3] else None
            )
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        query = "SELECT id, email, full_name, password_hash, created_at FROM users WHERE email = ?"
        result = self.db.execute_query(query, (email,))
        
        if result and len(result) > 0:
            return User(
                email=result[0][1],
                full_name=result[0][2],
                id=result[0][0],
                password_hash=result[0][3],
                created_at=datetime.fromisoformat(result[0][4]) if result[0][4] else None
            )
        return None
    
    # ========== СЧЕТА ==========
    
    def create_account(self, user_id: int, name: str, balance: float = 0) -> bool:
        query = """
            INSERT INTO accounts (user_id, name, balance, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        self.db.execute_query(query, (user_id, name, balance))
        return True
    
    # ========== ТРАНЗАКЦИИ ==========
    
    def create_transaction(self, transaction: Transaction) -> bool:
        query = """
            INSERT INTO transactions 
            (user_id, account_id, amount, category, description, date, type, is_manual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.db.execute_query(query, (
            transaction.user_id,
            transaction.account_id,
            transaction.amount,
            transaction.category,
            transaction.description,
            transaction.date.isoformat(),
            transaction.type,
            1 if transaction.is_manual else 0
        ))
        return True
    
    # ========== ЦЕЛИ ==========
    
    def create_goal(self, goal: FinancialGoal) -> bool:
        query = """
            INSERT INTO goals (user_id, name, target_amount, current_amount, deadline, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        deadline_str = goal.deadline.isoformat() if goal.deadline else None
        
        self.db.execute_query(query, (
            goal.user_id,
            goal.name,
            goal.target_amount,
            goal.current_amount,
            deadline_str,
            goal.priority
        ))
        return True
    
    # ========== АНАЛИТИКА ==========
    
    def get_financial_summary(self, user_id: int, months: int = 1) -> Dict[str, Any]:
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        income_query = """
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions 
            WHERE user_id = ? 
            AND type = 'income'
            AND date >= ?
            AND date <= ?
        """
        income_result = self.db.execute_query(income_query, (
            user_id, start_date.isoformat(), end_date.isoformat()
        ))
        total_income = income_result[0][0] if income_result else 0
        
        expense_query = """
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions 
            WHERE user_id = ? 
            AND type = 'expense'
            AND date >= ?
            AND date <= ?
        """
        expense_result = self.db.execute_query(expense_query, (
            user_id, start_date.isoformat(), end_date.isoformat()
        ))
        total_expense = expense_result[0][0] if expense_result else 0
        
        savings = total_income - total_expense
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0
        
        return {
            'income': total_income,
            'expense': total_expense,
            'savings': savings,
            'savings_rate': savings_rate
        }
    
    def get_user_transactions(self, user_id: int, limit: int = 5) -> List[Transaction]:
        query = """
            SELECT id, user_id, account_id, amount, category, description, date, type, is_manual
            FROM transactions 
            WHERE user_id = ?
            ORDER BY date DESC LIMIT ?
        """
        results = self.db.execute_query(query, (user_id, limit))
        
        transactions = []
        if results:
            for row in results:
                transactions.append(Transaction(
                    user_id=row[1],
                    amount=row[3],
                    type=row[7],
                    category=row[4],
                    description=row[5],
                    date=date.fromisoformat(row[6]) if row[6] else date.today(),
                    id=row[0],
                    account_id=row[2],
                    is_manual=bool(row[8])
                ))
        
        return transactions
    
    def get_user_goals(self, user_id: int) -> List[FinancialGoal]:
        query = """
            SELECT id, user_id, name, target_amount, current_amount, deadline, priority, created_at
            FROM goals WHERE user_id = ?
        """
        results = self.db.execute_query(query, (user_id,))
        
        goals = []
        if results:
            for row in results:
                goals.append(FinancialGoal(
                    user_id=row[1],
                    name=row[2],
                    target_amount=row[3],
                    id=row[0],
                    current_amount=row[4],
                    deadline=date.fromisoformat(row[5]) if row[5] else None,
                    priority=row[6],
                    created_at=datetime.fromisoformat(row[7]) if row[7] else None
                ))
        
        return goals
