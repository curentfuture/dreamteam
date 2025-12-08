# main.py - добавь недостающие импорты и логику
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt

# Настройка страницы
st.set_page_config(
    page_title="💰 Умный финансовый помощник",
    page_icon="💰",
    layout="wide"
)

# Инициализация состояния
def init_session_state():
    default_states = {
        'user': None,
        'goals': [],
        'transactions': [],
        'optimization': {},
        'categories': [
            "Кафе/Рестораны", "Продукты", "Транспорт", 
            "Развлечения", "Здоровье", "Образование",
            "Зарплата", "Инвестиции", "Подарки", "Другое"
        ],
        'demo_data_loaded': False
    }
    
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_demo_data():
    """Загрузка демо-данных"""
    if not st.session_state.get('demo_data_loaded', False):
        # Демо-цели
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
        
        # Демо-транзакции
        st.session_state.transactions = [
            {"id": 1, "date": "2024-03-01", "amount": -1500, "category": "Кафе/Рестораны", "description": "Кофе и выпечка"},
            {"id": 2, "date": "2024-03-02", "amount": -3000, "category": "Продукты", "description": "Супермаркет"},
            {"id": 3, "date": "2024-03-03", "amount": 50000, "category": "Зарплата", "description": "ЗП март"},
            {"id": 4, "date": "2024-03-05", "amount": -8000, "category": "Развлечения", "description": "Кино и ужин"},
            {"id": 5, "date": "2024-03-10", "amount": -12000, "category": "Транспорт", "description": "Заправка авто"},
            {"id": 6, "date": "2024-03-12", "amount": -5000, "category": "Здоровье", "description": "Аптека"},
            {"id": 7, "date": "2024-03-15", "amount": 20000, "category": "Инвестиции", "description": "Дивиденды"},
            {"id": 8, "date": "2024-03-20", "amount": -7000, "category": "Образование", "description": "Книги и курсы"},
        ]
        
        st.session_state.demo_data_loaded = True

def main():
    init_session_state()
    
    st.title("💰 Умный финансовый помощник")
    st.markdown("---")
    
    if not st.session_state.user:
        show_auth_page()
    else:
        if st.session_state.user.get('name') == 'Демо':
            load_demo_data()
        show_main_app()

