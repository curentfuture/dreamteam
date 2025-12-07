# repository.py
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
            RETURNING id, email, full_name, created_at
        """
        result = self.db.execute_query(query, (email, full_name, password_hash))
        
        if result and len(result) > 0:
            user_data = {
                'id': result[0][0],
                'email': result[0][1],
                'full_name': result[0][2],
                'created_at': datetime.fromisoformat(result[0][3]) if result[0][3] else None
            }
            return User.from_dict(user_data)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        query = "SELECT id, email, full_name, password_hash, created_at FROM users WHERE email = ?"
        result = self.db.execute_query(query, (email,))
        
        if result and len(result) > 0:
            user_data = {
                'id': result[0][0],
                'email': result[0][1],
                'full_name': result[0][2],
                'password_hash': result[0][3],
                'created_at': datetime.fromisoformat(result[0][4]) if result[0][4] else None
            }
            return User.from_dict(user_data)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        query = "SELECT id, email, full_name, created_at FROM users WHERE id = ?"
        result = self.db.execute_query(query, (user_id,))
        
        if result and len(result) > 0:
            user_data = {
                'id': result[0][0],
                'email': result[0][1],
                'full_name': result[0][2],
                'created_at': datetime.fromisoformat(result[0][3]) if result[0][3] else None
            }
            return User.from_dict(user_data)
        return None
    
    # ========== СЧЕТА ==========
    
    def create_account(self, user_id: int, name: str, balance: float = 0, currency: str = 'RUB') -> Optional[Account]:
        query = """
            INSERT INTO accounts (user_id, name, balance, currency, last_updated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            RETURNING id, user_id, name, balance, currency, last_updated
        """
        result = self.db.execute_query(query, (user_id, name, balance, currency))
        
        if result and len(result) > 0:
            account_data = {
                'id': result[0][0],
                'user_id': result[0][1],
                'name': result[0][2],
                'balance': result[0][3],
                'currency': result[0][4],
                'last_updated': datetime.fromisoformat(result[0][5]) if result[0][5] else None
            }
            return Account.from_dict(account_data)
        return None
    
    def get_user_accounts(self, user_id: int) -> List[Account]:
        query = """
            SELECT id, user_id, name, balance, currency, last_updated 
            FROM accounts 
            WHERE user_id = ?
            ORDER BY name
        """
        results = self.db.execute_query(query, (user_id,))
        
        accounts = []
        for row in results:
            account_data = {
                'id': row[0],
                'user_id': row[1],
                'name': row[2],
                'balance': row[3],
                'currency': row[4],
                'last_updated': datetime.fromisoformat(row[5]) if row[5] else None
            }
            accounts.append(Account.from_dict(account_data))
        
        return accounts
    
    # ========== ТРАНЗАКЦИИ ==========
    
    def create_transaction(self, transaction: Transaction) -> Optional[Transaction]:
        if transaction.account_id:
            self._update_account_balance(
                transaction.account_id, 
                transaction.amount if transaction.type == 'income' else -transaction.amount
            )
        
        query = """
            INSERT INTO transactions 
            (user_id, account_id, amount, category, description, date, type, is_manual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id, user_id, account_id, amount, category, description, date, type, is_manual
        """
        
        params = (
            transaction.user_id,
            transaction.account_id,
            transaction.amount,
            transaction.category,
            transaction.description,
            transaction.date.isoformat(),
            transaction.type,
            1 if transaction.is_manual else 0
        )
        
        result = self.db.execute_query(query, params)
        
        if result and len(result) > 0:
            transaction_data = {
                'id': result[0][0],
                'user_id': result[0][1],
                'account_id': result[0][2],
                'amount': result[0][3],
                'category': result[0][4],
                'description': result[0][5],
                'date': date.fromisoformat(result[0][6]) if result[0][6] else None,
                'type': result[0][7],
                'is_manual': bool(result[0][8])
            }
            return Transaction.from_dict(transaction_data)
        return None
    
    def _update_account_balance(self, account_id: int, amount_change: float):
        query = """
            UPDATE accounts 
            SET balance = balance + ?, last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        self.db.execute_query(query, (amount_change, account_id))
    
    def get_user_transactions(
        self, 
        user_id: int, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[Transaction]:
        query = """
            SELECT id, user_id, account_id, amount, category, description, date, type, is_manual
            FROM transactions 
            WHERE user_id = ?
        """
        params = [user_id]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        results = self.db.execute_query(query, tuple(params))
        
        transactions = []
        for row in results:
            transaction_data = {
                'id': row[0],
                'user_id': row[1],
                'account_id': row[2],
                'amount': row[3],
                'category': row[4],
                'description': row[5],
                'date': date.fromisoformat(row[6]) if row[6] else None,
                'type': row[7],
                'is_manual': bool(row[8])
            }
            transactions.append(Transaction.from_dict(transaction_data))
        
        return transactions
    
    def get_transactions_by_category(
        self, 
        user_id: int, 
        category: str,
        months: int = 3
    ) -> List[Transaction]:
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        query = """
            SELECT id, user_id, account_id, amount, category, description, date, type, is_manual
            FROM transactions 
            WHERE user_id = ? 
            AND category = ?
            AND date >= ?
            AND date <= ?
            ORDER BY date DESC
        """
        
        results = self.db.execute_query(query, (
            user_id, category, start_date.isoformat(), end_date.isoformat()
        ))
        
        transactions = []
        for row in results:
            transaction_data = {
                'id': row[0],
                'user_id': row[1],
                'account_id': row[2],
                'amount': row[3],
                'category': row[4],
                'description': row[5],
                'date': date.fromisoformat(row[6]) if row[6] else None,
                'type': row[7],
                'is_manual': bool(row[8])
            }
            transactions.append(Transaction.from_dict(transaction_data))
        
        return transactions
    
    # ========== ЦЕЛИ ==========
    
    def create_goal(self, goal: FinancialGoal) -> Optional[FinancialGoal]:
        query = """
            INSERT INTO goals (user_id, name, target_amount, current_amount, deadline, priority)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id, user_id, name, target_amount, current_amount, deadline, priority, created_at
        """
        
        deadline_str = goal.deadline.isoformat() if goal.deadline else None
        
        result = self.db.execute_query(query, (
            goal.user_id,
            goal.name,
            goal.target_amount,
            goal.current_amount,
            deadline_str,
            goal.priority
        ))
        
        if result and len(result) > 0:
            goal_data = {
                'id': result[0][0],
                'user_id': result[0][1],
                'name': result[0][2],
                'target_amount': result[0][3],
                'current_amount': result[0][4],
                'deadline': result[0][5],
                'priority': result[0][6],
                'created_at': result[0][7]
            }
            return FinancialGoal.from_dict(goal_data)
        return None
    
    def get_user_goals(self, user_id: int) -> List[FinancialGoal]:
        query = """
            SELECT id, user_id, name, target_amount, current_amount, deadline, priority, created_at
            FROM goals 
            WHERE user_id = ?
            ORDER BY created_at DESC
        """
        
        results = self.db.execute_query(query, (user_id,))
        
        goals = []
        for row in results:
            goal_data = {
                'id': row[0],
                'user_id': row[1],
                'name': row[2],
                'target_amount': row[3],
                'current_amount': row[4],
                'deadline': row[5],
                'priority': row[6],
                'created_at': row[7]
            }
            goals.append(FinancialGoal.from_dict(goal_data))
        
        return goals
    
    def update_goal_progress(self, goal_id: int, new_amount: float) -> bool:
        query = """
            UPDATE goals 
            SET current_amount = ?
            WHERE id = ?
        """
        
        self.db.execute_query(query, (new_amount, goal_id))
        return True
    
    def delete_goal(self, goal_id: int) -> bool:
        query = "DELETE FROM goals WHERE id = ?"
        self.db.execute_query(query, (goal_id,))
        return True
    
    # ========== АНАЛИТИКА ==========
    
    def get_financial_summary(self, user_id: int, months: int = 3) -> Dict[str, Any]:
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
        
        category_query = """
            SELECT category, COALESCE(SUM(amount), 0) as total
            FROM transactions 
            WHERE user_id = ? 
            AND type = 'expense'
            AND date >= ?
            AND date <= ?
            GROUP BY category
            ORDER BY total DESC
        """
        category_results = self.db.execute_query(category_query, (
            user_id, start_date.isoformat(), end_date.isoformat()
        ))
        
        categories = []
        for row in category_results:
            categories.append({
                'category': row[0],
                'total': row[1],
                'percentage': (row[1] / total_expense * 100) if total_expense > 0 else 0
            })
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'months': months
            },
            'totals': {
                'income': total_income,
                'expense': total_expense,
                'savings': total_income - total_expense,
                'savings_rate': (total_income - total_expense) / total_income if total_income > 0 else 0
            },
            'categories': categories,
            'monthly_average': {
                'income': total_income / months,
                'expense': total_expense / months,
                'savings': (total_income - total_expense) / months
            }
        }
    
    def seed_mock_data(self, user_id: int):
        categories = ['Еда', 'Транспорт', 'Развлечения', 'Покупки', 'Здоровье', 'Образование']
        descriptions = {
            'Еда': ['Магнит', 'Пятерочка', 'Ресторан', 'Доставка еды'],
            'Транспорт': ['Такси', 'Метро', 'Бензин', 'Парковка'],
            'Развлечения': ['Кино', 'Концерт', 'Театр', 'Квест'],
            'Покупки': ['Одежда', 'Техника', 'Книги', 'Косметика'],
            'Здоровье': ['Аптека', 'Врач', 'Спортзал'],
            'Образование': ['Курсы', 'Книги', 'Конференция']
        }
        
        today = date.today()
        
        for i in range(3):
            salary_date = today.replace(day=5) - timedelta(days=i * 30)
            salary = Transaction(
                user_id=user_id,
                amount=85000 + random.randint(-5000, 10000),
                type='income',
                category='Зарплата',
                description='Заработная плата',
                date=salary_date,
                is_manual=False
            )
            self.create_transaction(salary)
        
        for i in range(50):
            days_ago = random.randint(0, 90)
            trans_date = today - timedelta(days=days_ago)
            category = random.choice(categories)
            description = random.choice(descriptions[category])
            
            amount_range = {
                'Еда': (200, 3000),
                'Транспорт': (50, 2000),
                'Развлечения': (500, 10000),
                'Покупки': (1000, 30000),
                'Здоровье': (300, 5000),
                'Образование': (1000, 20000)
            }
            
            min_a, max_a = amount_range[category]
            amount = random.randint(min_a, max_a)
            
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                type='expense',
                category=category,
                description=description,
                date=trans_date,
                is_manual=False
            )
            self.create_transaction(transaction)