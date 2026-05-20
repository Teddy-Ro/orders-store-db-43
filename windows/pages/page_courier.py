from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QMessageBox, 
                             QStackedWidget, QFrame, QGridLayout, QHeaderView)
from PyQt6.QtCore import Qt
from database.queries import (get_available_orders, get_active_courier_order, 
                              get_order_items_details, accept_order, complete_order)

class PageCourier(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.courier_id = user_info[0]  # employeeid авторизованного курьера
        self.current_order_id = None

        # Главный слой страницы
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Контейнер состояний экрана (Исключает любые наложения текста)
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
        toolbar_free.addWidget(QLabel("<h3>📥 Доступные оплаченные заказы в системе</h3>"))
        toolbar_free.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.setStyleSheet("padding: 6px 12px;")
        self.btn_refresh.clicked.connect(self.load_available_orders)
        toolbar_free.addWidget(self.btn_refresh)
        
        layout_free.addLayout(toolbar_free)
        
        self.table_available = QTableWidget(0, 4)
        self.table_available.setHorizontalHeaderLabels([
            "ID Заказа", "Дата оформления", "Клиент", "Адрес доставки"
        ])
        
        self.table_available.setColumnWidth(0, 90)   # ID Заказа
        self.table_available.setColumnWidth(1, 160)  # Дата оформления
        self.table_available.setColumnWidth(2, 220)  # Клиент
        # Адрес доставки займет ВСЁ оставшееся место на экране:
        self.table_available.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.table_available.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_available.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout_free.addWidget(self.table_available)

        self.btn_accept = QPushButton("🚚 Взять выбранный заказ в работу")
        self.btn_accept.setStyleSheet("background-color: #0284c7; color: white; padding: 12px; font-weight: bold; font-size: 14px; border-radius: 4px;")
        self.btn_accept.clicked.connect(self.take_order)
        layout_free.addWidget(self.btn_accept)
        
        self.stack.addWidget(self.page_free)

        # =====================================================================
        # СТРАНИЦА 1: КУРЬЕР В ПУТИ (Полная информация об одном активном заказе)
        # =====================================================================
        self.page_active = QWidget()
        layout_active = QVBoxLayout(self.page_active)
        layout_active.setContentsMargins(0, 0, 0, 0)
        layout_active.setSpacing(15)

        layout_active.addWidget(QLabel("<h3>📦 Текущее задание на доставку</h3>"))

        # Информационная карточка клиента (Поля выстроены строго в колонку)
        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("""
            QFrame { 
                background-color: rgba(255, 255, 255, 0.03); 
                border: 1px solid #313244; 
                border-radius: 6px; 
            } 
            QLabel { 
                border: none; 
                font-size: 13px; 
            }
        """)
        card_layout = QGridLayout(self.card_frame)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(12)  # Увеличили шаг между строками для читаемости

        self.val_order_id = QLabel("-")
        self.val_order_id.setStyleSheet("font-weight: bold; color: #38bdf8; font-size: 15px;")
        self.val_date = QLabel("-")
        self.val_client = QLabel("-")
        self.val_phone = QLabel("-")
        self.val_address = QLabel("-")
        self.val_address.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 14px;")

        # Размещение элементов строго вертикально
        card_layout.addWidget(QLabel("<b>Номер заказа:</b>"), 0, 0)
        card_layout.addWidget(self.val_order_id, 0, 1)
        
        card_layout.addWidget(QLabel("<b>Дата создания:</b>"), 1, 0)
        card_layout.addWidget(self.val_date, 1, 1)
        
        card_layout.addWidget(QLabel("<b>Получатель (ФИО):</b>"), 2, 0)
        card_layout.addWidget(self.val_client, 2, 1)
        
        card_layout.addWidget(QLabel("<b>Телефон связи:</b>"), 3, 0)
        card_layout.addWidget(self.val_phone, 3, 1)
        
        card_layout.addWidget(QLabel("<b>Адрес доставки:</b>"), 4, 0)
        card_layout.addWidget(self.val_address, 4, 1)
        
        card_layout.setColumnMinimumWidth(0, 150)
        card_layout.setColumnStretch(1, 1)

        layout_active.addWidget(self.card_frame)

        # Таблица состава товаров
        layout_active.addWidget(QLabel("<b>Состав посылки (список товаров):</b>"))
        self.table_items = QTableWidget(0, 4)
        self.table_items.setHorizontalHeaderLabels(["Артикул", "ID Товара", "Название товара", "Количество (шт)"])
        
        # Настройка интерактивных колонок
        self.table_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_items.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_items.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout_active.addWidget(self.table_items)

        # Кнопка выполнения заказа в подвале
        self.btn_complete = QPushButton("🏁 Заказ успешно доставлен и вручен")
        self.btn_complete.setStyleSheet("background-color: #22c55e; color: white; padding: 12px; font-weight: bold; font-size: 14px; border-radius: 4px;")
        self.btn_complete.clicked.connect(self.finish_order)
        layout_active.addWidget(self.btn_complete)

        self.stack.addWidget(self.page_active)

        # Определение стартового состояния экрана
        self.refresh_screen()

    def refresh_screen(self):
        """Проверяет состояние курьера и переключает экраны"""
        active_order = get_active_courier_order(self.courier_id)
        
        if active_order:
            # Есть активный заказ -> Карточка активного заказа
            self.current_order_id = active_order[0]
            
            self.val_order_id.setText(f"№ {active_order[0]}")
            self.val_date.setText(str(active_order[1]).split('.')[0])
            self.val_client.setText(str(active_order[2]))
            self.val_phone.setText(str(active_order[3] or "Не указан"))
            self.val_address.setText(str(active_order[4]))
            
            self.load_order_items(self.current_order_id)
            self.stack.setCurrentIndex(1)
        else:
            # Свободен -> Пул свободных заказов
            self.current_order_id = None
            self.load_available_orders()
            self.stack.setCurrentIndex(0)

    def load_available_orders(self):
        self.table_available.setRowCount(0)
        orders = get_available_orders()
        for row, data in enumerate(orders):
            self.table_available.insertRow(row)
            self.table_available.setItem(row, 0, QTableWidgetItem(str(data[0])))
            self.table_available.setItem(row, 1, QTableWidgetItem(str(data[1])))
            self.table_available.setItem(row, 2, QTableWidgetItem(str(data[2])))
            self.table_available.setItem(row, 3, QTableWidgetItem(str(data[3])))
        # МЕТОД resizeColumnsToContents() ОТСЮДА УБРАН, ЧТОБЫ ИЗБЕЖАТЬ СЖАТИЯ!

    def load_order_items(self, order_id):
        self.table_items.setRowCount(0)
        items = get_order_items_details(order_id)
        for row, data in enumerate(items):
            self.table_items.insertRow(row)
            self.table_items.setItem(row, 0, QTableWidgetItem(str(data[0])))
            self.table_items.setItem(row, 1, QTableWidgetItem(str(data[1])))
            self.table_items.setItem(row, 2, QTableWidgetItem(str(data[2])))
            self.table_items.setItem(row, 3, QTableWidgetItem(str(data[3])))

    def take_order(self):
        selected = self.table_available.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите заказ из таблицы!")
            return
            
        row = selected[0].row()
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