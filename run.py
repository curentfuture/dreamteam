#!/usr/bin/env python3
import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Запуск Financial Assistant API с базой данных...")
    print("📍 API доступен по адресу: http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    print("💾 База данных: financial_assistant.db")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)