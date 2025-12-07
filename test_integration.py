#!/usr/bin/env python3
from core.database import Database
from core.repository import Repository
from core.models import Transaction, FinancialGoal
from datetime import date, timedelta

def test_integration():
    print("=== Тест интеграции БД с бэкендом ===\n")
    
    db = Database('test_financial.db')
    repo = Repository(db)
    
    print("1. Создание пользователя...")
    user = repo.create_user("test@example.com", "Тестовый Пользователь")
    print(f"   ✅ Создан пользователь: {user.full_name} (ID: {user.id})")
    
    print("\n2. Создание счета...")
    account = repo.create_account(user.id, "Основной счет", 50000)
    print(f"   ✅ Создан счет: {account.name} (Баланс: {account.balance} {account.currency})")
    
    print("\n3. Добавление транзакций...")
    
    income = Transaction(
        user_id=user.id,
        account_id=account.id,
        amount=85000,
        type='income',
        category='Зарплата',
        description='Заработная плата',
        date=date.today(),
        is_manual=False
    )
    repo.create_transaction(income)
    print("   ✅ Добавлена транзакция: Доход 85,000 руб")
    
    expense = Transaction(
        user_id=user.id,
        account_id=account.id,
        amount=2500,
        type='expense',
        category='Еда',
        description='Супермаркет',
        date=date.today(),
        is_manual=True
    )
    repo.create_transaction(expense)
    print("   ✅ Добавлена транзакция: Расход 2,500 руб")
    
    print("\n4. Создание финансовой цели...")
    goal = FinancialGoal(
        user_id=user.id,
        name='Новый автомобиль',
        target_amount=1500000,
        current_amount=200000,
        deadline=date.today() + timedelta(days=365),
        priority='high'
    )
    created_goal = repo.create_goal(goal)
    print(f"   ✅ Создана цель: {created_goal.name}")
    print(f"   Нужно накопить: {created_goal.target_amount:,} руб")
    print(f"   Уже есть: {created_goal.current_amount:,} руб")
    print(f"   Осталось: {created_goal.amount_left:,} руб")
    
    print("\n5. Получение финансовой сводки...")
    summary = repo.get_financial_summary(user.id, 3)
    print(f"   📊 Доходы за 3 месяца: {summary['totals']['income']:,} руб")
    print(f"   📊 Расходы за 3 месяца: {summary['totals']['expense']:,} руб")
    print(f"   📊 Сбережения: {summary['totals']['savings']:,} руб")
    print(f"   📊 Норма сбережений: {summary['totals']['savings_rate']:.1%}")
    
    print("\n6. Получение транзакций пользователя...")
    transactions = repo.get_user_transactions(user.id, limit=5)
    print(f"   📋 Последние {len(transactions)} транзакций:")
    for t in transactions:
        print(f"     • {t.date}: {t.description} - {t.amount} руб ({t.category})")
    
    print("\n7. Получение целей пользователя...")
    goals = repo.get_user_goals(user.id)
    print(f"   🎯 Всего целей: {len(goals)}")
    for g in goals:
        print(f"     • {g.name}: {g.current_amount:,}/{g.target_amount:,} руб")
    
    print("\n=== Тест завершен успешно! ===")
    print("\nДля запуска API выполните:")
    print("  python run.py")
    print("\nДля тестирования API используйте:")
    print("  curl -X POST http://localhost:8000/api/register -d 'email=user@test.com&full_name=Test User'")

if __name__ == "__main__":
    test_integration()