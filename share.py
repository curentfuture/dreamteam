import subprocess
import threading
import time
from pyngrok import ngrok
import os

def run_streamlit():
    """Запуск Streamlit"""
    print("🚀 Запускаем Streamlit...")
    subprocess.run([
        "streamlit", "run", "app/main.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--browser.serverAddress", "0.0.0.0"
    ])

def main():
    print("=" * 50)
    print("💰 Финансовый помощник - Запуск для команды")
    print("=" * 50)
    
    # Установи свой токен ngrok
    # Получи здесь: https://dashboard.ngrok.com/get-started/your-authtoken
    NGROK_TOKEN = "30K9f5jAUNC9vXREus72UUg0oSz_5J19iYtx37Xkn1WQpZTRX"  # ЗАМЕНИ НА СВОЙ
    
    if not NGROK_TOKEN or NGROK_TOKEN.startswith("2j0D"):
        print("\n❌ Нужен ngrok токен!")
        print("1. Зайди: https://dashboard.ngrok.com/signup")
        print("2. Зарегистрируйся")
        print("3. Скопируй токен с: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("4. Вставь его в переменную NGROK_TOKEN в этом файле")
        return
    
    # Настройка ngrok
    ngrok.set_auth_token(NGROK_TOKEN)
    
    # Запускаем Streamlit в отдельном потоке
    print("\n⏳ Запускаем приложение...")
    streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Ждем запуска Streamlit
    time.sleep(5)
    
    # Открываем туннель
    print("🌐 Создаем публичную ссылку...")
    try:
        public_url = ngrok.connect(8501, "http")
        print("\n" + "=" * 50)
        print("✅ ПРИЛОЖЕНИЕ ЗАПУЩЕНО!")
        print("=" * 50)
        print(f"\n📱 Твоя локальная ссылка:")
        print(f"   http://localhost:8501")
        print(f"\n🌍 Публичная ссылка (отправь команде):")
        print(f"   🔗 {public_url}")
        print(f"\n📋 Скопируй и отправь команде в чат:")
        print(f"   {public_url}")
        print("\n🔄 Приложение работает...")
        print("📌 Нажми Ctrl+C чтобы остановить")
        print("=" * 50)
        
        # Держим программу активной
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n🔧 Попробуй:")
        print("1. Проверь ngrok токен")
        print("2. Убедись что порт 8501 свободен")
        print("3. Запусти: lsof -i :8501")

if __name__ == "__main__":
    main()