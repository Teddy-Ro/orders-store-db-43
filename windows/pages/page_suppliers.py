from PyQt6.QtWidgets import (QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QMessageBox, QMenu, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from database.queries import get_all_suppliers, delete_supplier
from windows.dialogs.supplier_dialog import SupplierDialog

class PageSuppliers(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("<h3>База поставщиков</h3>"))

        toolbar.addWidget(QLabel("🔍 Поиск:"))
        self.in_search = QLineEdit()
        self.in_search.setFixedWidth(200)
        self.in_search.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.in_search)

        toolbar.addStretch()
        
        self.btn_add = QPushButton("➕ Добавить поставщика")
        self.btn_add.clicked.connect(self.add_supplier)
        toolbar.addWidget(self.btn_add)

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_data) # Или load_orders, как называется твоя функция
        toolbar.addWidget(self.btn_refresh)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Компания", "Контактное лицо", "Телефон", "Детали"])
        self.table.setColumnWidth(0, 50)   # ID
        self.table.setColumnWidth(1, 220)  # Компания
        self.table.setColumnWidth(2, 180)  # Контактное лицо
        self.table.setColumnWidth(3, 130)  # Телефон
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        try:
            suppliers = get_all_suppliers()
            self.table.setRowCount(len(suppliers))
            for row_idx, row_data in enumerate(suppliers):
                for col_idx, cell_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data if cell_data is not None else "")))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{e}")
        
    def filter_table(self, text):
        search_text = text.lower()
        for row in range(self.table.rowCount()): # Убедись, что твоя таблица называется self.table
            row_visible = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break
            self.table.setRowHidden(row, not row_visible)

    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item: return
        row = item.row()
        
        menu = QMenu()
        edit_action = menu.addAction("✏️ Изменить")
        delete_action = menu.addAction("❌ Удалить")
        
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.edit_supplier(row)
        elif action == delete_action:
            self.delete_supplier(row)

    def add_supplier(self):
        if SupplierDialog(self).exec():
            self.load_data()

    def edit_supplier(self, row):
        supplier_data = [self.table.item(row, i).text() for i in range(5)]
        if SupplierDialog(self, supplier_data).exec():
            self.load_data()

    def delete_supplier(self, row):
        sup_id = self.table.item(row, 0).text()
        sup_name = self.table.item(row, 1).text()

        if QMessageBox.question(self, 'Подтверждение', f"Удалить поставщика '{sup_name}'?") == QMessageBox.StandardButton.Yes:
            try:
                delete_supplier(sup_id)
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", "Нельзя удалить: к поставщику привязаны товары или документы!")