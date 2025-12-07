import subprocess
import threading
import time
from pyngrok import ngrok, conf
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def run_streamlit():
    """Запуск Streamlit приложения"""
    print("🚀 Запускаем Streamlit приложение...")
    
    # Запускаем Streamlit
    subprocess.run([
        "streamlit", "run", 
        "app/main.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.serverAddress", "0.0.0.0",
        "--theme.base", "light"
    ])

def setup_ngrok():
    """Настройка и запуск ngrok"""
    print("🔧 Настраиваем ngrok...")
    
    # Получаем authtoken из переменных окружения или запрашиваем
    auth_token = os.getenv("NGROK_AUTHTOKEN")
    
    if not auth_token:
        print("\n⚠️  NGROK_AUTHTOKEN не найден в .env файле")
        print("📝 Получите токен: https://dashboard.ngrok.com/get-started/your-authtoken")
        auth_token = input("Введите ваш ngrok authtoken: ")
        
        # Сохраняем в .env для будущего использования
        with open(".env", "w") as f:
            f.write(f"NGROK_AUTHTOKEN={auth_token}")
        print("✅ Токен сохранен в .env файл")
    
    # Настраиваем ngrok
    conf.get_default().auth_token = auth_token
    conf.get_default().region = "eu"  # Европа, можно изменить на "us", "ap", "au"
    
    # Открываем туннель
    print("🌐 Открываем туннель...")
    public_url = ngrok.connect(8501, "http")
    
    print(f"\n✅ Приложение запущено!")
    print(f"📱 Локальная ссылка: http://localhost:8501")
    print(f"🌍 Публичная ссылка: {public_url}")
    print(f"\n📋 Ссылка для демонстрации: {public_url}")
    
    return public_url

def main():
    """Основная функция запуска"""
    print("=" * 50)
    print("💰 Умный финансовый помощник")
    print("=" * 50)
    
    # Создаем .env файл если его нет
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Конфигурация ngrok\n")
            f.write("NGROK_AUTHTOKEN=ваш_токен_здесь\n")
        print("📄 Создан .env файл. Добавьте ваш ngrok токен.")
    
    try:
        # Запускаем Streamlit в отдельном потоке
        streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
        streamlit_thread.start()
        
        # Ждем немного перед запуском ngrok
        time.sleep(3)
        
        # Настраиваем ngrok
        public_url = setup_ngrok()
        
        # Держим программу активной
        print("\n🔄 Приложение работает...")
        print("📌 Нажмите Ctrl+C чтобы остановить")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Останавливаем приложение...")
            ngrok.kill()
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Убедитесь что ngrok токен верный")
        print("2. Проверьте что порт 8501 свободен")
        print("3. Попробуйте другой порт: измените 8501 на 8502 в run.py")

if __name__ == "__main__":
    main()