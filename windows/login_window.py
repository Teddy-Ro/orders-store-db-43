from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from database.queries import check_login

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему ERP")
        self.setFixedSize(350, 220)
        # Убираем кнопку закрытия "Х", чтобы нельзя было войти без авторизации
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        
        self.user_info = None # Тут сохраним данные успешного входа

        # Интерфейс
        layout = QVBoxLayout()
        layout.setSpacing(10)

        layout.addWidget(QLabel("Логин сотрудника:"))
        self.txt_login = QLineEdit()
        self.txt_login.setPlaceholderText("Введите логин...")
        layout.addWidget(self.txt_login)

        layout.addWidget(QLabel("Пароль:"))
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Введите пароль...")
        layout.addWidget(self.txt_password)

        self.btn_enter = QPushButton("Войти")
        self.btn_enter.setStyleSheet("background-color: #2da44e; color: white; font-weight: bold; padding: 6px;")
        self.btn_enter.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_enter)

        self.btn_exit = QPushButton("Выход")
        self.btn_exit.clicked.connect(self.reject) # Закрывает программу полностью
        layout.addWidget(self.btn_exit)

        self.setLayout(layout)

    def handle_login(self):
        login = self.txt_login.text().strip()
        password = self.txt_password.text().strip()

        # Хардкодный KISS-вариант для тестов (если база пустая или лень искать логин из Faker)
        if login == "a" and password == "":
            self.user_info = (0, "Главный Администратор", 1, "Разработчик")
            self.accept()
            return
        elif login == "s" and password == "":
            self.user_info = (0, "Иван Продавец", 2, "Менеджер")
            self.accept()
            return

        # Проверка через реальную БД
        try:
            result = check_login(login, password)
            if result:
                self.user_info = result
                self.accept() # Закрывает окно и возвращает QDialog.DialogCode.Accepted
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка при проверке данных:\n{e}")