def show_auth_page():
    """Страница авторизации"""
    st.header("🔐 Вход в систему")
    
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        
        if st.button("Войти", type="primary"):
            st.session_state.user = {
                "username": username,
                "name": username
            }
            st.rerun()
    
    with tab2:
        new_user = st.text_input("Новый логин")
        new_pass = st.text_input("Новый пароль", type="password")
        
        if st.button("Зарегистрироваться"):
            st.session_state.user = {"username": new_user, "name": new_user}
            st.rerun()
    
    # Демо-режим
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Демо-режим (с данными)", use_container_width=True):
            st.session_state.user = {"username": "demo", "name": "Демо"}
            load_demo_data()
            st.rerun()
    
    with col2:
        if st.button("🆕 Начать с чистого листа", use_container_width=True):
            st.session_state.user = {"username": "new", "name": "Новый пользователь"}
            st.rerun()

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
                "⚙️ Настройки"
            ]
        )
        
        # Быстрые действия
        st.markdown("---")
        st.markdown("### 🚀 Быстрые действия")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Цель", use_container_width=True):
                st.session_state.show_new_goal = True
                st.rerun()
        
        with col2:
            if st.button("💸 Трата", use_container_width=True):
                st.session_state.show_new_transaction = True
                st.rerun()
        
        # Выход
        st.markdown("---")
        if st.button("🚪 Выйти", type="secondary", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    
    # Основной контент
    if menu == "📊 Дашборд":
        show_dashboard()
    elif menu == "🎯 Мои цели":
        show_goals_page()
    elif menu == "💸 Транзакции":
        show_transactions_page()
    elif menu == "⚡ Оптимизация":
        show_optimization_page()
    elif menu == "📈 Прогноз":
        show_forecast_page()
    elif menu == "⚙️ Настройки":
        show_settings_page()

def show_dashboard():
    """Дашборд"""
    st.header("📊 Финансовый дашборд")
    
    # Базовые метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_goals = len(st.session_state.goals)
        st.metric("🎯 Всего целей", total_goals)
    
    with col2:
        active_goals = len([g for g in st.session_state.goals if g.get('active', True)])
        st.metric("✅ Активных целей", active_goals)
    
    with col3:
        total_needed = sum(g.get('amount', 0) for g in st.session_state.goals)
        st.metric("💰 Общая сумма", f"{total_needed:,} ₽")
    
    with col4:
        total_saved = sum(g.get('saved', 0) for g in st.session_state.goals)
        st.metric("💵 Накоплено", f"{total_saved:,} ₽")
    
    st.markdown("---")
    
    # Последние транзакции
    if st.session_state.transactions:
        st.subheader("💸 Последние операции")
        
        df = pd.DataFrame(st.session_state.transactions[-5:])
        df['Сумма'] = df['amount'].apply(lambda x: f"{x:+,.0f} ₽")
        df['Дата'] = pd.to_datetime(df['date']).dt.strftime('%d.%m.%Y')
        
        st.dataframe(
            df[['Дата', 'category', 'Сумма', 'description']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Дата": "Дата",
                "category": "Категория",
                "Сумма": "Сумма",
                "description": "Описание"
            }
        )

def show_goals_page():
    """Страница целей"""
    st.header("🎯 Финансовые цели")
    
    # Форма создания цели
    if st.button("➕ Создать новую цель", type="primary"):
        st.session_state.show_new_goal = True
    
    if st.session_state.get('show_new_goal', False):
        with st.expander("📝 Новая цель", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                goal_name = st.text_input("Название цели", "Новый iPhone")
                goal_amount = st.number_input("Сумма (руб)", 100000, step=1000)
                current_saved = st.number_input("Уже накоплено", 0, step=1000)
            
            with col2:
                priority = st.select_slider("Важность", ["Низкая", "Средняя", "Высокая", "Критическая"])
                target_date = st.date_input("Цель до", datetime.now() + timedelta(days=180))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Создать", type="primary"):
                    st.session_state.goals.append({
                        "id": len(st.session_state.goals) + 1,
                        "name": goal_name,
                        "amount": goal_amount,
                        "saved": current_saved,
                        "priority": priority,
                        "target_date": target_date.strftime("%Y-%m-%d"),
                        "created": datetime.now().strftime("%Y-%m-%d"),
                        "active": True
                    })
                    st.session_state.show_new_goal = False
                    st.rerun()
            
            with col2:
                if st.button("❌ Отмена"):
                    st.session_state.show_new_goal = False
                    st.rerun()
    
    st.markdown("---")
    
    # Список целей
    if st.session_state.goals:
        st.subheader("📋 Мои цели")
        for goal in st.session_state.goals:
            with st.container():
                progress = goal.get('saved', 0) / goal.get('amount', 1) if goal.get('amount', 0) > 0 else 0
                remaining = goal.get('amount', 0) - goal.get('saved', 0)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"#### {goal['name']}")
                    st.progress(min(progress, 1.0))
                    st.caption(f"{goal.get('saved', 0):,} ₽ из {goal.get('amount', 0):,} ₽ | Приоритет: {goal.get('priority', 'Средняя')}")
                
                with col2:
                    st.metric("Осталось", f"{remaining:,} ₽")
                
                st.divider()
    else:
        st.info("🎯 У вас пока нет целей. Создайте первую цель!")

def show_transactions_page():
    """Страница транзакций с мок-данными"""
    st.header("💸 Управление транзакциями")
    
    # Загрузка мок-данных
    @st.cache_data
    def load_mock_transactions():
        try:
            with open('data/mock_transactions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Создаем DataFrame с транзакциями
            transactions = []
            for category, items in data['categories'].items():
                for item in items:
                    date = datetime.now() - timedelta(days=item['days_ago'])
                    transactions.append({
                        'date': date,
                        'amount': item['amount'],
                        'category': category,
                        'description': item['description'],
                        'type': 'expense' if item['amount'] < 0 else 'income'
                    })
            
            # Добавляем регулярные доходы
            transactions.append({
                'date': datetime.now() - timedelta(days=5),
                'amount': 75000,
                'category': 'Зарплата',
                'description': 'Зарплата',
                'type': 'income'
            })
            
            transactions.append({
                'date': datetime.now() - timedelta(days=35),
                'amount': 65000,
                'category': 'Зарплата',
                'description': 'Зарплата',
                'type': 'income'
            })
            
            return pd.DataFrame(transactions)
        except:
            # Если файла нет, создаем минимальные данные
            return pd.DataFrame([{
                'date': datetime.now() - timedelta(days=10),
                'amount': -5000,
                'category': 'Продукты',
                'description': 'Магазин',
                'type': 'expense'
            }])
    
    # Загружаем мок-данные
    mock_df = load_mock_transactions()
    
    # Объединяем с ручными транзакциями
    if st.session_state.transactions:
        manual_df = pd.DataFrame(st.session_state.transactions)
        manual_df['date'] = pd.to_datetime(manual_df['date'])
        manual_df['type'] = manual_df['amount'].apply(lambda x: 'expense' if x < 0 else 'income')
        
        # Объединяем датафреймы
        all_transactions = pd.concat([mock_df, manual_df], ignore_index=True)
    else:
        all_transactions = mock_df
    
    # Форма добавления транзакции
    if st.button("➕ Добавить транзакцию", type="primary"):
        st.session_state.show_new_transaction = True
    
    if st.session_state.get('show_new_transaction', False):
        with st.expander("📝 Новая транзакция", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                trans_type = st.radio("Тип", ["Трата", "Доход"])
                amount = st.number_input("Сумма (руб)", 1000.0, step=100.0)
                if trans_type == "Трата":
                    amount = -abs(amount)
            
            with col2:
                category = st.selectbox("Категория", st.session_state.categories)
                date = st.date_input("Дата", datetime.now())
                description = st.text_input("Описание", placeholder="На что потратили?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Добавить", type="primary"):
                    new_trans = {
                        "id": len(st.session_state.transactions) + 1,
                        "date": date.strftime("%Y-%m-%d"),
                        "amount": amount,
                        "category": category,
                        "description": description
                    }
                    st.session_state.transactions.append(new_trans)
                    st.session_state.show_new_transaction = False
                    st.success("Транзакция добавлена!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Отмена"):
                    st.session_state.show_new_transaction = False
                    st.rerun()
    
    st.markdown("---")
    
    # Фильтры и анализ
    st.subheader("📊 Анализ транзакций")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Фильтр по периоду
        period = st.selectbox(
            "Период",
            ["Все время", "Последние 30 дней", "Последние 7 дней", "Текущий месяц"]
        )
    
    with col2:
        # Фильтр по категориям
        selected_categories = st.multiselect(
            "Категории",
            st.session_state.categories,
            default=[]
        )
    
    with col3:
        # Фильтр по типу
        filter_type = st.selectbox(
            "Тип",
            ["Все", "Только траты", "Только доходы"]
        )
    
    # Применяем фильтры
    filtered_df = all_transactions.copy()
    
    # Фильтр по периоду
    if period == "Последние 30 дней":
        cutoff_date = datetime.now() - timedelta(days=30)
        filtered_df = filtered_df[filtered_df['date'] >= cutoff_date]
    elif period == "Последние 7 дней":
        cutoff_date = datetime.now() - timedelta(days=7)
        filtered_df = filtered_df[filtered_df['date'] >= cutoff_date]
    elif period == "Текущий месяц":
        current_month = datetime.now().month
        filtered_df = filtered_df[filtered_df['date'].dt.month == current_month]
    
    # Фильтр по категориям
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
    
    # Фильтр по типу
    if filter_type == "Только траты":
        filtered_df = filtered_df[filtered_df['amount'] < 0]
    elif filter_type == "Только доходы":
        filtered_df = filtered_df[filtered_df['amount'] > 0]
    
    # Сортировка по дате
    filtered_df = filtered_df.sort_values('date', ascending=False)
    
    # Отображение результатов
    if not filtered_df.empty:
        # Таблица транзакций
        st.subheader("📋 История транзакций")
        
        display_df = filtered_df.copy()
        display_df['Дата'] = display_df['date'].dt.strftime('%d.%m.%Y')
        display_df['Сумма'] = display_df['amount'].apply(lambda x: f"{x:+,.0f} ₽")
        display_df['Тип'] = display_df['type'].apply(lambda x: '📉 Трата' if x == 'expense' else '📈 Доход')
        
        st.dataframe(
            display_df[['Дата', 'Тип', 'category', 'Сумма', 'description']].head(20),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Дата": "Дата",
                "Тип": "Тип",
                "category": "Категория",
                "Сумма": "Сумма",
                "description": "Описание"
            }
        )
        
        # Статистика
        st.subheader("📈 Статистика")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_count = len(filtered_df)
            st.metric("Всего операций", total_count)
        
        with col2:
            total_income = filtered_df[filtered_df['amount'] > 0]['amount'].sum()
            st.metric("📈 Общий доход", f"{total_income:,.0f} ₽")
        
        with col3:
            total_expense = abs(filtered_df[filtered_df['amount'] < 0]['amount'].sum())
            st.metric("📉 Общие расходы", f"{total_expense:,.0f} ₽")
        
        with col4:
            balance = total_income - total_expense
            st.metric("💰 Баланс", f"{balance:+,.0f} ₽")
        
        # Анализ по категориям
        st.subheader("📊 Расходы по категориям")
        
        expense_by_category = filtered_df[filtered_df['amount'] < 0].groupby('category')['amount'].sum().abs()
        
        if not expense_by_category.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Таца расходов по категориям
                category_df = pd.DataFrame({
                    'Категория': expense_by_category.index,
                    'Сумма': expense_by_category.values
                }).sort_values('Сумма', ascending=False)
                
                st.dataframe(
                    category_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Категория": "Категория",
                        "Сумма": st.column_config.NumberColumn(
                            "Сумма (₽)",
                            format="%d ₽"
                        )
                    }
                )
            
            with col2:
                # Круговая диаграмма
                if len(expense_by_category) > 0:
                    fig, ax = plt.subplots()
                    ax.pie(expense_by_category.values, labels=expense_by_category.index, autopct='%1.1f%%')
                    ax.set_title('Распределение расходов')
                    st.pyplot(fig)
        
        # График расходов по времени
        st.subheader("📅 Динамика расходов")
        
        if not filtered_df.empty:
            # Группировка по дате
            daily_expenses = filtered_df[filtered_df['amount'] < 0].copy()
            daily_expenses['day'] = daily_expenses['date'].dt.date
            daily_totals = daily_expenses.groupby('day')['amount'].sum().abs()
            
            if not daily_totals.empty:
                # Линейный график
                st.line_chart(daily_totals)
    
    else:
        st.info("Нет транзакций по выбранным фильтрам")

def show_optimization_page():
    """Страница оптимизации - ТЕПЕРЬ РАБОТАЕТ!"""
    st.header("⚡ Оптимизация расходов")
    
    st.info("""
    💡 **Как это работает:**
    1. Укажите на сколько процентов готовы сократить каждую категорию расходов
    2. Система рассчитает сколько вы сэкономите в месяц
    3. Увидите как это повлияет на достижение ваших целей
    """)
    
    # Текущие расходы (мок-данные)
    expense_categories = {
        "Кафе/Рестораны": {"amount": 15000, "importance": "Низкая"},
        "Продукты": {"amount": 25000, "importance": "Высокая"},
        "Транспорт": {"amount": 12000, "importance": "Средняя"},
        "Развлечения": {"amount": 8000, "importance": "Низкая"},
        "Подписки": {"amount": 3000, "importance": "Низкая"},
        "Одежда": {"amount": 7000, "importance": "Средняя"}
    }
    
    st.subheader("📊 Ваши текущие расходы")
    
    # Показываем расходы и слайдеры
    optimization_results = {}
    
    for category, data in expense_categories.items():
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.write(f"**{category}**")
            st.caption(f"Важность: {data['importance']}")
        
        with col2:
            st.metric("В месяц", f"{data['amount']:,} руб")
        
        with col3:
            reduction = st.slider(
                f"Сократить %",
                min_value=0,
                max_value=50,
                value=0,
                step=5,
                key=f"opt_{category}",
                label_visibility="collapsed"
            )
            
            if reduction > 0:
                savings = data["amount"] * reduction / 100
                optimization_results[category] = {
                    "savings": savings,
                    "reduction": reduction,
                    "original": data["amount"]
                }
    
    st.markdown("---")
    
    # Кнопка расчета
    if st.button("🧮 Рассчитать эффект оптимизации", type="primary"):
        if optimization_results:
            total_savings = sum(item["savings"] for item in optimization_results.values())
            
            st.success(f"💰 **Общая экономия: {total_savings:,.0f} руб/мес**")
            
            # Показываем детали
            with st.expander("📋 Детали оптимизации"):
                for category, data in optimization_results.items():
                    st.write(f"**{category}**: -{data['reduction']}% = {data['savings']:.0f} руб/мес")
            
            # Влияние на цели
            if st.session_state.goals:
                st.subheader("🎯 Влияние на ваши цели")
                
                for goal in st.session_state.goals:
                    remaining = goal["amount"] - goal["saved"]
                    
                    # Без оптимизации (предположим что откладываем 10% от средней зарплаты)
                    base_monthly_saving = 15000  # пример
                    months_without = remaining / base_monthly_saving if base_monthly_saving > 0 else 999
                    
                    # С оптимизацией
                    months_with = remaining / (base_monthly_saving + total_savings) if (base_monthly_saving + total_savings) > 0 else 999
                    
                    faster_by = months_without - months_with
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            f"Без оптимизации",
                            f"{months_without:.1f} мес",
                            delta=f"{(datetime.now() + timedelta(days=months_without*30)).strftime('%d.%m.%Y')}"
                        )
                    
                    with col2:
                        st.metric(
                            f"С оптимизацией",
                            f"{months_with:.1f} мес",
                            delta=f"-{faster_by:.1f} мес"
                        )
                    
                    with col3:
                        percent_faster = (faster_by / months_without) * 100 if months_without > 0 else 0
                        st.metric(
                            "Эффект",
                            f"{percent_faster:.0f}% быстрее",
                            delta=f"{faster_by:.1f} мес"
                        )
                    
                    st.divider()
            else:
                st.info("🎯 Создайте финансовую цель чтобы увидеть эффект оптимизации!")
        else:
            st.warning("Выберите категории для сокращения чтобы увидеть эффект")

