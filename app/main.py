import streamlit as st
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(
    page_title="💰 Умный финансовый помощник",
    page_icon="💰",
    layout="wide"
)

# Глобальные функции для загрузки данных
@st.cache_data
def load_transaction_data():
    """Загрузка данных из csvjson.json"""
    try:
        with open('data/csvjson.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Добавляем необходимые колонки если их нет
        if 'description' not in df.columns:
            df['description'] = ''
        
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return pd.DataFrame()

@st.cache_data
def get_financial_summary(df):
    """Расчет финансовой сводки"""
    if df.empty:
        return {
            'total_income': 0,
            'total_expense': 0,
            'balance': 0,
            'transaction_count': 0,
            'expense_by_category': pd.Series(dtype=float),
            'income_by_category': pd.Series(dtype=float)
        }
    
    income_df = df[df['type'] == 'income']
    expense_df = df[df['type'] == 'expense']
    
    return {
        'total_income': income_df['amount'].sum(),
        'total_expense': abs(expense_df['amount'].sum()),
        'balance': income_df['amount'].sum() - abs(expense_df['amount'].sum()),
        'transaction_count': len(df),
        'expense_by_category': expense_df.groupby('category')['amount'].sum().abs(),
        'income_by_category': income_df.groupby('category')['amount'].sum()
    }

@st.cache_data
def get_goals_progress(df):
    """Расчет прогресса по целям на основе расходов"""
    if df.empty:
        return []
    
    expense_by_category = df[df['type'] == 'expense'].groupby('category')['amount'].sum().abs()
    
    # Создаем цели на основе категорий расходов
    goals = []
    for category, amount in expense_by_category.items():
        # Цель - сократить расходы по категории на 20%
        target_amount = amount * 0.8  # Сократить на 20%
        saved = amount - target_amount  # Уже "сэкономили" если тратим меньше
        
        goals.append({
            'name': f'Сократить {category}',
            'category': category,
            'current': amount,
            'target': target_amount,
            'saved': max(0, saved),
            'priority': 'Высокий' if amount > expense_by_category.median() else 'Средний'
        })
    
    return goals

# Инициализация состояния
if 'user' not in st.session_state:
    st.session_state.user = None
if 'custom_goals' not in st.session_state:
    st.session_state.custom_goals = []
if 'optimization_rules' not in st.session_state:
    st.session_state.optimization_rules = {}

def main():
    st.title("💰 Умный финансовый помощник")
    st.markdown("---")
    
    if not st.session_state.user:
        show_auth_page()
    else:
        show_main_app()

def show_auth_page():
    """Страница авторизации с улучшенной безопасностью"""
    st.header("🔐 Вход в систему")
    
    # Вкладки для входа и регистрации
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        st.subheader("Вход в аккаунт")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            username = st.text_input("Логин", key="login_username")
            password = st.text_input("Пароль", type="password", key="login_password")
            
            # Запомнить меня
            remember_me = st.checkbox("Запомнить меня")
            
            if st.button("Войти", type="primary", use_container_width=True):
                if validate_login(username, password):
                    st.session_state.user = {
                        "username": username,
                        "name": get_user_name(username),
                        "role": "user",
                        "remember_me": remember_me
                    }
                    st.success(f"Добро пожаловать, {st.session_state.user['name']}!")
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
            
            # Быстрый вход для демо
            st.markdown("---")
            st.markdown("**Быстрый доступ:**")
            
            demo_col1, demo_col2 = st.columns(2)
            with demo_col1:
                if st.button("👑 Админ", use_container_width=True):
                    st.session_state.user = {
                        "username": "admin",
                        "name": "Администратор",
                        "role": "admin"
                    }
                    st.success("Вход как администратор!")
                    st.rerun()
            
            with demo_col2:
                if st.button("👤 Демо", use_container_width=True):
                    st.session_state.user = {
                        "username": "demo",
                        "name": "Демо Пользователь",
                        "role": "demo"
                    }
                    st.success("Вход в демо-режим!")
                    st.rerun()
    
    with tab2:
        st.subheader("Создание аккаунта")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            new_username = st.text_input("Придумайте логин", key="new_username")
            new_email = st.text_input("Email", key="new_email")
            new_password = st.text_input("Придумайте пароль", type="password", key="new_password")
            
            # Индикатор сложности пароля
            if new_password:
                strength = check_password_strength(new_password)
                st.progress(strength['score'] / 4)
                st.caption(f"Сложность: {strength['level']}")
                
                if strength['score'] < 2:
                    st.warning("Пароль слишком простой!")
            
            confirm_password = st.text_input("Подтвердите пароль", type="password", key="confirm_password")
            
            # Условия использования
            agree_terms = st.checkbox("Я согласен с условиями использования", key="agree_terms")
            
            if st.button("Зарегистрироваться", type="primary", use_container_width=True):
                if validate_registration(new_username, new_email, new_password, confirm_password, agree_terms):
                    # Регистрация пользователя
                    register_user(new_username, new_email, new_password)
                    
                    st.session_state.user = {
                        "username": new_username,
                        "name": new_username,
                        "email": new_email,
                        "role": "user",
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    st.success(f"🎉 Аккаунт {new_username} успешно создан!")
                    st.balloons()
                    st.rerun()

def validate_login(username, password):
    """Валидация логина и пароля"""
    # В реальном приложении здесь была бы проверка в базе данных
    # Для демо используем простые проверки
    
    if not username or not password:
        return False
    
    # Демо-пользователи
    demo_users = {
        "admin": "admin123",
        "user": "password123",
        "demo": "demo123"
    }
    
    return demo_users.get(username) == password

def get_user_name(username):
    """Получение имени пользователя"""
    names = {
        "admin": "Администратор",
        "user": "Пользователь",
        "demo": "Демо Пользователь"
    }
    
    return names.get(username, username)

def check_password_strength(password):
    """Проверка сложности пароля"""
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Длина должна быть не менее 8 символов")
    
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Добавьте заглавные буквы")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Добавьте цифры")
    
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password):
        score += 1
    else:
        feedback.append("Добавьте специальные символы")
    
    levels = {
        0: "Очень слабый",
        1: "Слабый",
        2: "Средний",
        3: "Хороший",
        4: "Отличный"
    }
    
    return {
        'score': score,
        'level': levels.get(score, "Неизвестно"),
        'feedback': feedback
    }

