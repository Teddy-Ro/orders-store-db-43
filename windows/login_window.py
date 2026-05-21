from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.queries import check_login

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        # Немного увеличили высоту для комфортного размещения красивых отступов
        self.setFixedSize(360, 280) 
        
        # Убираем кнопку закрытия "Х" и подсказки, оставляя чистое диалоговое окно
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        
        self.user_info = None  # Тут сохраним данные успешного входа

        # Главный слой окна с хорошими рамками
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Крупный современный заголовок приветствия
        lbl_welcome = QLabel("Вход в систему")
        lbl_welcome.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Цвет акцента подхватится автоматически, но мы сделаем его поярче для эффекта
        lbl_welcome.setStyleSheet("color: #38bdf8; margin-bottom: 5px; border: none; background: transparent;")
        main_layout.addWidget(lbl_welcome)

        # --- ВНУТРЕННЯЯ КАРТОЧКА ФОРМЫ ---
        form_card = QFrame()
        # Стилизуем под карточку-контейнер
        form_card.setStyleSheet("QFrame { background-color: rgba(255, 255, 255, 0.02); border: 1px solid #313244; border-radius: 8px; }")
        card_layout = QVBoxLayout(form_card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(8)

        card_layout.addWidget(QLabel("<b>Логин сотрудника:</b>"))
        self.txt_login = QLineEdit()
        self.txt_login.setPlaceholderText("Введите ваш логин...")
        card_layout.addWidget(self.txt_login)

        card_layout.addWidget(QLabel("<b>Пароль:</b>"))
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Введите ваш пароль...")
        card_layout.addWidget(self.txt_password)

        main_layout.addWidget(form_card)

        # --- НИЖНЯЯ ПАНЕЛЬ КНОПОК ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_exit = QPushButton("Выйти")
        # Стилизуем кнопку выхода под мягкий деструктивный оттенок
        self.btn_exit.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: #f38ba8; 
                padding: 8px; 
                font-weight: bold; 
                border: 1px solid #f38ba8; 
                border-radius: 6px; 
            }
            QPushButton:hover { background-color: rgba(243, 139, 168, 0.1); }
        """)
        self.btn_exit.clicked.connect(self.reject) # Закрывает программу полностью
        button_layout.addWidget(self.btn_exit)

        self.btn_enter = QPushButton("Войти в систему")
        # Применяем наш заготовленный стиль экшена из themes.py + красивый зеленый ховер
        self.btn_enter.setStyleSheet("""
            QPushButton { 
                background-color: #22c55e; 
                color: #11111b; 
                font-weight: bold; 
                padding: 8px 20px; 
                border-radius: 6px; 
            }
            QPushButton:hover { background-color: #4ade80; }
        """)
        self.btn_enter.clicked.connect(self.handle_login)
        button_layout.addWidget(self.btn_enter)

        main_layout.addLayout(button_layout)

    def handle_login(self):
        login = self.txt_login.text().strip()
        password = self.txt_password.text().strip()

        # Быстрый KISS-вход для тестов разработки
        if login == "" and password == "":
            self.user_info = (1, "Главный Администратор", 1, "Разработчик")
            self.accept()
            return
        elif login == "s" and password == "":
            self.user_info = (2, "Иван Продавец", 2, "Менеджер")
            self.accept()
            return

        # Проверка через реальную БД
        try:
            result = check_login(login, password)
            if result:
                self.user_info = result
                self.accept() 
            else:
                QMessageBox.warning(self, "Ошибка авторизации", "Неверно указан логин или пароль!")
        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка БД", f"Не удалось подключиться к серверу PostgreSQL:\n{e}")