#!/usr/bin/env python3
"""
Запуск Financial Assistant API
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("🚀 FINANCIAL ASSISTANT API")
print("="*60)

try:
    from main import app
    import uvicorn
    
    print("✅ Приложение загружено")
    
    print("\n📍 API будет доступен по адресам:")
    print("   • http://localhost:8000")
    print("   • http://localhost:8000/docs - Swagger документация")
    
    print("\n📋 Основные endpoints:")
    print("   POST /api/register      - Регистрация пользователя")
    print("   GET  /api/transactions  - Получить транзакции")
    print("   POST /api/transactions  - Добавить транзакцию")
    print("   GET  /api/goals         - Получить цели")
    print("   POST /api/goals         - Создать цель")
    print("   GET  /api/analytics     - Получить аналитику")
    
    print("\n🔄 Запуск сервера...")
    print("   Для остановки нажмите Ctrl+C")
    print("="*60)
    
    # Запускаем без reload
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Отключаем reload
        log_level="info"
    )
    
except ImportError as e:
    print(f"\n❌ Ошибка импорта: {e}")
    print("\n📦 Установите зависимости:")
    print("   pip install fastapi uvicorn")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Ошибка при запуске: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
