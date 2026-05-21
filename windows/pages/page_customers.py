from PyQt6.QtWidgets import (QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QMessageBox, QMenu, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from database.queries import get_all_customers, delete_customer
from windows.dialogs.customer_dialog import CustomerDialog

class PageCustomers(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Панель инструментов
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("<h3>База клиентов</h3>"))

        toolbar.addWidget(QLabel("🔍 Поиск:"))
        self.in_search = QLineEdit()
        self.in_search.setFixedWidth(200)
        self.in_search.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.in_search)

        toolbar.addStretch()
        
        self.btn_add = QPushButton("➕ Добавить клиента")
        self.btn_add.clicked.connect(self.add_customer)
        toolbar.addWidget(self.btn_add)

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_data)
        toolbar.addWidget(self.btn_refresh)
        layout.addLayout(toolbar)

        # Таблица (Только для чтения!)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Компания", "Телефон", "Email"])
        self.table.setColumnWidth(0, 50)   # ID
        self.table.setColumnWidth(1, 220)  # ФИО (делаем шире)
        self.table.setColumnWidth(2, 150)  # Компания
        self.table.setColumnWidth(3, 130)  # Телефон
        self.table.setColumnWidth(4, 130)  # Email
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Настройка контекстного меню (ПКМ)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        """Загрузка данных в таблицу"""
        self.table.setRowCount(0)
        try:
            customers = get_all_customers()
            self.table.setRowCount(len(customers))
            for row_idx, row_data in enumerate(customers):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data if cell_data is not None else ""))
                    self.table.setItem(row_idx, col_idx, item)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{e}")

    def filter_table(self, text):
        search_text = text.lower()
        for row in range(self.table.rowCount()):
            row_visible = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break
            self.table.setRowHidden(row, not row_visible)

    def show_context_menu(self, position):
        """Отрисовка выпадающего меню при нажатии ПКМ"""
        # Проверяем, кликнули ли мы по существующей строке
        item = self.table.itemAt(position)
        if not item:
            return

        row = item.row()
        
        # Создаем меню
        menu = QMenu()
        edit_action = QAction("✏️ Изменить", self)
        delete_action = QAction("❌ Удалить", self)
        
        menu.addAction(edit_action)
        menu.addAction(delete_action)

        # Показываем меню и ждем выбор
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.edit_customer(row)
        elif action == delete_action:
            self.delete_customer(row)

    def add_customer(self):
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.load_data()

    def edit_customer(self, row):
        # Собираем данные из выделенной строки
        customer_data = [self.table.item(row, i).text() for i in range(5)]
        
        dialog = CustomerDialog(self, customer_data)
        if dialog.exec():
            self.load_data()

    def delete_customer(self, row):
        customer_id = self.table.item(row, 0).text()
        customer_name = self.table.item(row, 1).text()

        reply = QMessageBox.question(self, 'Подтверждение', f"Удалить клиента '{customer_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_customer(customer_id)
                self.load_data()
            except Exception as e:
                if "violates foreign key constraint" in str(e):
                    QMessageBox.warning(self, "Ошибка", "Нельзя удалить клиента: у него есть заказы!")