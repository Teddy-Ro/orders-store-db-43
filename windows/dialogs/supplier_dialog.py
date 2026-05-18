from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox
from database.queries import add_supplier, update_supplier

class SupplierDialog(QDialog):
    def __init__(self, parent=None, supplier_data=None):
        super().__init__(parent)
        self.supplier_id = supplier_data[0] if supplier_data else None
        self.setWindowTitle("Редактирование поставщика" if supplier_data else "Новый поставщик")
        self.setFixedSize(350, 300)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.in_company = QLineEdit()
        self.in_contact = QLineEdit()
        self.in_phone = QLineEdit()
        self.in_details = QTextEdit()
        self.in_details.setMaximumHeight(80)

        form_layout.addRow("Название компании *:", self.in_company)
        form_layout.addRow("Контактное лицо:", self.in_contact)
        form_layout.addRow("Телефон:", self.in_phone)
        form_layout.addRow("Реквизиты/Детали:", self.in_details)

        layout.addLayout(form_layout)

        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_save.setStyleSheet("background-color: #2da44e; color: white; padding: 5px; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_data)
        layout.addWidget(self.btn_save)

        if supplier_data:
            self.in_company.setText(str(supplier_data[1] or ""))
            self.in_contact.setText(str(supplier_data[2] or ""))
            self.in_phone.setText(str(supplier_data[3] or ""))
            self.in_details.setText(str(supplier_data[4] or ""))

    def save_data(self):
        company = self.in_company.text().strip()
        contact = self.in_contact.text().strip()
        phone = self.in_phone.text().strip()
        details = self.in_details.toPlainText().strip()

        # Проверки (Валидация)
        if not company or len(company) < 2:
            QMessageBox.warning(self, "Внимание", "Название компании должно содержать минимум 2 символа!")
            self.in_company.setFocus()
            return

        if phone:
            import re
            phone_pattern = re.compile(r'^[\+\(\)\s\-0-9]+$')
            if not phone_pattern.match(phone) or len(phone) < 5:
                QMessageBox.warning(self, "Внимание", "Некорректный формат телефона!")
                self.in_phone.setFocus()
                return

        try:
            if self.supplier_id:
                update_supplier(self.supplier_id, company, contact or None, phone or None, details or None)
            else:
                add_supplier(company, contact or None, phone or None, details or None)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить:\n{e}")