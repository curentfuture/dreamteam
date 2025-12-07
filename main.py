from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
import sqlite3
import uvicorn
from typing import Optional, List, Dict, Any

app = FastAPI(title="Financial Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация БД
def init_db():
    conn = sqlite3.connect('financial_assistant.db')
    cursor = conn.cursor()
    
    # Пользователи
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Транзакции
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date DATE NOT NULL,
            type TEXT CHECK(type IN ('expense', 'income')),
            is_manual BOOLEAN DEFAULT 0
        )
    ''')
    
    # Цели
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            deadline DATE,
            priority TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {
        "message": "Financial Assistant API работает!",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Эта страница"},
            {"path": "/docs", "method": "GET", "description": "Swagger документация"},
            {"path": "/api/health", "method": "GET", "description": "Проверка здоровья"},
            {"path": "/api/register", "method": "POST", "description": "Регистрация пользователя"},
            {"path": "/api/transactions", "method": "GET", "description": "Получить транзакции"},
            {"path": "/api/transactions", "method": "POST", "description": "Добавить транзакцию"},
            {"path": "/api/goals", "method": "GET", "description": "Получить цели"},
            {"path": "/api/goals", "method": "POST", "description": "Создать цель"},
            {"path": "/api/analytics", "method": "GET", "description": "Получить аналитику"}
        ]
    }

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "financial-assistant",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }

@app.post("/api/register")
async def register(
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(None)
):
    conn = sqlite3.connect('financial_assistant.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (email, full_name) VALUES (?, ?)",
            (email, full_name)
        )
        user_id = cursor.lastrowid
        
        # Добавляем демо-данные
        demo_transactions = [
            (user_id, 85000, 'Зарплата', 'Заработная плата', '2024-12-07', 'income', 0),
            (user_id, 2500, 'Еда', 'Супермаркет', '2024-12-07', 'expense', 0),
            (user_id, 1500, 'Транспорт', 'Такси', '2024-12-07', 'expense', 0),
            (user_id, 3000, 'Развлечения', 'Кино', '2024-12-07', 'expense', 0),
        ]
        
        cursor.executemany(
            "INSERT INTO transactions (user_id, amount, category, description, date, type, is_manual) VALUES (?, ?, ?, ?, ?, ?, ?)",
            demo_transactions
        )
        
        # Добавляем демо-цель
        cursor.execute(
            "INSERT INTO goals (user_id, name, target_amount, current_amount, deadline) VALUES (?, ?, ?, ?, ?)",
            (user_id, 'Новый iPhone', 100000, 20000, '2025-06-01')
        )
        
        conn.commit()
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "message": "Пользователь зарегистрирован. Добавлены демо-данные.",
            "demo_data": {
                "transactions": len(demo_transactions),
                "goal": "Новый iPhone (100,000 руб)"
            }
        }
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
    finally:
        conn.close()

@app.get("/api/transactions")
async def get_transactions(
    email: str,
    limit: int = 10
):
    conn = sqlite3.connect('financial_assistant.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user_id = user_result[0]
        
        cursor.execute('''
            SELECT id, amount, category, description, date, type, is_manual
            FROM transactions 
            WHERE user_id = ?
            ORDER BY date DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        transactions = cursor.fetchall()
        
        result = []
        for trans in transactions:
            result.append({
                "id": trans[0],
                "amount": trans[1],
                "category": trans[2],
                "description": trans[3],
                "date": trans[4],
                "type": trans[5],
                "is_manual": bool(trans[6])
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "count": len(result),
            "transactions": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
    finally:
        conn.close()

@app.post("/api/transactions")
async def add_transaction(
    email: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    description: str = Form(""),
    type: str = Form("expense")
):
    conn = sqlite3.connect('financial_assistant.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user_id = user_result[0]
        
        cursor.execute('''
            INSERT INTO transactions (user_id, amount, category, description, date, type, is_manual)
            VALUES (?, ?, ?, ?, DATE('now'), ?, 1)
        ''', (user_id, amount, category, description, type))
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Транзакция добавлена",
            "transaction": {
                "amount": amount,
                "category": category,
                "description": description,
                "type": type,
                "date": datetime.now().date().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
    finally:
        conn.close()

@app.get("/api/goals")
async def get_goals(email: str):
    conn = sqlite3.connect('financial_assistant.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user_id = user_result[0]
        
        cursor.execute('''
            SELECT id, name, target_amount, current_amount, deadline, priority, created_at
            FROM goals 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        goals = cursor.fetchall()
        
        result = []
        for goal in goals:
            target = goal[2]
            current = goal[3]
            progress = (current / target * 100) if target > 0 else 0
            
            result.append({
                "id": goal[0],
                "name": goal[1],
                "target_amount": target,
                "current_amount": current,
                "progress": progress,
                "deadline": goal[4],
                "priority": goal[5],
                "created_at": goal[6]
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "count": len(result),
            "goals": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
    finally:
        conn.close()

@app.post("/api/goals")
async def create_goal(
    email: str = Form(...),
    name: str = Form(...),
    target_amount: float = Form(...),
    current_amount: float = Form(0),
    deadline: str = Form(None),
    priority: str = Form("medium")
):
    conn = sqlite3.connect('financial_assistant.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user_id = user_result[0]
        
        cursor.execute('''
            INSERT INTO goals (user_id, name, target_amount, current_amount, deadline, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, target_amount, current_amount, deadline, priority))
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Цель создана",
            "goal": {
                "name": name,
                "target_amount": target_amount,
                "current_amount": current_amount,
                "deadline": deadline,
                "priority": priority
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
    finally:
        conn.close()

@app.get("/api/analytics")
async def get_analytics(
    email: str,
    months: int = 3
):
    conn = sqlite3.connect('financial_assistant.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_result = cursor.fetchone()
        
        if not user_result:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user_id = user_result[0]
        
        # Доходы за период
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions 
            WHERE user_id = ? 
            AND type = 'income'
            AND date >= DATE('now', '-' || ? || ' months')
        ''', (user_id, months))
        
        total_income = cursor.fetchone()[0]
        
        # Расходы за период
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions 
            WHERE user_id = ? 
            AND type = 'expense'
            AND date >= DATE('now', '-' || ? || ' months')
        ''', (user_id, months))
        
        total_expense = cursor.fetchone()[0]
        
        # Расходы по категориям
        cursor.execute('''
            SELECT category, COALESCE(SUM(amount), 0) as total
            FROM transactions 
            WHERE user_id = ? 
            AND type = 'expense'
            AND date >= DATE('now', '-' || ? || ' months')
            GROUP BY category
            ORDER BY total DESC
        ''', (user_id, months))
        
        categories = cursor.fetchall()
        
        category_data = []
        for cat in categories:
            category_data.append({
                "category": cat[0],
                "total": cat[1],
                "percentage": (cat[1] / total_expense * 100) if total_expense > 0 else 0
            })
        
        savings = total_income - total_expense
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0
        
        return {
            "success": True,
            "user_id": user_id,
            "period_months": months,
            "totals": {
                "income": total_income,
                "expense": total_expense,
                "savings": savings,
                "savings_rate": savings_rate
            },
            "categories": category_data,
            "monthly_average": {
                "income": total_income / months if months > 0 else 0,
                "expense": total_expense / months if months > 0 else 0,
                "savings": savings / months if months > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("🚀 Financial Assistant API запускается...")
    print("📍 Адрес: http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
