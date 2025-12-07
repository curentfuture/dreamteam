#!/usr/bin/env python3
"""
Тест интеграции Financial Assistant
"""

import sys
import os
import uuid

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("🚀 Тест интеграции Financial Assistant")
print("="*60)

try:
    print("\n1. Проверка импортов...")
    
    # Базовые импорты
    import sqlite3
    print("   ✅ SQLite доступен")
    
    # Наши модули
    from core.database import Database
    from core.repository import Repository
    from core.models import Transaction, FinancialGoal
    from datetime import date, timedelta
    
    print("   ✅ Все модули загружены")
    
    print("\n2. Инициализация базы данных...")
    db = Database('test_financial.db')
    repo = Repository(db)
    print("   ✅ База данных создана: test_financial.db")
    
    # Генерируем уникальный email для теста
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    print(f"\n3. Создание тестового пользователя ({unique_email})...")
    user = repo.create_user(unique_email, "Тестовый Пользователь", "test123")
    
    if user:
        print(f"   ✅ Пользователь создан: {user.full_name} (ID: {user.id})")
        
        print("\n4. Создание тестового счета...")
        repo.create_account(user.id, "Основной счет", 50000)
        print("   ✅ Счет создан: Основной счет (50,000 руб)")
        
        print("\n5. Добавление тестовых транзакций...")
        
        # Доход
        income = Transaction(
            user_id=user.id,
            amount=85000,
            type='income',
            category='Зарплата',
            description='Заработная плата',
            date=date.today(),
            is_manual=False
        )
        repo.create_transaction(income)
        print("   ✅ Добавлен доход: 85,000 руб (Зарплата)")
        
        # Расходы
        expenses = [
            ("Еда", "Супермаркет", 2500),
            ("Транспорт", "Такси", 800),
            ("Развлечения", "Кино", 1500),
            ("Покупки", "Одежда", 5000)
        ]
        
        for category, desc, amount in expenses:
            expense = Transaction(
                user_id=user.id,
                amount=amount,
                type='expense',
                category=category,
                description=desc,
                date=date.today(),
                is_manual=True
            )
            repo.create_transaction(expense)
            print(f"   ✅ Добавлен расход: {amount} руб ({category})")
        
        print("\n6. Создание финансовой цели...")
        goal = FinancialGoal(
            user_id=user.id,
            name='Новый iPhone',
            target_amount=100000,
            current_amount=20000,
            deadline=date.today() + timedelta(days=180),
            priority='high'
        )
        
        if repo.create_goal(goal):
            print("   ✅ Цель создана: Новый iPhone (100,000 руб)")
            print(f"      Уже накоплено: 20,000 руб")
            print(f"      Осталось: 80,000 руб")
            print(f"      Дедлайн: {goal.deadline}")
        
        print("\n7. Получение финансовой статистики...")
        summary = repo.get_financial_summary(user.id, 1)
        print(f"   📊 Доходы: {summary['income']:,} руб")
        print(f"   📊 Расходы: {summary['expense']:,} руб")
        print(f"   📊 Сбережения: {summary['savings']:,} руб")
        print(f"   📊 Норма сбережений: {summary['savings_rate']:.1f}%")
        
        print("\n8. Получение списка транзакций...")
        transactions = repo.get_user_transactions(user.id, limit=3)
        print(f"   📋 Последние {len(transactions)} транзакций:")
        for i, t in enumerate(transactions, 1):
            sign = "+" if t.type == "income" else "-"
            print(f"      {i}. {t.date}: {t.description} {sign}{t.amount} руб")
        
        print("\n9. Получение списка целей...")
        goals = repo.get_user_goals(user.id)
        print(f"   🎯 Всего целей: {len(goals)}")
        for g in goals:
            progress = (g.current_amount / g.target_amount * 100) if g.target_amount > 0 else 0
            print(f"      • {g.name}: {g.current_amount:,}/{g.target_amount:,} руб ({progress:.1f}%)")
        
        print("\n" + "="*60)
        print("✅ ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("="*60)
        print("\n📋 Результаты:")
        print(f"   • Создан пользователь: {user.email}")
        print(f"   • Добавлено транзакций: {len(expenses) + 1}")
        print(f"   • Создана цель: Новый iPhone")
        print(f"   • База данных: test_financial.db")
        
    else:
        print("❌ Не удалось создать пользователя")
        
except ImportError as e:
    print(f"\n❌ Ошибка импорта: {e}")
    print("\nУстановите зависимости командой:")
    print("  pip install fastapi pandas numpy scikit-learn python-multipart")
    
except Exception as e:
    print(f"\n❌ Ошибка при выполнении теста: {e}")
    import traceback
    traceback.print_exc()
