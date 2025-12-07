# main.py
from fastapi import FastAPI, HTTPException, Depends, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import uvicorn

from core.database import Database
from core.repository import Repository
from core.models import Transaction, FinancialGoal, User, Account, UserProfile
from core.calculator import FinancialCalculator
from core.recommender import RecommendationEngine

app = FastAPI(title="Financial Assistant API", version="2.0.0")

# Инициализация БД и репозитория
db = Database('financial_assistant.db')
repo = Repository(db)
recommendation_engine = RecommendationEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(email: str = Form(...)) -> Optional[User]:
    user = repo.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user

@app.get("/")
async def root():
    return {"message": "Financial Assistant API", "status": "running", "database": "connected"}

@app.post("/api/register")
async def register(
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(None)
):
    existing_user = repo.get_user_by_email(email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    password_hash = f"hashed_{password}" if password else None
    
    user = repo.create_user(email, full_name, password_hash)
    if not user:
        raise HTTPException(status_code=500, detail="Ошибка при создании пользователя")
    
    repo.create_account(user.id, "Основной счет", 0, "RUB")
    repo.seed_mock_data(user.id)
    
    return {
        "success": True,
        "user": user.to_dict(),
        "message": "Пользователь создан. Добавлены демо-данные."
    }

@app.post("/api/login")
async def login(email: str = Form(...)):
    user = repo.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    return {
        "success": True,
        "user": user.to_dict(),
        "message": "Вход выполнен успешно"
    }

@app.get("/api/transactions")
async def get_transactions(
    user: User = Depends(get_current_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    
    transactions = repo.get_user_transactions(user.id, start, end, limit)
    
    return {
        "success": True,
        "count": len(transactions),
        "transactions": [t.to_dict() for t in transactions]
    }

@app.post("/api/transactions")
async def create_transaction(
    user: User = Depends(get_current_user),
    amount: float = Form(...),
    category: str = Form(...),
    description: str = Form(""),
    transaction_date: str = Form(None),
    type: str = Form("expense"),
    account_id: int = Form(None)
):
    trans_date = date.fromisoformat(transaction_date) if transaction_date else date.today()
    
    transaction = Transaction(
        user_id=user.id,
        account_id=account_id,
        amount=amount,
        type=type,
        category=category,
        description=description,
        date=trans_date,
        is_manual=True
    )
    
    created_transaction = repo.create_transaction(transaction)
    if not created_transaction:
        raise HTTPException(status_code=500, detail="Ошибка при создании транзакции")
    
    return {
        "success": True,
        "transaction": created_transaction.to_dict(),
        "message": "Транзакция добавлена"
    }

@app.get("/api/goals")
async def get_goals(user: User = Depends(get_current_user)):
    goals = repo.get_user_goals(user.id)
    
    return {
        "success": True,
        "goals": [goal.to_dict() for goal in goals]
    }

@app.post("/api/goals")
async def create_goal(
    user: User = Depends(get_current_user),
    name: str = Form(...),
    target_amount: float = Form(...),
    current_amount: float = Form(0),
    deadline: Optional[str] = Form(None),
    priority: str = Form("medium")
):
    deadline_date = date.fromisoformat(deadline) if deadline else None
    
    goal = FinancialGoal(
        user_id=user.id,
        name=name,
        target_amount=target_amount,
        current_amount=current_amount,
        deadline=deadline_date,
        priority=priority
    )
    
    created_goal = repo.create_goal(goal)
    if not created_goal:
        raise HTTPException(status_code=500, detail="Ошибка при создании цели")
    
    return {
        "success": True,
        "goal": created_goal.to_dict(),
        "message": "Цель создана"
    }

@app.put("/api/goals/{goal_id}/progress")
async def update_goal_progress(
    goal_id: int,
    new_amount: float = Form(...),
    user: User = Depends(get_current_user)
):
    goals = repo.get_user_goals(user.id)
    goal_exists = any(goal.id == goal_id for goal in goals)
    
    if not goal_exists:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    success = repo.update_goal_progress(goal_id, new_amount)
    
    return {
        "success": success,
        "message": "Прогресс обновлен"
    }

@app.get("/api/analytics/summary")
async def get_financial_summary(
    user: User = Depends(get_current_user),
    months: int = 3
):
    summary = repo.get_financial_summary(user.id, months)
    
    return {
        "success": True,
        "summary": summary
    }

@app.get("/api/recommendations/{goal_id}")
async def get_recommendations(
    goal_id: int,
    user: User = Depends(get_current_user)
):
    goals = repo.get_user_goals(user.id)
    goal = next((g for g in goals if g.id == goal_id), None)
    
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    transactions = repo.get_user_transactions(user.id, limit=100)
    summary = repo.get_financial_summary(user.id, 3)
    
    user_profile = UserProfile(
        user_id=user.id,
        monthly_income=summary['monthly_average']['income'],
        monthly_expenses=summary['monthly_average']['expense'],
        average_savings_rate=summary['totals']['savings_rate'],
        risk_tolerance=0.5
    )
    
    calculator = FinancialCalculator()
    spending_analysis = calculator.analyze_spending_patterns(transactions)
    
    recommendations = recommendation_engine.generate_recommendations(
        goal, user_profile, spending_analysis
    )
    
    return {
        "success": True,
        "goal": goal.to_dict(),
        "recommendations": [rec.to_dict() for rec in recommendations],
        "count": len(recommendations)
    }

@app.post("/api/recommendations/{goal_id}/calculate-impact")
async def calculate_impact(
    goal_id: int,
    selected_ids: List[str] = Body(...),
    user: User = Depends(get_current_user)
):
    goals = repo.get_user_goals(user.id)
    goal = next((g for g in goals if g.id == goal_id), None)
    
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    transactions = repo.get_user_transactions(user.id, limit=100)
    summary = repo.get_financial_summary(user.id, 3)
    
    user_profile = UserProfile(
        user_id=user.id,
        monthly_income=summary['monthly_average']['income'],
        monthly_expenses=summary['monthly_average']['expense'],
        average_savings_rate=summary['totals']['savings_rate'],
        risk_tolerance=0.5
    )
    
    calculator = FinancialCalculator()
    spending_analysis = calculator.analyze_spending_patterns(transactions)
    
    all_recommendations = recommendation_engine.generate_recommendations(
        goal, user_profile, spending_analysis
    )
    
    selected_recommendations = [
        rec for rec in all_recommendations
        if rec.id in selected_ids
    ]
    
    impact = recommendation_engine.calculate_combined_impact(
        goal, user_profile, selected_recommendations
    )
    
    return {
        "success": True,
        "impact": impact,
        "selected_count": len(selected_recommendations)
    }

@app.get("/api/accounts")
async def get_accounts(user: User = Depends(get_current_user)):
    accounts = repo.get_user_accounts(user.id)
    
    return {
        "success": True,
        "accounts": [acc.to_dict() for acc in accounts]
    }

@app.post("/api/accounts")
async def create_account(
    user: User = Depends(get_current_user),
    name: str = Form(...),
    balance: float = Form(0),
    currency: str = Form("RUB")
):
    account = repo.create_account(user.id, name, balance, currency)
    
    if not account:
        raise HTTPException(status_code=500, detail="Ошибка при создании счета")
    
    return {
        "success": True,
        "account": account.to_dict(),
        "message": "Счет создан"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)