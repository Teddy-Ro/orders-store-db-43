from PyQt6.QtWidgets import (QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QMenu, 
                             QAbstractItemView, QSplitter, QTextEdit)
from PyQt6.QtCore import Qt
from database.queries import get_all_products, delete_product
from windows.dialogs.product_dialog import ProductDialog

class PageProducts(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Orientation.Vertical)

        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("<h3>📦 Каталог товаров</h3>"))
        
        toolbar.addWidget(QLabel("🔍 Поиск:"))
        self.in_search = QLineEdit()
        self.in_search.setFixedWidth(200)
        self.in_search.setPlaceholderText("Артикул или название...")
        self.in_search.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.in_search)

        toolbar.addStretch()

        btn_add = QPushButton("➕ Добавить товар")
        btn_add.clicked.connect(self.add_prod)
        toolbar.addWidget(btn_add)
        
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_data)
        toolbar.addWidget(self.btn_refresh)
        
        top_layout.addLayout(toolbar)

        # 9 колонок в соответствии со схемой
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Артикул", "Название", "Закупка", "Продажа", 
            "Остаток", "Ед. изм.", "Описание", "ID Пост-ка"
        ])
        
        self.table.setColumnWidth(0, 50)   
        self.table.setColumnWidth(1, 100)  
        self.table.setColumnWidth(2, 300)  
        self.table.setColumnWidth(3, 100)   
        self.table.setColumnWidth(4, 100)   
        self.table.setColumnWidth(5, 90)   
        self.table.setColumnWidth(6, 90)   
        
        # Скрываем описание и ID поставщика из таблицы
        self.table.setColumnHidden(7, True)
        self.table.setColumnHidden(8, True)
        
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.table.itemSelectionChanged.connect(self.show_details)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_menu)
        top_layout.addWidget(self.table)
        
        splitter.addWidget(top_container)

        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        
        lbl_desc_title = QLabel("📝 ХАРАКТЕРИСТИКИ И ОПИСАНИЕ ТОВАРА")
        lbl_desc_title.setStyleSheet("color: #a6adc8; font-weight: bold; font-size: 11px;")
        bottom_layout.addWidget(lbl_desc_title)
        
        self.text_details = QTextEdit()
        self.text_details.setReadOnly(True)
        self.text_details.setPlaceholderText("Выберите товар из таблицы выше, чтобы просмотреть подробную информацию...")
        bottom_layout.addWidget(self.text_details)
        
        splitter.addWidget(bottom_container)
        splitter.setSizes([450, 150])
        layout.addWidget(splitter)
        
        self.load_data()

    def load_data(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for row, data in enumerate(get_all_products()):
            self.table.insertRow(row)
            for col, cell in enumerate(data): 
                val = "" if cell is None else str(cell)
                self.table.setItem(row, col, QTableWidgetItem(val))
        self.table.blockSignals(False)
        self.text_details.clear()

    def show_details(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.text_details.clear()
            return
            
        row = selected_items[0].row()
        name = self.table.item(row, 2).text()
        unit = self.table.item(row, 6).text() or "шт."
        desc = self.table.item(row, 7).text() or "Описание отсутствует."
        
        info_text = f"📦 Товар: {name}\n📐 Единица измерения: {unit}\n\n📖 Описание:\n{desc}"
        self.text_details.setText(info_text)

    def filter_table(self, text):
        search_text = text.lower()
        for row in range(self.table.rowCount()):
            row_visible = False
            for col in [1, 2]: # Ищем только по Артикулу и Названию
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
        a_edit = menu.addAction("✏️ Изменить")
        a_del = menu.addAction("❌ Удалить")
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        
        if action == a_edit:
            data = [self.table.item(row, i).text() for i in range(9)]
            if ProductDialog(self, data).exec(): 
                self.load_data()
        elif action == a_del:
            if QMessageBox.question(self, 'Удаление', f"Удалить товар {self.table.item(row, 2).text()}?") == QMessageBox.StandardButton.Yes:
                try: 
                    delete_product(self.table.item(row, 0).text())
                    self.load_data()
                except Exception as e: 
                    QMessageBox.warning(self, "Ошибка", "Нельзя удалить (товар есть в заказах)!")

    def add_prod(self):
        if ProductDialog(self).exec(): 
            self.load_data()