def validate_registration(username, email, password, confirm_password, agree_terms):
    """Валидация данных регистрации"""
    errors = []
    
    if not username:
        errors.append("Введите логин")
    elif len(username) < 3:
        errors.append("Логин должен быть не менее 3 символов")
    
    if email and "@" not in email:
        errors.append("Введите корректный email")
    
    if not password:
        errors.append("Введите пароль")
    elif len(password) < 8:
        errors.append("Пароль должен быть не менее 8 символов")
    
    if password != confirm_password:
        errors.append("Пароли не совпадают")
    
    if not agree_terms:
        errors.append("Примите условия использования")
    
    if errors:
        for error in errors:
            st.error(error)
        return False
    
    return True

def register_user(username, email, password):
    """Регистрация пользователя (заглушка)"""
    # В реальном приложении здесь была бы запись в базу данных
    # с хэшированием пароля
    pass

def show_main_app():
    """Главное приложение"""
    with st.sidebar:
        st.success(f"👋 Привет, {st.session_state.user['name']}!")
        
        menu = st.radio(
            "📌 Навигация",
            [
                "📊 Дашборд",
                "🎯 Мои цели", 
                "💸 Транзакции",
                "⚡ Оптимизация",
                "📈 Прогноз",
                "⚙️ Анализ"
            ]
        )
        
        st.markdown("---")
        if st.button("🚪 Выйти", type="secondary", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    
    # Загружаем данные
    transaction_df = load_transaction_data()
    
    if transaction_df.empty:
        st.error("Не удалось загрузить данные. Проверьте файл data/csvjson.json")
        return
    
    # Отображаем выбранную страницу
    if menu == "📊 Дашборд":
        show_dashboard(transaction_df)
    elif menu == "🎯 Мои цели":
        show_goals_page(transaction_df)
    elif menu == "💸 Транзакции":
        show_transactions_page(transaction_df)
    elif menu == "⚡ Оптимизация":
        show_optimization_page(transaction_df)
    elif menu == "📈 Прогноз":
        show_forecast_page(transaction_df)
    elif menu == "⚙️ Анализ":
        show_analysis_page(transaction_df)

def show_dashboard(df):
    """Дашборд с данными из csvjson.json"""
    st.header("📊 Финансовый дашборд")
    
    # Расчет статистики
    summary = get_financial_summary(df)
    
    # Ключевые метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Всего транзакций", summary['transaction_count'])
    
    with col2:
        st.metric("📈 Общий доход", f"{summary['total_income']:,.2f} ₽")
    
    with col3:
        st.metric("📉 Общие расходы", f"{summary['total_expense']:,.2f} ₽")
    
    with col4:
        st.metric("💵 Баланс", f"{summary['balance']:+,.2f} ₽")
    
    st.markdown("---")
    
    # Последние транзакции
    st.subheader("💸 Последние операции")
    
    recent_df = df.sort_values('date', ascending=False).head(10).copy()
    recent_df['Дата'] = recent_df['date'].dt.strftime('%d.%m.%Y')
    recent_df['Сумма'] = recent_df['amount'].apply(lambda x: f"{x:+,.2f} ₽")
    recent_df['Тип'] = recent_df['type'].apply(lambda x: '📈 Доход' if x == 'income' else '📉 Трата')
    
    st.dataframe(
        recent_df[['Дата', 'Тип', 'category', 'Сумма', 'description']],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # Анализ расходов по категориям
    st.subheader("📊 Расходы по категориям")
    
    if not summary['expense_by_category'].empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Таблица
            expense_df = pd.DataFrame({
                'Категория': summary['expense_by_category'].index,
                'Сумма': summary['expense_by_category'].values
            }).sort_values('Сумма', ascending=False)
            
            st.dataframe(
                expense_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Сумма": st.column_config.NumberColumn(
                        format="%.2f ₽"
                    )
                }
            )
        
        with col2:
            # Круговая диаграмма
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(
                summary['expense_by_category'].values,
                labels=summary['expense_by_category'].index,
                autopct='%1.1f%%',
                startangle=90
            )
            ax.set_title('Распределение расходов')
            ax.axis('equal')
            st.pyplot(fig)