def show_forecast_page():
    """Страница прогноза - ТЕПЕРЬ РАБОТАЕТ!"""
    st.header("📈 Прогноз накоплений")
    
    if not st.session_state.goals:
        st.info("🎯 Сначала создайте финансовую цель на странице 'Мои цели'")
        return
    
    # Выбор цели
    goal_names = [f"{g['name']} ({g['amount']:,} руб)" for g in st.session_state.goals]
    selected_goal_idx = st.selectbox("Выберите цель", range(len(goal_names)), format_func=lambda x: goal_names[x])
    
    if selected_goal_idx is not None:
        goal = st.session_state.goals[selected_goal_idx]
        remaining = goal["amount"] - goal["saved"]
        
        st.subheader(f"Прогноз для: {goal['name']}")
        st.write(f"💰 Осталось накопить: **{remaining:,} руб**")
        
        # Параметры прогноза
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_saving = st.number_input(
                "Ежемесячное накопление (руб)",
                min_value=1000,
                value=15000,
                step=1000,
                help="Сколько готовы откладывать каждый месяц"
            )
        
        with col2:
            investment_return = st.slider(
                "Доходность инвестиций (% годовых)",
                min_value=0.0,
                max_value=15.0,
                value=7.0,
                step=0.5,
                help="Предполагаемая доходность инвестиций"
            )
        
        # Расчеты
        st.markdown("---")
        
        # Простой расчет (без инвестиций)
        months_no_invest = remaining / monthly_saving if monthly_saving > 0 else 999
        
        # Расчет с инвестициями (упрощенная формула)
        monthly_rate = investment_return / 12 / 100
        if monthly_rate > 0:
            # FV = PV * (1 + r)^n + PMT * ((1 + r)^n - 1) / r
            # Решаем для n (количество месяцев)
            try:
                # Используем численное решение
                n = 0
                current = goal["saved"]
                while current < goal["amount"] and n < 600:  # максимум 50 лет
                    current = current * (1 + monthly_rate) + monthly_saving
                    n += 1
                months_with_invest = n
            except:
                months_with_invest = months_no_invest
        else:
            months_with_invest = months_no_invest
        
        # Отображение результатов
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Без инвестиций",
                f"{months_no_invest:.1f} мес",
                delta=f"{(datetime.now() + timedelta(days=months_no_invest*30)).strftime('%d.%m.%Y')}"
            )
        
        with col2:
            st.metric(
                f"С инвестициями ({investment_return}%)",
                f"{months_with_invest:.1f} мес",
                delta=f"-{months_no_invest - months_with_invest:.1f} мес"
            )
        
        with col3:
            percent_faster = ((months_no_invest - months_with_invest) / months_no_invest) * 100 if months_no_invest > 0 else 0
            st.metric(
                "Выгода",
                f"{percent_faster:.0f}% быстрее",
                delta="Инвестиции ускоряют!"
            )
        
        # График накоплений
        st.subheader("📊 График накоплений")
        
        # Генерируем данные для графика
        months_to_plot = int(min(max(months_no_invest, months_with_invest), 60)) + 1  # максимум 5 лет
        
        timeline = list(range(months_to_plot + 1))
        
        # Без инвестиций
        savings_no_invest = [goal["saved"]]
        for i in range(months_to_plot):
            new_amount = savings_no_invest[-1] + monthly_saving
            savings_no_invest.append(min(goal["amount"], new_amount))
        
        # С инвестициями
        savings_with_invest = [goal["saved"]]
        for i in range(months_to_plot):
            new_amount = savings_with_invest[-1] * (1 + monthly_rate) + monthly_saving
            savings_with_invest.append(min(goal["amount"], new_amount))
        
        # Создаем DataFrame для графика
        chart_data = pd.DataFrame({
            "Месяц": timeline * 2,
            "Накопления": savings_no_invest + savings_with_invest,
            "Сценарий": ["Без инвестиций"] * len(timeline) + [f"С инвестициями ({investment_return}%)"] * len(timeline)
        })
        
        # Линейный график
        st.line_chart(chart_data, x="Месяц", y="Накопления", color="Сценарий")
        
        # Дополнительная информация
        with st.expander("💡 Рекомендации по инвестициям"):
            st.write("""
            **Консервативная стратегия (3-6% годовых):**
            - Банковские вклады
            - Облигации федерального займа (ОФЗ)
            - Корпоративные облигации
            
            **Умеренная стратегия (6-10% годовых):**
            - ETF на индексы (S&P 500, МосБиржи)
            - Дивидендные акции
            - ПИФы
            
            **Агрессивная стратегия (10%+ годовых):**
            - Акции роста
            - Венчурные инвестиции
            - Криптовалюты (высокий риск!)
            
            ⚠️ **Важно:** Чем выше потенциальная доходность, тем выше риски.
            """)

