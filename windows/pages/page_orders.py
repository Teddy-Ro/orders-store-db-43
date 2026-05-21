from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, 
                             QLineEdit, QSpinBox, QHeaderView, QFrame, QFormLayout, QMenu, QAbstractItemView, QCompleter, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.queries import get_customers_for_search, get_products_for_search, create_order_transaction
from windows.dialogs.customer_dialog import CustomerDialog

class PageOrders(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.seller_id = user_info[0] 
        self.cart_items = {} 

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # =====================================================================
        # ЗОНА 1: КАРТОЧКА КЛИЕНТА И ДОСТАВКИ
        # =====================================================================
        box_client = QGroupBox("Данные клиента и доставки")
        box_client.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_client_box = QVBoxLayout(box_client)
        layout_client_box.setContentsMargins(15, 15, 15, 15)

        client_inner_layout = QHBoxLayout()
        form_client = QFormLayout()
        form_client.setSpacing(10)

        self.combo_name = QComboBox()
        self.combo_phone = QComboBox()
        self.combo_email = QComboBox()
        self.in_address = QLineEdit()

        for combo in [self.combo_name, self.combo_phone, self.combo_email]:
            combo.setEditable(True)
            combo.setMinimumWidth(280)
            combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            
            completer = combo.completer()
            if completer:
                completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
                completer.setFilterMode(Qt.MatchFlag.MatchContains)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            
            combo.activated.connect(self.sync_client_combos)

        self.combo_name.setPlaceholderText("Поиск по ФИО...")
        self.combo_phone.setPlaceholderText("Поиск по телефону...")
        self.combo_email.setPlaceholderText("Поиск по Email...")
        self.in_address.setPlaceholderText("Укажите точный адрес доставки для этого заказа...")

        form_client.addRow("ФИО клиента:", self.combo_name)
        form_client.addRow("Телефон:", self.combo_phone)
        form_client.addRow("Email:", self.combo_email)
        form_client.addRow("Адрес доставки:", self.in_address)
        client_inner_layout.addLayout(form_client)

        vbox_new_client = QVBoxLayout()
        self.btn_new_client = QPushButton("➕ Новый клиент")
        self.btn_new_client.setObjectName("action_btn")
        self.btn_new_client.setFixedWidth(150)
        self.btn_new_client.clicked.connect(self.add_new_client)
        vbox_new_client.addWidget(self.btn_new_client)
        vbox_new_client.addStretch()
        client_inner_layout.addLayout(vbox_new_client)
        
        client_inner_layout.addStretch()
        layout_client_box.addLayout(client_inner_layout)
        layout.addWidget(box_client)

        # =====================================================================
        # ЗОНА 2: КАРТОЧКА ВЫБОРА ТОВАРОВ
        # =====================================================================
        box_product = QGroupBox("Подбор товаров в корзину")
        box_product.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_product_box = QVBoxLayout(box_product)
        layout_product_box.setContentsMargins(15, 15, 15, 15)

        row_prod = QHBoxLayout()
        row_prod.setSpacing(12)

        self.combo_product = QComboBox()
        self.combo_product.setEditable(True)
        self.combo_product.setMinimumWidth(450)
        self.combo_product.setPlaceholderText("Введите артикул или название товара для быстрого поиска...")
        self.combo_product.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        completer_prod = self.combo_product.completer()
        if completer_prod:
            completer_prod.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer_prod.setFilterMode(Qt.MatchFlag.MatchContains)
            completer_prod.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            
        self.combo_product.currentIndexChanged.connect(self.on_product_selected)

        self.spin_qty = QSpinBox()
        self.spin_qty.setMinimum(1)
        self.spin_qty.setFixedWidth(80)
        
        self.lbl_stock_info = QLabel("Доступно: 0")
        self.lbl_stock_info.setStyleSheet("color: #a6adc8; font-style: italic;")

        self.btn_add_to_cart = QPushButton("🛒 Добавить в заказ")
        self.btn_add_to_cart.setObjectName("action_btn")
        self.btn_add_to_cart.setFixedWidth(180)
        self.btn_add_to_cart.clicked.connect(self.add_to_cart)
        
        row_prod.addWidget(QLabel("Выбор товара:"))
        row_prod.addWidget(self.combo_product)
        row_prod.addWidget(QLabel("Кол-во:"))
        row_prod.addWidget(self.spin_qty)
        row_prod.addWidget(self.lbl_stock_info)
        row_prod.addStretch()
        row_prod.addWidget(self.btn_add_to_cart)
        layout_product_box.addLayout(row_prod)
        layout.addWidget(box_product)

        # =====================================================================
        # ЗОНА 3: ТАБЛИЦА С КОРЗИНОЙ ЗАКАЗА
        # =====================================================================
        self.table_cart = QTableWidget(0, 6)
        self.table_cart.setHorizontalHeaderLabels(["ID", "Артикул", "Название товара", "Цена за шт.", "Количество (✏️)", "Итоговая сумма"])
        
        self.table_cart.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_cart.setColumnWidth(0, 60)   # ID
        self.table_cart.setColumnWidth(1, 110)  # Артикул
        self.table_cart.setColumnWidth(3, 110)  # Цена
        self.table_cart.setColumnWidth(4, 140)  # Кол-во
        self.table_cart.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.table_cart.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_cart.cellChanged.connect(self.on_cell_changed)
        
        self.table_cart.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_cart.customContextMenuRequested.connect(self.show_cart_menu)
        
        layout.addWidget(self.table_cart)

        # =====================================================================
        # ЗОНА 4: ПОДВАЛ И ОФОРМЛЕНИЕ ЧЕКА
        # =====================================================================
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(5, 5, 5, 5)
        
        self.btn_clear = QPushButton("🗑 Очистить форму")
        self.btn_clear.setStyleSheet("padding: 8px 15px; color: #f38ba8;")
        self.btn_clear.clicked.connect(self.clear_form)
        
        self.lbl_total = QLabel("Итого к оплате: 0.00 руб.")
        self.lbl_total.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        self.lbl_total.setStyleSheet("color: #a6e3a1; margin-right: 15px;")
        
        self.btn_checkout = QPushButton("🚀 Сформировать и отправить заказ")
        self.btn_checkout.setStyleSheet("""
            QPushButton { 
                background-color: #22c55e; 
                color: #11111b; 
                font-weight: bold; 
                padding: 10px 25px; 
                font-size: 13px; 
                border-radius: 6px; 
            }
            QPushButton:hover { background-color: #4ade80; }
        """)
        self.btn_checkout.clicked.connect(self.checkout)
        
        footer_layout.addWidget(self.btn_clear)
        footer_layout.addStretch()
        footer_layout.addWidget(self.lbl_total)
        footer_layout.addWidget(self.btn_checkout)
        layout.addLayout(footer_layout)

        self.load_dropdowns()

    # =====================================================================
    # БИЗНЕС-ЛОГИКА СТРАНИЦЫ (ПОЛНОСТЬЮ СОХРАНЕНА)
    # =====================================================================
    def load_dropdowns(self):
        self.combo_name.clear()
        self.combo_phone.clear()
        self.combo_email.clear()
        
        for cust in get_customers_for_search():
            c_id, name, phone, email = cust
            self.combo_name.addItem(name, c_id) 
            self.combo_phone.addItem(phone or "—", c_id)
            self.combo_email.addItem(email or "—", c_id)
            
        self.combo_product.clear()
        for prod in get_products_for_search():
            text = f"[{prod[1]}] {prod[2]} — {prod[3]:.2f} руб."
            self.combo_product.addItem(text, {'id': prod[0], 'price': prod[3], 'stock': prod[4], 'unit': prod[5]})
        
        self.combo_name.setCurrentIndex(-1)
        self.combo_phone.setCurrentIndex(-1)
        self.combo_email.setCurrentIndex(-1)
        self.combo_product.setCurrentIndex(-1)

    def sync_client_combos(self, index):
        if index < 0: return
        self.combo_name.blockSignals(True)
        self.combo_phone.blockSignals(True)
        self.combo_email.blockSignals(True)

        self.combo_name.setCurrentIndex(index)
        self.combo_phone.setCurrentIndex(index)
        self.combo_email.setCurrentIndex(index)

        self.combo_name.blockSignals(False)
        self.combo_phone.blockSignals(False)
        self.combo_email.blockSignals(False)

    def add_new_client(self):
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.load_dropdowns()
            last_idx = self.combo_name.count() - 1
            if last_idx >= 0:
                self.sync_client_combos(last_idx)

    def on_product_selected(self):
        idx = self.combo_product.currentIndex()
        if idx >= 0:
            prod_data = self.combo_product.itemData(idx)
            stock = prod_data['stock']
            self.spin_qty.setMaximum(stock)
            self.lbl_stock_info.setText(f"Доступно: {stock} {prod_data['unit']}")
        else:
            self.spin_qty.setMaximum(1)
            self.lbl_stock_info.setText("Доступно: 0")

    def add_to_cart(self):
        idx = self.combo_product.currentIndex()
        if idx < 0: return

        prod_data = self.combo_product.itemData(idx)
        prod_id = prod_data['id']
        qty = self.spin_qty.value()

        if prod_id in self.cart_items:
            new_qty = self.cart_items[prod_id]['qty'] + qty
            if new_qty > prod_data['stock']:
                QMessageBox.warning(self, "Ошибка", "Нельзя добавить больше, чем есть на складе!")
                return
            self.cart_items[prod_id]['qty'] = new_qty
        else:
            text = self.combo_product.currentText()
            art = text.split(']')[0][1:]
            name = text.split('] ')[1]
            self.cart_items[prod_id] = {
                'art': art, 'name': name, 'price': prod_data['price'], 'qty': qty, 'stock': prod_data['stock']
            }

        self.update_cart_table()

    def on_cell_changed(self, row, column):
        if column != 4: return
        try:
            p_id = int(self.table_cart.item(row, 0).text())
            qty_str = self.table_cart.item(row, column).text().strip()
            new_qty = int(qty_str)
            if new_qty <= 0: raise ValueError
        except (ValueError, AttributeError):
            QMessageBox.warning(self, "Ошибка", "Количество должно быть целым числом больше нуля!")
            self.update_cart_table()
            return

        max_stock = self.cart_items[p_id]['stock']
        if new_qty > max_stock:
            QMessageBox.warning(self, "Превышение остатка", f"На складе доступно всего {max_stock} шт.!")
            self.update_cart_table()
            return

        self.cart_items[p_id]['qty'] = new_qty
        self.update_cart_table()

    def update_cart_table(self):
        self.table_cart.blockSignals(True)
        self.table_cart.setRowCount(0)
        total_sum = 0

        for p_id, data in self.cart_items.items():
            row = self.table_cart.rowCount()
            self.table_cart.insertRow(row)
            
            summa = data['price'] * data['qty']
            total_sum += summa

            item_id = QTableWidgetItem(str(p_id))
            item_art = QTableWidgetItem(data['art'])
            item_name = QTableWidgetItem(data['name'])
            item_price = QTableWidgetItem(f"{data['price']:.2f}")
            item_qty = QTableWidgetItem(str(data['qty']))
            item_sum = QTableWidgetItem(f"{summa:.2f}")

            for item in [item_id, item_art, item_name, item_price, item_sum]:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            item_qty.setFlags(item_qty.flags() | Qt.ItemFlag.ItemIsEditable)

            self.table_cart.setItem(row, 0, item_id)
            self.table_cart.setItem(row, 1, item_art)
            self.table_cart.setItem(row, 2, item_name)
            self.table_cart.setItem(row, 3, item_price)
            self.table_cart.setItem(row, 4, item_qty)
            self.table_cart.setItem(row, 5, item_sum)

        self.lbl_total.setText(f"Итого к оплате: {total_sum:.2f} руб.")
        self.table_cart.blockSignals(False)

    def show_cart_menu(self, pos):
        item = self.table_cart.itemAt(pos)
        if not item: return
        row = item.row()
        p_id = int(self.table_cart.item(row, 0).text())
        
        menu = QMenu()
        action_del = menu.addAction("❌ Удалить из заказа полностью")
        action = menu.exec(self.table_cart.viewport().mapToGlobal(pos))
        
        if action == action_del:
            del self.cart_items[p_id]
            self.update_cart_table()

    def clear_form(self):
        self.cart_items.clear()
        self.update_cart_table()
        self.in_address.clear()
        self.combo_name.setCurrentIndex(-1)
        self.combo_phone.setCurrentIndex(-1)
        self.combo_email.setCurrentIndex(-1)
        self.combo_product.setCurrentIndex(-1)

    def checkout(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста!")
            return
            
        c_idx = self.combo_name.currentIndex()
        if c_idx < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента!")
            return
            
        address = self.in_address.text().strip()
        if not address:
            QMessageBox.warning(self, "Ошибка", "Укажите адрес доставки!")
            return

        customer_id = self.combo_name.itemData(c_idx)

        items_to_db = []
        for p_id, data in self.cart_items.items():
            items_to_db.append({'product_id': p_id, 'qty': data['qty'], 'price': data['price']})

        try:
            order_id = create_order_transaction(customer_id, self.seller_id, address, items_to_db)
            QMessageBox.information(self, "Успех", f"Заказ №{order_id} успешно оформлен и передан на сборку!")
            self.clear_form()
            self.load_dropdowns() 
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Сбой при оформлении заказа:\n{e}")