def show_goals_page(df):
    """Страница целей на основе данных"""
    st.header("🎯 Финансовые цели")
    
    # Автоматические цели на основе расходов
    auto_goals = get_goals_progress(df)
    
    st.info("💡 Цели созданы автоматически на основе ваших расходов по категориям")
    
    # Показываем автоматические цели
    if auto_goals:
        st.subheader("📋 Автоматические цели")
        
        for goal in auto_goals:
            with st.container():
                progress = goal['saved'] / (goal['current'] - goal['target']) if (goal['current'] - goal['target']) > 0 else 0
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"#### {goal['name']}")
                    st.progress(min(progress, 1.0))
                    st.caption(f"Текущие расходы: {goal['current']:,.0f} ₽ | Цель: {goal['target']:,.0f} ₽")
                
                with col2:
                    remaining = goal['current'] - goal['target']
                    st.metric("Нужно сократить", f"{remaining:,.0f} ₽")
                
                with col3:
                    st.metric("Приоритет", goal['priority'])
                
                st.divider()
    
    # Ручные цели пользователя
    st.subheader("➕ Создать свою цель")
    
    with st.form("custom_goal_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            goal_name = st.text_input("Название цели")
            goal_amount = st.number_input("Сумма цели (руб)", 10000, step=1000)
        
        with col2:
            goal_category = st.selectbox(
                "Категория",
                ['Накопления', 'Инвестиции', 'Обучение', 'Путешествия', 'Другое']
            )
            months = st.slider("Срок (месяцев)", 1, 36, 12)
        
        if st.form_submit_button("Добавить цель"):
            st.session_state.custom_goals.append({
                'name': goal_name,
                'amount': goal_amount,
                'category': goal_category,
                'months': months,
                'saved': 0,
                'created': datetime.now().strftime('%Y-%m-%d')
            })
            st.success(f"Цель '{goal_name}' добавлена!")
            st.rerun()
    
    # Показываем ручные цели
    if st.session_state.custom_goals:
        st.subheader("📝 Мои цели")
        
        for goal in st.session_state.custom_goals:
            progress = goal['saved'] / goal['amount'] if goal['amount'] > 0 else 0
            monthly = goal['amount'] / goal['months']
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{goal['name']}** ({goal['category']})")
                st.progress(min(progress, 1.0))
                st.caption(f"Накоплено: {goal['saved']:,.0f} ₽ из {goal['amount']:,.0f} ₽")
            
            with col2:
                st.metric("В месяц", f"{monthly:,.0f} ₽")

def show_transactions_page(df):
    """Страница транзакций"""
    st.header("💸 Транзакции")
    
    # Проверяем наличие колонки date
    if 'date' not in df.columns:
        st.error("В данных отсутствует колонка 'date'")
        st.write("Доступные колонки:", df.columns.tolist())
        return
    
    # Фильтры
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "Начальная дата",
            df['date'].min().date() if not df.empty else datetime.now().date()
        )
    
    with col2:
        end_date = st.date_input(
            "Конечная дата", 
            df['date'].max().date() if not df.empty else datetime.now().date()
        )
    
    with col3:
        categories = ['Все'] + sorted(df['category'].unique().tolist())
        selected_category = st.selectbox("Категория", categories)
    
    # Применяем фильтры
    filtered_df = df.copy()
    filtered_df = filtered_df[
        (filtered_df['date'].dt.date >= start_date) & 
        (filtered_df['date'].dt.date <= end_date)
    ]
    
    if selected_category != 'Все':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    # Показываем транзакции
    if not filtered_df.empty:
        # Статистика
        st.subheader("📈 Статистика за период")
        
        period_income = filtered_df[filtered_df['type'] == 'income']['amount'].sum()
        period_expense = abs(filtered_df[filtered_df['type'] == 'expense']['amount'].sum())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Количество", len(filtered_df))
        
        with col2:
            st.metric("Доходы", f"{period_income:,.2f} ₽")
        
        with col3:
            st.metric("Расходы", f"{period_expense:,.2f} ₽")
        
        # Таблица транзакций
        st.subheader("📋 Детали транзакций")
        
        display_df = filtered_df.copy()
        display_df['Дата'] = display_df['date'].dt.strftime('%d.%m.%Y')
        display_df['Сумма'] = display_df['amount'].apply(lambda x: f"{x:+,.2f} ₽")
        display_df['Тип'] = display_df['type'].apply(lambda x: '📈 Доход' if x == 'income' else '📉 Трата')
        
        # СОРТИРОВКА ИСПРАВЛЕНА: сортируем по исходной колонке date, а не по переименованной
        display_df = display_df.sort_values('date', ascending=False)
        
        st.dataframe(
            display_df[['Дата', 'Тип', 'category', 'Сумма', 'description']],
            use_container_width=True,
            hide_index=True
        )
        
        # Топ-5 самых крупных трат
        st.subheader("🔥 Топ-5 самых крупных трат")
        
        top_expenses = filtered_df[filtered_df['type'] == 'expense'].copy()
        if not top_expenses.empty:
            top_expenses = top_expenses.nsmallest(5, 'amount')
            
            top_display = top_expenses.copy()
            top_display['Дата'] = top_display['date'].dt.strftime('%d.%m.%Y')
            top_display['Сумма'] = top_display['amount'].apply(lambda x: f"{x:+,.2f} ₽")
            top_display['abs_amount'] = top_display['amount'].abs()
            top_display = top_display.sort_values('abs_amount', ascending=False)
            
            st.dataframe(
                top_display[['Дата', 'category', 'Сумма', 'description']],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("Нет транзакций за выбранный период")

def show_optimization_page(df):
    """Страница оптимизации расходов"""
    st.header("⚡ Оптимизация расходов")
    
    if df.empty:
        st.info("Нет данных для анализа")
        return
    
    expense_by_category = df[df['type'] == 'expense'].groupby('category')['amount'].sum().abs()
    
    if expense_by_category.empty:
        st.info("Нет данных о расходах")
        return
    
    st.subheader("📊 Ваши текущие расходы по категориям")
    
    # Показываем расходы и предлагаем оптимизацию
    optimization_suggestions = []
    
    for category, amount in expense_by_category.items():
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.write(f"**{category}**")
        
        with col2:
            st.metric("В месяц", f"{amount:,.0f} ₽")
        
        with col3:
            reduction = st.slider(
                f"Сократить %",
                0, 50, 0, 5,
                key=f"opt_{category}",
                label_visibility="collapsed"
            )
            
            if reduction > 0:
                savings = amount * reduction / 100
                optimization_suggestions.append({
                    'category': category,
                    'current': amount,
                    'reduction': reduction,
                    'savings': savings
                })
    
    st.markdown("---")
    
    # Расчет эффекта оптимизации
    if optimization_suggestions:
        total_savings = sum(item['savings'] for item in optimization_suggestions)
        
        st.success(f"💰 **Общая экономия: {total_savings:,.0f} руб/мес**")
        
        # Показываем детали
        with st.expander("📋 Детали оптимизации"):
            for item in optimization_suggestions:
                st.write(f"**{item['category']}**: -{item['reduction']}% = {item['savings']:.0f} руб/мес")
        
        # Расчет влияния на цели
        st.subheader("🎯 Влияние на ваши цели")
        
        # Предполагаем, что сэкономленные деньги идут в накопления
        if st.session_state.custom_goals:
            for goal in st.session_state.custom_goals[:3]:  # Первые 3 цели
                remaining = goal['amount'] - goal['saved']
                
                # Без оптимизации
                base_monthly = goal['amount'] / goal['months'] if goal['months'] > 0 else 0
                months_without = remaining / base_monthly if base_monthly > 0 else 999
                
                # С оптимизацией
                months_with = remaining / (base_monthly + total_savings) if (base_monthly + total_savings) > 0 else 999
                
                faster_by = months_without - months_with
                
                if faster_by > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            f"Без оптимизации",
                            f"{months_without:.1f} мес"
                        )
                    
                    with col2:
                        st.metric(
                            f"С оптимизацией",
                            f"{months_with:.1f} мес",
                            delta=f"-{faster_by:.1f} мес"
                        )
                    
                    st.divider()
        else:
            st.info("Создайте цели чтобы увидеть полный эффект оптимизации")
    else:
        st.warning("Выберите категории для сокращения чтобы увидеть эффект")