def show_settings_page():
    """Настройки"""
    st.header("⚙️ Настройки")
    
    with st.expander("📁 Категории расходов"):
        st.write("Настройте категории для лучшего анализа расходов")
        
        # Показываем текущие категории
        st.write("**Текущие категории:**")
        cols = st.columns(3)
        for i, category in enumerate(st.session_state.categories):
            with cols[i % 3]:
                if st.button(f"🗑️ {category}", key=f"del_{category}"):
                    if category not in ["Зарплата", "Другое"]:
                        st.session_state.categories.remove(category)
                        st.rerun()
        
        # Добавление новой категории
        st.markdown("---")
        new_category = st.text_input("Добавить новую категорию")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("➕ Добавить категорию"):
                if new_category and new_category not in st.session_state.categories:
                    st.session_state.categories.append(new_category)
                    st.success(f"Категория '{new_category}' добавлена!")
                    st.rerun()
        
        with col2:
            if st.button("🔄 Сбросить"):
                st.session_state.categories = [
                    "Кафе/Рестораны", "Продукты", "Транспорт", 
                    "Развлечения", "Здоровье", "Образование",
                    "Зарплата", "Инвестиции", "Подарки", "Другое"
                ]
                st.success("Категории сброшены!")
                st.rerun()
    
    with st.expander("🧹 Очистка данных"):
        st.warning("⚠️ Это действие нельзя отменить!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Очистить все цели", type="secondary"):
                st.session_state.goals = []
                st.success("Все цели удалены!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Очистить все транзакции", type="secondary"):
                st.session_state.transactions = []
                st.success("Все транзакции удалены!")
                st.rerun()

if __name__ == "__main__":
    main()