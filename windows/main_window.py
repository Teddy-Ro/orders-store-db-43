import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QFrame, QStackedWidget, QLabel, QPushButton, QButtonGroup, QApplication)
from PyQt6.QtCore import Qt

from styles.themes import get_theme_stylesheet

from windows.pages.page_customers import PageCustomers
from windows.pages.page_suppliers import PageSuppliers
from windows.pages.page_employees import PageEmployees
from windows.pages.page_products import PageProducts
from windows.pages.page_orders import PageOrders
from windows.pages.page_orders_history import PageOrdersHistory
from windows.pages.page_courier import PageCourier
from windows.pages.page_analytics import PageAnalytics
from windows.pages.page_developer import PageDeveloper

class MainWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.user_id, self.user_name, self.access_level, self.user_position = user_info
        self.setWindowTitle(f"Orders Store ERP — [{self.user_position} {self.user_name}]")
        self.resize(1100, 650)
        self.is_logged_out = False

        # --- АВТОМАТИЧЕСКОЕ ОПРЕДЕЛЕНИЕ СИСТЕМНОЙ ТЕМЫ ОС ---
        is_os_dark = QApplication.instance().palette().window().color().value() < 128
        self.current_theme = "dark" if is_os_dark else "light"

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==================== ЛЕВАЯ ПАНЕЛЬ (САЙДБАР) ====================
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)

        lbl_profile = QLabel(f"{self.user_name}\n\n{self.user_position}")
        lbl_profile.setStyleSheet("font-weight: bold; border: none;")
        lbl_profile.setWordWrap(True)
        sidebar_layout.addWidget(lbl_profile)
        sidebar_layout.addSpacing(30)

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("border: none;")

        self.menu_group = QButtonGroup(self)
        self.menu_group.setExclusive(True)

        page_welcome = QWidget()
        lbl_w = QLabel("Выберите раздел в меню слева", page_welcome)
        lbl_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_w.setStyleSheet("font-size: 14px; color: gray;")
        QVBoxLayout(page_welcome).addWidget(lbl_w)
        self.content_stack.addWidget(page_welcome)

        # --- ДИНАМИЧЕСКОЕ ДОБАВЛЕНИЕ СТРАНИЦ ПО ПРАВАМ ДОСТУПА ---
        def add_menu_item(title, widget, allowed_levels):
            if self.access_level in allowed_levels:
                idx = self.content_stack.addWidget(widget)
                
                btn = QPushButton(title)
                btn.setCheckable(True)
                btn.clicked.connect(lambda ch, i=idx: self.content_stack.setCurrentIndex(i))
                
                self.menu_group.addButton(btn)
                sidebar_layout.addWidget(btn)

        # Наполнение модулей ERP системы
        add_menu_item("Сборка заказа", PageOrders(user_info), [1, 2])
        add_menu_item("История заказов", PageOrdersHistory(user_info), [1, 2])
        add_menu_item("База клиентов", PageCustomers(), [1, 2])
        add_menu_item("Каталог товаров", PageProducts(), [1, 2])
        add_menu_item("Доставки курьера", PageCourier(user_info), [1, 3])
        add_menu_item("Поставщики", PageSuppliers(), [1]) 
        add_menu_item("Сотрудники", PageEmployees(), [1])
        add_menu_item("Аналитика и отчеты", PageAnalytics(), [1])
        add_menu_item("Панель разработчика", PageDeveloper(), [1])

        sidebar_layout.addStretch()

        # === КНОПКА ПЕРЕКЛЮЧЕНИЯ ТЕМЫ (ТЁМНАЯ / СВЕТЛАЯ) ===
        self.btn_theme = QPushButton("🌓 Сменить тему")
        self.btn_theme.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme)

        # КНОПКА ВЫХОДА ИЗ СИСТЕМЫ
        self.btn_logout = QPushButton("Выйти из системы")
        self.btn_logout.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.btn_logout)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack)

        self.apply_theme()

    def apply_theme(self):
        """Запрашивает актуальный стиль из styles.themes и мгновенно перерисовывает все окна"""
        qss_style = get_theme_stylesheet(self.current_theme)
        QApplication.instance().setStyleSheet(qss_style)

    def toggle_theme(self):
        """Циклически меняет флаг темы и обновляет графический интерфейс"""
        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"
        self.apply_theme()

    def logout(self):
        """Полный безопасный перезапуск приложения для смены пользователя"""
        self.close()
        os.execl(sys.executable, sys.executable, *sys.argv)