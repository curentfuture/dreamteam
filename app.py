import sys
import os

# Добавляем папку app в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Теперь можно импортировать
from app.main import main

if __name__ == "__main__":
    main()