def show_forecast_page(df):
    """Страница прогноза"""
    st.header("📈 Прогноз накоплений")
    
    if df.empty:
        st.info("Нет данных для прогноза")
        return
    
    # Анализ текущих доходов и расходов
    monthly_income = df[df['type'] == 'income']['amount'].sum() / 3  # Предполагаем 3 месяца данных
    monthly_expense = abs(df[df['type'] == 'expense']['amount'].sum()) / 3
    
    current_savings_rate = monthly_income - monthly_expense
    
    st.subheader("📊 Текущая ситуация")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Средний доход", f"{monthly_income:,.0f} ₽/мес")
    
    with col2:
        st.metric("📉 Средние расходы", f"{monthly_expense:,.0f} ₽/мес")
    
    with col3:
        st.metric("💵 Текущее накопление", f"{current_savings_rate:,.0f} ₽/мес")
    
    st.markdown("---")
    
    # Прогноз для целей
    if st.session_state.custom_goals:
        st.subheader("🎯 Прогноз по вашим целям")
        
        for goal in st.session_state.custom_goals:
            remaining = goal['amount'] - goal['saved']
            
            # Параметры прогноза
            col1, col2 = st.columns(2)
            
            with col1:
                monthly_input = st.number_input(
                    f"Ежемесячное накопление для '{goal['name']}'",
                    min_value=1000.0,
                    value=float(current_savings_rate) if current_savings_rate > 0 else 10000.0,
                    step=1000.0,
                    key=f"monthly_{goal['name']}"
                )
            
            with col2:
                return_rate = st.slider(
                    "Доходность инвестиций (% годовых)",
                    0.0, 15.0, 7.0, 0.5,
                    key=f"return_{goal['name']}"
                )
            
            # Расчеты
            months_no_invest = remaining / monthly_input if monthly_input > 0 else 999
            
            # С инвестициями
            monthly_return = return_rate / 12 / 100
            if monthly_return > 0:
                n = 0
                current = goal['saved']
                while current < goal['amount'] and n < 600:
                    current = current * (1 + monthly_return) + monthly_input
                    n += 1
                months_with_invest = n
            else:
                months_with_invest = months_no_invest
            
            # Отображение
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Без инвестиций",
                    f"{months_no_invest:.1f} мес"
                )
            
            with col2:
                st.metric(
                    f"С инвестициями ({return_rate}%)",
                    f"{months_with_invest:.1f} мес",
                    delta=f"-{months_no_invest - months_with_invest:.1f} мес"
                )
            
            st.divider()
    else:
        st.info("Создайте финансовые цели чтобы увидеть прогноз")

