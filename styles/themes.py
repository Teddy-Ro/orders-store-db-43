def get_theme_stylesheet(mode="dark"):
    """
    Возвращает полный QSS-стиль для приложения на основе выбранной темы.
    mode: "dark" или "light"
    """
    if mode == "dark":
        # Палитра Catppuccin / Modern Dark
        bg_main = "#1e1e2e"       # Главный фон окна
        bg_sidebar = "#11111b"    # Фон левой панели
        bg_card = "#181825"       # Фон карточек и таблиц
        border_color = "#313244"  # Цвет границ
        text_main = "#cdd6f4"     # Основной текст
        text_muted = "#a6adc8"    # Второстепенный текст
        accent = "#38bdf8"        # Акцентный голубой цвет
        btn_hover = "#2563eb"
    else:
        # Палитра Modern Light
        bg_main = "#f1f5f9"       # Светло-серый фон
        bg_sidebar = "#ffffff"    # Белоснежный сайдбар
        bg_card = "#ffffff"       # Белые карточки
        border_color = "#cbd5e1"  # Серые границы
        text_main = "#0f172a"     # Темный текст
        text_muted = "#64748b"    # Серый текст
        accent = "#0284c7"        # Насыщенный синий акцент
        btn_hover = "#1d4ed8"

    # Сборка глобального стиля приложения (QSS — аналог CSS для Qt)
    return f"""
        QMainWindow, QWidget {{
            background-color: {bg_main};
            color: {text_main};
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 13px;
        }}
        
        /* Стилизация сайдбара */
        QFrame#sidebar {{
            background-color: {bg_sidebar};
            border-right: 1px solid {border_color};
        }}
        
        /* Современные закругленные кнопки меню */
        QPushButton {{
            background-color: transparent;
            color: {text_main};
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            text-align: left;
        }}
        QPushButton:hover {{
            background-color: rgba(128, 128, 128, 0.15);
        }}
        QPushButton:checked {{
            background-color: {accent};
            color: #11111b;
            font-weight: bold;
        }}
        
        /* Кнопки действий (Применить, Обновить) */
        QPushButton#action_btn {{
            background-color: {accent};
            color: #11111b;
            font-weight: bold;
            border-radius: 6px;
            padding: 6px 15px;
        }}
        
        /* Таблицы в стиле Web */
        QTableWidget {{
            background-color: {bg_card};
            border: 1px solid {border_color};
            gridline-color: {border_color};
            border-radius: 8px;
        }}
        QHeaderView::section {{
            background-color: {bg_sidebar};
            color: {text_muted};
            padding: 6px;
            border: none;
            border-bottom: 1px solid {border_color};
            font-weight: bold;
        }}
        
        /* Поля ввода */
        QLineEdit, QDateEdit, QSpinBox {{
            background-color: {bg_card};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 5px;
            color: {text_main};
        }}
        QLineEdit:focus, QDateEdit:focus {{
            border: 1px solid {accent};
        }}
        
        /* Карточки и Групп-боксы */
        QGroupBox, QFrame#card {{
            background-color: {bg_card};
            border: 1px solid {border_color};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }}
    """