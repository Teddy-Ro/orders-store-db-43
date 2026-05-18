from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QComboBox
from database.queries import add_employee, update_employee

class EmployeeDialog(QDialog):
    def __init__(self, parent=None, emp_data=None):
        super().__init__(parent)
        self.emp_id = emp_data[0] if emp_data else None
        self.setWindowTitle("Редактирование сотрудника" if emp_data else "Новый сотрудник")
        self.setFixedSize(350, 250)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.in_name = QLineEdit()
        self.in_pos = QLineEdit()
        self.in_log = QLineEdit()
        self.in_pwd = QLineEdit()
        self.combo_lvl = QComboBox()
        self.combo_lvl.addItems(["1 - Администратор", "2 - Продавец", "3 - Курьер"])

        form.addRow("ФИО *:", self.in_name)
        form.addRow("Должность:", self.in_pos)
        form.addRow("Логин *:", self.in_log)
        form.addRow("Пароль *:", self.in_pwd)
        form.addRow("Доступ:", self.combo_lvl)
        layout.addLayout(form)

        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_save.clicked.connect(self.save_data)
        layout.addWidget(self.btn_save)

        if emp_data:
            self.in_name.setText(str(emp_data[1]))
            self.in_pos.setText(str(emp_data[2] or ""))
            self.in_log.setText(str(emp_data[3]))
            self.in_pwd.setText(str(emp_data[4]))
            # Устанавливаем нужный индекс в комбобоксе (1, 2 или 3) -> индексы 0, 1, 2
            self.combo_lvl.setCurrentIndex(int(emp_data[5]) - 1)

    def save_data(self):
        name = self.in_name.text().strip()
        log = self.in_log.text().strip()
        pwd = self.in_pwd.text().strip()
        lvl = self.combo_lvl.currentIndex() + 1 # Индекс 0 -> Уровень 1

        if len(name) < 2 or len(log) < 3 or len(pwd) < 3:
            QMessageBox.warning(self, "Ошибка", "ФИО (от 2 симв.), Логин (от 3 симв.) и Пароль (от 3 симв.) обязательны!")
            return

        try:
            if self.emp_id: update_employee(self.emp_id, name, self.in_pos.text() or None, log, pwd, lvl)
            else: add_employee(name, self.in_pos.text() or None, log, pwd, lvl)
            self.accept()
        except Exception as e:
            if "unique" in str(e).lower(): QMessageBox.warning(self, "Ошибка", "Такой логин уже существует!")
            else: QMessageBox.critical(self, "Ошибка", f"Ошибка БД:\n{e}")