def show_analysis_page(df):
    """Страница углубленного анализа"""
    st.header("⚙️ Детальный анализ")
    
    if df.empty:
        st.info("Нет данных для анализа")
        return
    
    # Анализ по времени
    st.subheader("📅 Анализ по времени")
    
    df['month'] = df['date'].dt.to_period('M')
    monthly_data = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
    
    if not monthly_data.empty:
        # График доходов и расходов по месяцам
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if 'income' in monthly_data.columns:
            ax.plot(monthly_data.index.astype(str), monthly_data['income'], label='Доходы', marker='o')
        
        if 'expense' in monthly_data.columns:
            ax.plot(monthly_data.index.astype(str), abs(monthly_data['expense']), label='Расходы', marker='s')
        
        ax.set_xlabel('Месяц')
        ax.set_ylabel('Сумма (руб)')
        ax.set_title('Динамика доходов и расходов')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
    
    # Анализ привычек
    st.subheader("📊 Анализ финансовых привычек")
    
    # Самые частые категории трат
    frequent_categories = df[df['type'] == 'expense']['category'].value_counts().head(5)
    
    if not frequent_categories.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Самые частые категории трат:**")
            for category, count in frequent_categories.items():
                st.write(f"• {category}: {count} раз")
        
        with col2:
            # Дни недели с наибольшими тратами
            df['weekday'] = df['date'].dt.day_name()
            weekday_expenses = df[df['type'] == 'expense'].groupby('weekday')['amount'].sum().abs()
            
            if not weekday_expenses.empty:
                st.write("**Траты по дням недели:**")
                for day, amount in weekday_expenses.sort_values(ascending=False).items():
                    st.write(f"• {day}: {amount:,.0f} руб")
    
    # Рекомендации
    st.subheader("💡 Рекомендации")
    
    expense_by_category = df[df['type'] == 'expense'].groupby('category')['amount'].sum().abs()
    
    if not expense_by_category.empty:
        # Находим категорию с наибольшими расходами
        max_category = expense_by_category.idxmax()
        max_amount = expense_by_category.max()
        
        st.info(f"**Основная статья расходов:** {max_category} ({max_amount:,.0f} руб)")
        
        # Простые рекомендации
        recommendations = [
            f"Рассмотрите возможность сокращения расходов на {max_category}",
            "Автоматизируйте накопления: настройте автоперевод 10% от дохода",
            "Ведите учет ежедневных мелких расходов",
            "Установите лимиты по категориям расходов",
            "Планируйте крупные покупки заранее"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")

if __name__ == "__main__":
    main()