import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

def show_goals_page():
    """Страница управления целями"""
    
    st.header("🎯 Финансовые цели")
    
    # Кнопка создания новой цели
    if st.button("➕ Создать новую цель", type="primary", use_container_width=True):
        st.session_state.show_new_goal_form = True
    
    st.markdown("---")
    
    # Если нажали кнопку создания - показываем форму
    if st.session_state.get('show_new_goal_form', False):
        show_new_goal_form()
        st.markdown("---")
    
    # Список существующих целей
    show_goals_list()

def show_new_goal_form():
    """Форма создания новой цели"""
    st.subheader("📝 Создание новой цели")
    
    with st.form("new_goal_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            goal_name = st.text_input(
                "Название цели *",
                placeholder="Например: Новый iPhone, Отпуск, Авто"
            )
            
            goal_amount = st.number_input(
                "Сумма цели (руб) *",
                min_value=1000,
                value=100000,
                step=1000,
                help="Сколько денег нужно накопить"
            )
            
            current_saved = st.number_input(
                "Уже накоплено (руб)",
                min_value=0,
                value=0,
                step=1000
            )
        
        with col2:
            priority = st.select_slider(
                "Важность цели",
                options=["Низкая", "Средняя", "Высокая", "Критическая"],
                value="Средняя"
            )
            
            urgency = st.select_slider(
                "Срочность",
                options=["Не срочно", "Средняя", "Срочно", "Очень срочно"],
                value="Средняя"
            )
            
            target_date = st.date_input(
                "Желаемая дата достижения",
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=180)
            )
        
        # Дополнительные параметры
        with st.expander("⚙️ Дополнительные настройки"):
            monthly_saving = st.number_input(
                "Планируемое ежемесячное накопление (руб)",
                min_value=1000,
                value=10000,
                step=1000
            )
            
            category = st.selectbox(
                "Категория цели",
                ["Техника", "Путешествия", "Авто", "Недвижимость", "Образование", "Здоровье", "Другое"]
            )
        
        # Кнопки формы
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            submit = st.form_submit_button("✅ Создать цель", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Отмена", use_container_width=True)
        
        if submit:
            if goal_name and goal_amount:
                # Создаем новую цель
                new_goal = {
                    "id": len(st.session_state.goals) + 1,
                    "name": goal_name,
                    "amount": goal_amount,
                    "saved": current_saved,
                    "priority": priority,
                    "urgency": urgency,
                    "target_date": target_date.strftime("%Y-%m-%d"),
                    "category": category,
                    "monthly_saving": monthly_saving,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "active": True
                }
                
                # Расчет времени до цели
                remaining = goal_amount - current_saved
                if monthly_saving > 0:
                    months_needed = remaining / monthly_saving
                    new_goal["estimated_months"] = months_needed
                    new_goal["estimated_date"] = (
                        datetime.now() + timedelta(days=months_needed * 30)
                    ).strftime("%Y-%m-%d")
                
                st.session_state.goals.append(new_goal)
                st.session_state.show_new_goal_form = False
                st.success(f"Цель '{goal_name}' успешно создана!")
                st.rerun()
            else:
                st.error("Заполните обязательные поля (отмечены *)")
        
        if cancel:
            st.session_state.show_new_goal_form = False
            st.rerun()

def show_goals_list():
    """Отображение списка целей"""
    
    if not st.session_state.goals:
        st.info("🎯 У вас пока нет финансовых целей. Создайте первую цель!")
        return
    
    st.subheader("📋 Мои цели")
    
    # Фильтры
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_active = st.checkbox("Только активные", value=True)
    
    with col2:
        sort_by = st.selectbox(
            "Сортировать по",
            ["Приоритету", "Срочности", "Дате создания", "Сумме"]
        )
    
    with col3:
        search_term = st.text_input("Поиск по названию", "")
    
    # Фильтрация целей
    filtered_goals = st.session_state.goals.copy()
    
    if show_active:
        filtered_goals = [g for g in filtered_goals if g.get('active', True)]
    
    if search_term:
        filtered_goals = [
            g for g in filtered_goals 
            if search_term.lower() in g.get('name', '').lower()
        ]
    
    # Сортировка
    if sort_by == "Приоритету":
        priority_order = {"Критическая": 4, "Высокая": 3, "Средняя": 2, "Низкая": 1}
        filtered_goals.sort(key=lambda x: priority_order.get(x.get('priority', 'Низкая'), 1), reverse=True)
    elif sort_by == "Срочности":
        urgency_order = {"Очень срочно": 4, "Срочно": 3, "Средняя": 2, "Не срочно": 1}
        filtered_goals.sort(key=lambda x: urgency_order.get(x.get('urgency', 'Не срочно'), 1), reverse=True)
    elif sort_by == "Дате создания":
        filtered_goals.sort(key=lambda x: x.get('created', ''), reverse=True)
    elif sort_by == "Сумме":
        filtered_goals.sort(key=lambda x: x.get('amount', 0), reverse=True)
    
    # Отображение целей
    for goal in filtered_goals:
        with st.container():
            show_single_goal(goal)
            st.markdown("---")

def show_single_goal(goal):
    """Отображение одной цели"""
    
    # Рассчитываем прогресс
    progress = goal.get('saved', 0) / goal.get('amount', 1)
    remaining = goal.get('amount', 0) - goal.get('saved', 0)
    
    # Цвет прогресс-бара в зависимости от прогресса
    if progress >= 1:
        progress_color = "🎉"
        progress_text = "Цель достигнута!"
    elif progress >= 0.75:
        progress_color = "🟢"
        progress_text = "Почти у цели!"
    elif progress >= 0.5:
        progress_color = "🟡"
        progress_text = "На полпути"
    elif progress >= 0.25:
        progress_color = "🟠"
        progress_text = "Есть прогресс"
    else:
        progress_color = "🔴"
        progress_text = "Только начинаем"
    
    # Основная информация
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        # Заголовок и статус
        status = "✅ " if progress >= 1 else "🎯 "
        st.markdown(f"### {status}{goal.get('name', 'Без названия')}")
        
        # Категория и приоритет
        st.caption(f"📁 {goal.get('category', 'Другое')} | "
                  f"🎯 Приоритет: {goal.get('priority', 'Средняя')} | "
                  f"⏰ Срочность: {goal.get('urgency', 'Средняя')}")
        
        # Прогресс-бар
        st.progress(min(progress, 1.0))
        
        # Текст прогресса
        st.write(f"{progress_color} {progress_text}: "
                f"{goal.get('saved', 0):,} ₽ из {goal.get('amount', 0):,} ₽ "
                f"({progress:.1%})")
    
    with col2:
        # Метрики
        st.metric("💰 Осталось накопить", f"{remaining:,} ₽")
        
        if goal.get('estimated_months'):
            st.metric("📅 Ориентировочно", f"{goal['estimated_months']:.1f} мес")
        
        # Дата цели
        if goal.get('target_date'):
            st.caption(f"📅 Цель до: {goal['target_date']}")
    
    with col3:
        # Кнопки действий
        if st.button("✏️", key=f"edit_{goal['id']}", help="Редактировать"):
            st.session_state.editing_goal = goal['id']
            st.rerun()
        
        if st.button("➕", key=f"add_{goal['id']}", help="Добавить накопления"):
            st.session_state.adding_to_goal = goal['id']
            st.rerun()
        
        if st.button("📊", key=f"stats_{goal['id']}", help="Статистика"):
            st.session_state.viewing_goal_stats = goal['id']
            st.rerun()
        
        if st.button("🗑️", key=f"delete_{goal['id']}", help="Удалить"):
            if st.checkbox(f"Удалить цель '{goal['name']}'?", key=f"confirm_delete_{goal['id']}"):
                st.session_state.goals = [g for g in st.session_state.goals if g['id'] != goal['id']]
                st.rerun()