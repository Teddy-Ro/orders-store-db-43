from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QMessageBox, 
                             QStackedWidget, QFrame, QGridLayout, QHeaderView, QSplitter)
from PyQt6.QtCore import Qt
from database.queries import (get_available_orders, get_active_courier_order, 
                              get_order_items_details, accept_order, complete_order)

class PageCourier(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.courier_id = user_info[0] 
        self.current_order_id = None

        # Главный слой страницы
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # =====================================================================
        # СТРАНИЦА 0: КУРЬЕР СВОБОДЕН (Пул доступных заказов)
        # =====================================================================
        self.page_free = QWidget()
        layout_free = QVBoxLayout(self.page_free)
        layout_free.setContentsMargins(0, 0, 0, 0)
        
        # Тулбар: заголовок + кнопка обновления в одну линию
        toolbar_free = QHBoxLayout()
        lbl_pool = QLabel("ДОСТУПНЫЕ ЗАКАЗЫ ДЛЯ ДОСТАВКИ")
        lbl_pool.setStyleSheet("color: #a6adc8; font-weight: bold; font-size: 11px;")
        toolbar_free.addWidget(lbl_pool)
        
        toolbar_free.addStretch()
        
        btn_refresh = QPushButton("🔄 Обновить")
        btn_refresh.setFixedWidth(100)
        btn_refresh.clicked.connect(self.refresh_screen)
        toolbar_free.addWidget(btn_refresh)
        layout_free.addLayout(toolbar_free)

        splitter_free = QSplitter(Qt.Orientation.Vertical)

        # --- Верхний виджет: Доступные заказы ---
        widget_orders = QWidget()
        layout_orders = QVBoxLayout(widget_orders)
        layout_orders.setContentsMargins(0, 0, 0, 0)

        self.table_available = QTableWidget()
        self.table_available.setColumnCount(4)
        self.table_available.setHorizontalHeaderLabels(["ID Заказа", "Дата создания", "Сумма", "Покупатель"])
        self.table_available.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_available.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_available.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_available.itemSelectionChanged.connect(self.load_order_items)
        layout_orders.addWidget(self.table_available)

        btn_take = QPushButton("Взять выбранный заказ в работу")
        btn_take.setStyleSheet("background-color: #a6e3a1; color: #11111b; font-weight: bold; height: 35px;")
        btn_take.clicked.connect(self.take_order)
        layout_orders.addWidget(btn_take)
        
        splitter_free.addWidget(widget_orders)

        # --- Нижний виджет: Предпросмотр состава заказа ---
        widget_items = QWidget()
        layout_items = QVBoxLayout(widget_items)
        layout_items.setContentsMargins(0, 10, 0, 0)

        lbl_items = QLabel("СОСТАВ ВЫБРАННОГО ЗАКАЗА (ПРЕДПРОСМОТР)")
        lbl_items.setStyleSheet("color: #cfc9c2; font-weight: bold; font-size: 11px;")
        layout_items.addWidget(lbl_items)

        self.table_items = QTableWidget()
        self.table_items.setColumnCount(4)
        self.table_items.setHorizontalHeaderLabels(["Товар", "Цена за ед.", "Количество", "Стоимость"])
        self.table_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_items.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout_items.addWidget(self.table_items)

        splitter_free.addWidget(widget_items)
        
        layout_free.addWidget(splitter_free)
        self.stack.addWidget(self.page_free)

        # =====================================================================
        # СТРАНИЦА 1: КУРЬЕР ЗАНЯТ (Активный заказ в процессе доставки)
        # =====================================================================
        self.page_busy = QWidget()
        layout_busy = QVBoxLayout(self.page_busy)
        
        lbl_active = QLabel("ВАШ АКТИВНЫЙ ЗАКАЗ В РАБОТЕ")
        lbl_active.setStyleSheet("color: #f9e2af; font-weight: bold; font-size: 11px; margin-bottom: 5px;")
        layout_busy.addWidget(lbl_active)

        # Карточка с информацией о клиенте и доставке
        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.card_frame.setStyleSheet("background-color: #1e1e2e; border-radius: 8px; border: 1px solid #313244;")
        self.card_layout = QGridLayout(self.card_frame)
        self.card_layout.setContentsMargins(15, 15, 15, 15)
        
        self.lbl_info_id = QLabel()
        self.lbl_info_customer = QLabel()
        self.lbl_info_phone = QLabel()
        self.lbl_info_amount = QLabel()
        
        self.card_layout.addWidget(QLabel("Заказ:"), 0, 0)
        self.card_layout.addWidget(self.lbl_info_id, 0, 1)
        self.card_layout.addWidget(QLabel("Получатель:"), 1, 0)
        self.card_layout.addWidget(self.lbl_info_customer, 1, 1)
        self.card_layout.addWidget(QLabel("Телефон:"), 2, 0)
        self.card_layout.addWidget(self.lbl_info_phone, 2, 1)
        self.card_layout.addWidget(QLabel("Сумма к оплате:"), 3, 0)
        self.card_layout.addWidget(self.lbl_info_amount, 3, 1)
        
        layout_busy.addWidget(self.card_frame)

        # Таблица состава текущего активного заказа
        lbl_active_items = QLabel("Содержимое посылки:")
        lbl_active_items.setStyleSheet("color: #a6adc8; font-weight: bold; margin-top: 10px;")
        layout_busy.addWidget(lbl_active_items)

        self.table_active_items = QTableWidget()
        self.table_active_items.setColumnCount(4)
        self.table_active_items.setHorizontalHeaderLabels(["Товар", "Цена", "Кол-во", "Итого"])
        self.table_active_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout_busy.addWidget(self.table_active_items)

        # Кнопка завершения
        btn_complete = QPushButton("Доставлено! Закрыть заказ")
        btn_complete.setStyleSheet("background-color: #a6e3a1; color: #11111b; font-weight: bold; height: 40px; margin-top: 10px;")
        btn_complete.clicked.connect(self.finish_order)
        layout_busy.addWidget(btn_complete)

        self.stack.addWidget(self.page_busy)

        self.refresh_screen()

    def refresh_screen(self):
        """Проверяет статус курьера в БД и переключает интерфейс."""
        active_order = get_active_courier_order(self.courier_id)
        
        self.table_items.setRowCount(0)

        if active_order:
            self.current_order_id = active_order[0]
            self.lbl_info_id.setText(f"<b>№ {active_order[0]}</b> (от {active_order[1].strftime('%d.%m.%Y %H:%M')})")
            self.lbl_info_customer.setText(str(active_order[3]))
            self.lbl_info_phone.setText(str(active_order[4]) if active_order[4] else "Не указан")
            
            try:
                amount_val = float(active_order[2])
                self.lbl_info_amount.setText(f"<font color='#a6e3a1'><b>{amount_val:.2f} руб.</b></font>")
            except (ValueError, TypeError):
                self.lbl_info_amount.setText(f"<b>{active_order[2]} руб.</b>")

            self.load_active_order_items()
            self.stack.setCurrentIndex(1)
        else:
            self.current_order_id = None
            self.load_available_orders()
            self.stack.setCurrentIndex(0)

    def load_available_orders(self):
        """Заполняет верхнюю таблицу доступными заказами."""
        self.table_available.setRowCount(0)
        orders = get_available_orders()
        
        for row, data in enumerate(orders):
            self.table_available.insertRow(row)
            self.table_available.setItem(row, 0, QTableWidgetItem(str(data[0])))
            self.table_available.setItem(row, 1, QTableWidgetItem(data[1].strftime("%d.%m.%Y %H:%M")))
            
            try:
                price_val = float(data[2])
                price_str = f"{price_val:.2f} руб."
            except (ValueError, TypeError):
                price_str = f"{data[2]} руб."
                
            self.table_available.setItem(row, 2, QTableWidgetItem(price_str))
            self.table_available.setItem(row, 3, QTableWidgetItem(str(data[3])))

    def load_order_items(self):
        """Заполняет нижнюю таблицу составом выбранного в пуле заказа (предпросмотр)."""
        self.table_items.setRowCount(0)
        selected = self.table_available.selectedItems()
        if not selected:
            return
            
        row = self.table_available.currentRow()
        order_id_item = self.table_available.item(row, 0)
        if not order_id_item:
            return
            
        order_id = int(order_id_item.text())
        items = get_order_items_details(order_id)
        
        for r_idx, item in enumerate(items):
            self.table_items.insertRow(r_idx)
            self.table_items.setItem(r_idx, 0, QTableWidgetItem(str(item[0]))) # Название товара
            
            try:
                price_at_order = float(item[1])
                price_str = f"{price_at_order:.2f} руб."
            except (ValueError, TypeError):
                price_str = f"{item[1]} руб."
            self.table_items.setItem(r_idx, 1, QTableWidgetItem(price_str)) # Цена за единицу
            
            self.table_items.setItem(r_idx, 2, QTableWidgetItem(str(item[2]))) # Количество
            
            try:
                total_item_price = float(item[3])
                total_str = f"{total_item_price:.2f} руб."
            except (ValueError, TypeError):
                total_str = f"{item[3]} руб."
            self.table_items.setItem(r_idx, 3, QTableWidgetItem(total_str)) # Итого за товар

    def load_active_order_items(self):
        """Загружает состав текущего принятого заказа для экрана занятости."""
        self.table_active_items.setRowCount(0)
        if not self.current_order_id:
            return
        items = get_order_items_details(self.current_order_id)
        for row, item in enumerate(items):
            self.table_active_items.insertRow(row)
            self.table_active_items.setItem(row, 0, QTableWidgetItem(str(item[0])))
            
            try:
                p_val = float(item[1])
                p_str = f"{p_val:.2f} руб."
            except (ValueError, TypeError):
                p_str = f"{item[1]} руб."
            self.table_active_items.setItem(row, 1, QTableWidgetItem(p_str))
            
            self.table_active_items.setItem(row, 2, QTableWidgetItem(str(item[2])))
            
            try:
                t_val = float(item[3])
                t_str = f"{t_val:.2f} руб."
            except (ValueError, TypeError):
                t_str = f"{item[3]} руб."
            self.table_active_items.setItem(row, 3, QTableWidgetItem(t_str))

    def take_order(self):
        selected = self.table_available.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите заказ из таблицы!")
            return
            
        row = self.table_available.currentRow()
        order_id = int(self.table_available.item(row, 0).text())
        
        reply = QMessageBox.question(
            self, "Принять заказ", 
            f"Вы уверены, что хотите взять в работу заказ №{order_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                accept_order(order_id, self.courier_id)
                QMessageBox.information(self, "Успех", f"Заказ №{order_id} принят в работу.")
                self.refresh_screen()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", f"Не удалось взять заказ:\n{e}")

    def finish_order(self):
        if not self.current_order_id:
            return
            
        reply = QMessageBox.question(
            self, "Завершить доставку", 
            f"Подтверждаете, что заказ №{self.current_order_id} успешно доставлен?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                complete_order(self.current_order_id)
                QMessageBox.information(self, "Готово", "Статус заказа успешно обновлен на 'Доставлен'.")
                self.refresh_screen()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", f"Не удалось завершить заказ:\n{e}")