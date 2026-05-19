from PyQt6.QtWidgets import QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QMenu, QAbstractItemView
from PyQt6.QtCore import Qt
from database.queries import get_all_products, delete_product
from windows.dialogs.product_dialog import ProductDialog

class PageProducts(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("<h3>📦 Каталог товаров</h3>"))
        
        toolbar.addWidget(QLabel("🔍 Поиск:"))
        self.in_search = QLineEdit()
        self.in_search.setFixedWidth(200)
        self.in_search.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.in_search)
        toolbar.addStretch()

        btn_add = QPushButton("➕ Добавить товар"); btn_add.clicked.connect(self.add_prod)
        toolbar.addWidget(btn_add); layout.addLayout(toolbar)
        
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_data) # Или load_orders, как называется твоя функция
        toolbar.addWidget(self.btn_refresh)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Артикул", "Название", "Закупка", "Продажа", "Остаток", "ID Пост-ка"])
        self.table.setColumnWidth(0, 50)   # ID
        self.table.setColumnWidth(1, 100)  # Артикул
        self.table.setColumnWidth(2, 220)  # Название товара
        self.table.setColumnWidth(3, 90)   # Цена закупки
        self.table.setColumnWidth(4, 90)   # Цена продажи
        self.table.setColumnWidth(5, 80)   # Остаток
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_menu)
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        for row, data in enumerate(get_all_products()):
            self.table.insertRow(row)
            for col, cell in enumerate(data): self.table.setItem(row, col, QTableWidgetItem(str(cell if cell else "")))
    
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

    def show_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item: return
        row = item.row()
        menu = QMenu()
        a_edit = menu.addAction("✏️ Изменить"); a_del = menu.addAction("❌ Удалить")
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        if action == a_edit:
            data = [self.table.item(row, i).text() for i in range(7)]
            if ProductDialog(self, data).exec(): self.load_data()
        elif action == a_del:
            if QMessageBox.question(self, 'Удаление', f"Удалить товар {self.table.item(row, 2).text()}?") == QMessageBox.StandardButton.Yes:
                try: delete_product(self.table.item(row, 0).text()); self.load_data()
                except Exception as e: QMessageBox.warning(self, "Ошибка", "Нельзя удалить (товар есть в заказах)!")

    def add_prod(self):
        if ProductDialog(self).exec(): self.load_data()