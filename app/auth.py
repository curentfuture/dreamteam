import streamlit as st

def show_auth_page():
    """Страница авторизации/регистрации"""
    
    # Стилизация
    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Лого и приветствие
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #4CAF50;'>💰</h1>
            <h2>Умный финансовый помощник</h2>
            <p>Контролируйте финансы, достигайте целей, оптимизируйте расходы</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Вкладки
    tab1, tab2 = st.tabs(["🔐 Вход", "📝 Регистрация"])
    
    with tab1:
        st.subheader("Вход в систему")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Логин или email", key="login_username")
            password = st.text_input("Пароль", type="password", key="login_password")
            
            if st.button("Войти", type="primary", use_container_width=True):
                # Простейшая авторизация для демо
                if username and password:
                    st.session_state.user = {
                        "username": username,
                        "name": username.split("@")[0] if "@" in username else username,
                        "email": username if "@" in username else f"{username}@example.com"
                    }
                    st.success(f"Добро пожаловать, {st.session_state.user['name']}!")
                    st.rerun()
                else:
                    st.error("Заполните все поля")
    
    with tab2:
        st.subheader("Создание аккаунта")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            reg_username = st.text_input("Придумайте логин", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Пароль", type="password", key="reg_password")
            reg_confirm = st.text_input("Подтвердите пароль", type="password", key="reg_confirm")
            
            if st.button("Зарегистрироваться", type="primary", use_container_width=True):
                if reg_password != reg_confirm:
                    st.error("Пароли не совпадают")
                elif not all([reg_username, reg_email, reg_password]):
                    st.error("Заполните все поля")
                else:
                    st.session_state.user = {
                        "username": reg_username,
                        "name": reg_username,
                        "email": reg_email
                    }
                    st.success("Регистрация успешна! Добро пожаловать!")
                    st.rerun()
    
    # Демо-доступ
    st.markdown("---")
    with st.expander("🚀 Быстрый старт (демо-режим)"):
        st.write("Для тестирования используйте:")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Войти как демо-пользователь", use_container_width=True):
                st.session_state.user = {
                    "username": "demo_user",
                    "name": "Демо Пользователь",
                    "email": "demo@example.com"
                }
                # Добавляем демо-данные
                st.session_state.goals = [
                    {
                        "id": 1,
                        "name": "Новый iPhone",
                        "amount": 100000,
                        "saved": 25000,
                        "priority": "Высокий",
                        "target_date": "2024-12-31",
                        "created": "2024-01-15",
                        "active": True
                    },
                    {
                        "id": 2,
                        "name": "Отпуск в Турции",
                        "amount": 150000,
                        "saved": 50000,
                        "priority": "Средний",
                        "target_date": "2024-08-31",
                        "created": "2024-01-10",
                        "active": True
                    }
                ]
                
                st.session_state.transactions = [
                    {"id": 1, "date": "2024-03-01", "amount": -1500, "category": "Кафе/Рестораны", "description": "Кофе и выпечка"},
                    {"id": 2, "date": "2024-03-02", "amount": -3000, "category": "Продукты", "description": "Супермаркет"},
                    {"id": 3, "date": "2024-03-03", "amount": 50000, "category": "Зарплата", "description": "ЗП март"},
                    {"id": 4, "date": "2024-03-05", "amount": -8000, "category": "Развлечения", "description": "Кино и ужин"},
                ]
                
                st.rerun()
        
        with col2:
            if st.button("Начать с чистого листа", use_container_width=True):
                st.session_state.user = {
                    "username": "new_user",
                    "name": "Новый Пользователь",
                    "email": "new@example.com"
                }
                st.session_state.goals = []
                st.session_state.transactions = []
                st.rerun()