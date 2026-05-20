import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QFrame, QStackedWidget, QLabel, QPushButton, QButtonGroup)
from PyQt6.QtCore import Qt
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

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==================== ЛЕВАЯ ПАНЕЛЬ ====================
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        
        # Настройка стилей сайдбара с учетом активного (checked) состояния кнопок
        sidebar.setStyleSheet("""
            QFrame { 
                border-right: 1px solid gray; 
            } 
            QPushButton { 
                text-align: left; 
                padding: 8px 8px 8px 12px; 
                border: none; 
                font-size: 14px; 
            } 
            QPushButton:hover { 
                background-color: rgba(128, 128, 128, 0.15); 
                border-radius: 4px; 
            } 
            QPushButton:checked { 
                background-color: rgba(128, 128, 128, 0.25); 
                font-weight: bold; 
                border-left: 4px solid gray; 
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)

        lbl_profile = QLabel(f"{self.user_name}\n\n{self.user_position}")
        lbl_profile.setStyleSheet("font-weight: bold; margin-bottom: 20px; border: none;")
        lbl_profile.setWordWrap(True)

        sidebar_layout.addWidget(lbl_profile)

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("border: none;")

        # Создаем эксклюзивную группу кнопок для автоматического переключения подсветки
        self.menu_group = QButtonGroup(self)
        self.menu_group.setExclusive(True)

        # Приветственная страница (Индекс 0)
        page_welcome = QWidget()
        lbl_w = QLabel("Выберите раздел в меню слева", page_welcome)
        lbl_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        QVBoxLayout(page_welcome).addWidget(lbl_w)
        self.content_stack.addWidget(page_welcome)

        # --- ФУНКЦИЯ ДОБАВЛЕНИЯ РАЗДЕЛОВ ---
        def add_menu_item(title, widget, allowed_levels):
            if self.access_level in allowed_levels:
                idx = self.content_stack.addWidget(widget)
                
                btn = QPushButton(title)
                btn.setCheckable(True) # Делаем кнопку фиксируемой
                
                # Привязываем клик к смене страницы
                btn.clicked.connect(lambda ch, i=idx: self.content_stack.setCurrentIndex(i))
                
                self.menu_group.addButton(btn)
                sidebar_layout.addWidget(btn)

        # Добавляем модули на панель
        add_menu_item("🛒 Сборка заказа", PageOrders(user_info), [1, 2])
        add_menu_item("📋 История заказов", PageOrdersHistory(user_info), [1, 2])
        add_menu_item("👥 База клиентов", PageCustomers(), [1, 2])
        add_menu_item("📦 Каталог товаров", PageProducts(), [1, 2])
        add_menu_item("🚚 Доставки курьера", PageCourier(user_info), [1, 3])
        add_menu_item("🏭 Поставщики", PageSuppliers(), [1]) 
        add_menu_item("👥 Сотрудники", PageEmployees(), [1])
        add_menu_item("📊 Аналитика и отчеты", PageAnalytics(), [1])
        add_menu_item("🛠 Панель разработчика", PageDeveloper(), [1])

        sidebar_layout.addStretch()

        self.btn_logout = QPushButton("🚪 Выйти")
        # Кнопку выхода не добавляем в общую группу, чтобы она не сбрасывала подсветку вкладок
        self.btn_logout.setStyleSheet("QPushButton:checked { border-left: none; }") 
        self.btn_logout.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.btn_logout)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack)

    def logout(self):
        """Полный перезапуск приложения для смены пользователя"""
        self.close()
        os.execl(sys.executable, sys.executable, *sys.argv)