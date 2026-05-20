import re
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox
from database.queries import add_customer, update_customer

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer_data=None):
        super().__init__(parent)
        self.customer_id = customer_data[0] if customer_data else None
        self.setWindowTitle("Редактирование клиента" if customer_data else "Новый клиент")
        self.setFixedSize(350, 200)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.in_name = QLineEdit()
        self.in_company = QLineEdit()
        self.in_phone = QLineEdit()
        self.in_email = QLineEdit()

        form_layout.addRow("ФИО *:", self.in_name)
        form_layout.addRow("Компания:", self.in_company)
        form_layout.addRow("Телефон:", self.in_phone)
        form_layout.addRow("Email:", self.in_email)

        layout.addLayout(form_layout)

        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_save.setStyleSheet("background-color: #2da44e; color: white; padding: 5px; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_data)
        layout.addWidget(self.btn_save)

        # Если передали данные - заполняем поля для редактирования
        if customer_data:
            self.in_name.setText(str(customer_data[1] or ""))
            self.in_company.setText(str(customer_data[2] or ""))
            self.in_phone.setText(str(customer_data[3] or ""))
            self.in_email.setText(str(customer_data[4] or ""))

    def save_data(self):
        # 1. Считываем данные и обрезаем лишние пробелы по краям
        name = self.in_name.text().strip()
        company = self.in_company.text().strip()
        phone = self.in_phone.text().strip()
        email = self.in_email.text().strip()

        # ==========================================
        # БЛОК ВАЛИДАЦИИ (ПРОВЕРКИ ДАННЫХ)
        # ==========================================

        # Проверка ФИО (Обязательное поле)
        if not name:
            QMessageBox.warning(self, "Внимание", "Поле 'ФИО' обязательно для заполнения!")
            self.in_name.setFocus()
            return
        if len(name) < 2:
            QMessageBox.warning(self, "Внимание", "ФИО слишком короткое. Введите минимум 2 символа.")
            self.in_name.setFocus()
            return

        # Проверка Телефона (Необязательное поле, но если есть - проверяем формат)
        if phone:
            # Разрешаем цифры, плюсы, минусы, скобки и пробелы
            phone_pattern = re.compile(r'^[\+\(\)\s\-0-9]+$')
            if not phone_pattern.match(phone) or len(phone) < 3:
                QMessageBox.warning(self, "Внимание", "Некорректный формат телефона!\nРазрешены только цифры и знаки +, -, ().")
                self.in_phone.setFocus()
                return

        # Проверка Email (Необязательное поле, простая проверка на наличие @ и точки)
        if email:
            email_pattern = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
            if not email_pattern.match(email):
                QMessageBox.warning(self, "Внимание", "Некорректный формат Email!\nПример: user@example.com")
                self.in_email.setFocus()
                return

        # ==========================================
        # СОХРАНЕНИЕ В БАЗУ ДАННЫХ
        # ==========================================
        try:
            # Заменяем пустые строки на None, чтобы в БД записался корректный NULL
            if self.customer_id:
                update_customer(self.customer_id, name, company or None, phone or None, email or None)
            else:
                add_customer(name, company or None, phone or None, email or None)
            
            self.accept() # Успех, закрываем окно
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить данные в базу:\n{e}")