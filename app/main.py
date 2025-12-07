import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import app.auth as auth
import app.goals as goals

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Настройка страницы
st.set_page_config(
    page_title="💰 Умный финансовый помощник",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация session_state
def init_session_state():
    """Инициализация состояния приложения"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'goals' not in st.session_state:
        st.session_state.goals = []
    if 'transactions' not in st.session_state:
        st.session_state.transactions = []
    if 'optimization' not in st.session_state:
        st.session_state.optimization = {}
    if 'categories' not in st.session_state:
        st.session_state.categories = [
            "Кафе/Рестораны", "Продукты", "Транспорт", 
            "Развлечения", "Здоровье", "Образование",
            "Зарплата", "Инвестиции", "Подарки", "Другое"
        ]

def main():
    """Основная функция приложения"""
    init_session_state()
    
    # Заголовок приложения
    st.title("💰 Умный финансовый помощник")
    st.markdown("---")
    
    # Если пользователь не авторизован - показываем страницу входа
    if not st.session_state.user:
        auth.show_auth_page()
    else:
        show_main_app()

def show_main_app():
    """Главное приложение после авторизации"""
    
    # Сайдбар с навигацией
    with st.sidebar:
        st.success(f"👋 Привет, {st.session_state.user.get('name', 'Пользователь')}!")
        
        # Меню навигации
        page = st.radio(
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
            if st.button("➕ Новая цель", use_container_width=True):
                st.session_state.new_goal = True
                st.rerun()
        with col2:
            if st.button("💸 Добавить трату", use_container_width=True):
                st.session_state.new_transaction = True
                st.rerun()
        
        # Выход
        st.markdown("---")
        if st.button("🚪 Выйти", type="secondary", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    
    # Основной контент в зависимости от выбранной страницы
    if page == "📊 Дашборд":
        show_dashboard()
    elif page == "🎯 Мои цели":
        goals.show_goals_page()
    elif page == "💸 Транзакции":
        transactions.show_transactions_page()
    elif page == "⚡ Оптимизация":
        optimization.show_optimization_page()
    elif page == "📈 Прогноз":
        forecast.show_forecast_page()
    elif page == "⚙️ Настройки":
        show_settings_page()

def show_dashboard():
    """Дашборд с основной информацией"""
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
    
    # Быстрый прогресс по целям
    if st.session_state.goals:
        st.subheader("📈 Прогресс по целям")
        
        for goal in st.session_state.goals[:3]:  # Показываем только первые 3
            with st.container():
                progress = goal.get('saved', 0) / goal.get('amount', 1)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{goal.get('name', 'Без названия')}**")
                    st.progress(min(progress, 1.0))
                    st.caption(f"{goal.get('saved', 0):,} ₽ из {goal.get('amount', 0):,} ₽")
                with col2:
                    remaining = goal.get('amount', 0) - goal.get('saved', 0)
                    st.metric("Осталось", f"{remaining:,} ₽")
        
        if len(st.session_state.goals) > 3:
            st.info(f"📋 ... и еще {len(st.session_state.goals) - 3} целей")
    else:
        st.info("🎯 У вас пока нет финансовых целей. Создайте первую цель!")
    
    st.markdown("---")
    
    # Последние транзакции
    if st.session_state.transactions:
        st.subheader("💸 Последние транзакции")
        
        # Преобразуем в DataFrame для удобства
        df = pd.DataFrame(st.session_state.transactions[-5:])  # Последние 5
        
        # Форматируем
        df['amount_formatted'] = df['amount'].apply(lambda x: f"{x:+,.0f} ₽")
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%d.%m.%Y')
        
        # Показываем таблицу
        st.dataframe(
            df[['date', 'category', 'amount_formatted', 'description']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "date": "Дата",
                "category": "Категория",
                "amount_formatted": "Сумма",
                "description": "Описание"
            }
        )
    else:
        st.info("💸 Транзакций пока нет. Добавьте первую!")

def show_settings_page():
    """Страница настроек"""
    st.header("⚙️ Настройки")
    
    with st.expander("📁 Категории расходов", expanded=True):
        st.write("Настройте свои категории для лучшего анализа")
        
        # Редактирование категорий
        new_category = st.text_input("Добавить новую категорию")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("➕ Добавить категорию"):
                if new_category and new_category not in st.session_state.categories:
                    st.session_state.categories.append(new_category)
                    st.success(f"Категория '{new_category}' добавлена!")
                    st.rerun()
        
        with col2:
            if st.button("🔄 Сбросить к стандартным"):
                st.session_state.categories = [
                    "Кафе/Рестораны", "Продукты", "Транспорт", 
                    "Развлечения", "Здоровье", "Образование",
                    "Зарплата", "Инвестиции", "Подарки", "Другое"
                ]
                st.success("Категории сброшены!")
                st.rerun()
        
        # Список текущих категорий
        st.markdown("**Текущие категории:**")
        cols = st.columns(3)
        for i, category in enumerate(st.session_state.categories):
            with cols[i % 3]:
                if st.button(f"🗑️ {category}", key=f"del_{category}"):
                    if category not in ["Зарплата", "Другое"]:
                        st.session_state.categories.remove(category)
                        st.rerun()
    
    with st.expander("🔐 Безопасность", expanded=False):
        st.write("Настройки безопасности")
        current_password = st.text_input("Текущий пароль", type="password")
        new_password = st.text_input("Новый пароль", type="password")
        confirm_password = st.text_input("Подтвердите пароль", type="password")
        
        if st.button("Изменить пароль", type="primary"):
            if new_password == confirm_password:
                st.success("Пароль успешно изменен!")
            else:
                st.error("Пароли не совпадают")

if __name__ == "__main__":
    main()