import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self, db_path='financial_assistant.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Создаем таблицы при первом запуске"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Пользователи
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    full_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Счета
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    balance REAL DEFAULT 0,
                    currency TEXT DEFAULT 'RUB',
                    last_updated TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Транзакции
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    account_id INTEGER,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    date DATE NOT NULL,
                    type TEXT CHECK(type IN ('expense', 'income', 'transfer')),
                    is_manual BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"   ✅ База данных создана: {self.db_path}")
        except Exception as e:
            print(f"   ❌ Ошибка при создании БД: {e}")
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для подключения"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа по имени колонки
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query, params=()):
        """Выполнить запрос и вернуть результат"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                cursor.close()
                conn.close()
                return result
            
            cursor.close()
            conn.close()
            return None
            
        except Exception as e:
            print(f"   ❌ Ошибка SQL: {e}")
            print(f"      Запрос: {query}")
            print(f"      Параметры: {params}")
            return None
