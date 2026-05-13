import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout)
from database.queries import init_database, get_all_customers
from database.seeder import generate_fake_data # Импортируем наш новый генератор

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Магазин заказов (MVP)")
        self.resize(700, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Панель с кнопками
        btn_layout = QHBoxLayout()
        self.btn_init_db = QPushButton("1. Сбросить таблицы (DDL)")
        self.btn_seed_db = QPushButton("2. Сгенерировать данные") # Новая кнопка
        self.btn_load_data = QPushButton("3. Показать Клиентов")
        
        btn_layout.addWidget(self.btn_init_db)
        btn_layout.addWidget(self.btn_seed_db)
        btn_layout.addWidget(self.btn_load_data)

        self.btn_init_db.clicked.connect(self.setup_database)
        self.btn_seed_db.clicked.connect(self.seed_database)
        self.btn_load_data.clicked.connect(self.load_customers)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Компания", "Телефон"])
        # Растягиваем столбцы
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

    def setup_database(self):
        try:
            init_database()
            QMessageBox.information(self, "Успех", "Таблицы успешно пересозданы!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать таблицы:\n{e}")

    def seed_database(self):
        """Обработчик кнопки генерации данных"""
        try:
            generate_fake_data()
            QMessageBox.information(self, "Успех", "База данных заполнена тестовыми данными!")
            # Автоматически обновляем таблицу, чтобы сразу увидеть результат
            self.load_customers() 
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации:\n{e}")

    def load_customers(self):
        try:
            customers = get_all_customers()
            self.table.setRowCount(len(customers))
            for row_idx, row_data in enumerate(customers):
                for col_idx, cell_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())