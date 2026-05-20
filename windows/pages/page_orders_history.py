from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QHeaderView, QAbstractItemView, QSplitter, QMenu, QPushButton, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from database.queries import get_all_orders, get_order_details, update_order_status

class PageOrdersHistory(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.access_level = user_info[2] 

        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # --- ВЕРХНЯЯ ЧАСТЬ: СПИСОК ЗАКАЗОВ ---
        widget_top = QWidget()
        vbox_top = QVBoxLayout(widget_top)
        vbox_top.setContentsMargins(0, 0, 0, 0)
        
        # === НОВАЯ ПАНЕЛЬ ИНСТРУМЕНТОВ (ПОИСК И ОБНОВЛЕНИЕ) ===
        toolbar = QHBoxLayout()
        lbl_orders = QLabel("📋 ИСТОРИЯ ЗАКАЗОВ")
        lbl_orders.setStyleSheet("color: #a6adc8; font-weight: bold; font-size: 11px;")
        toolbar.addWidget(lbl_orders)
        
        toolbar.addWidget(QLabel("🔍 Поиск:"))
        self.in_search = QLineEdit()
        self.in_search.setPlaceholderText("Найти заказ, клиента или статус...")
        self.in_search.setFixedWidth(250)
        self.in_search.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.in_search)

        toolbar.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_orders)
        toolbar.addWidget(self.btn_refresh)
        
        vbox_top.addLayout(toolbar)
        # ======================================================

        self.table_orders = QTableWidget(0, 7)
        self.table_orders.setHorizontalHeaderLabels(["ID", "Дата", "Статус", "Клиент", "Продавец", "Курьер", "Сумма"])
        self.table_orders.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_orders.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.table_orders.setColumnWidth(0, 50)
        self.table_orders.setColumnWidth(1, 100)
        self.table_orders.setColumnWidth(2, 120)
        self.table_orders.setColumnWidth(3, 200)
        self.table_orders.setColumnWidth(4, 150)
        self.table_orders.setColumnWidth(5, 150)
        self.table_orders.horizontalHeader().setStretchLastSection(True)

        self.table_orders.itemSelectionChanged.connect(self.load_details)
        
        self.table_orders.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_orders.customContextMenuRequested.connect(self.show_status_menu)

        vbox_top.addWidget(self.table_orders)
        splitter.addWidget(widget_top)

        # --- НИЖНЯЯ ЧАСТЬ: СОСТАВ ЗАКАЗА ---
        widget_bottom = QWidget()
        vbox_bottom = QVBoxLayout(widget_bottom)
        vbox_bottom.setContentsMargins(0, 0, 0, 0)

        lbl_details = QLabel("🔍 СОСТАВ ВЫБРАННОГО ЗАКАЗА")
        lbl_details.setStyleSheet("color: #a6adc8; font-weight: bold; font-size: 11px;")
        vbox_bottom.addWidget(lbl_details)

        self.table_details = QTableWidget(0, 5)
        self.table_details.setHorizontalHeaderLabels(["Артикул", "Название", "Цена за шт.", "Кол-во", "Сумма"])
        self.table_details.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_details.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.table_details.setColumnWidth(0, 100)
        self.table_details.setColumnWidth(2, 100)
        self.table_details.setColumnWidth(3, 80)
        self.table_details.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        vbox_bottom.addWidget(self.table_details)
        splitter.addWidget(widget_bottom)

        splitter.setSizes([400, 200])
        layout.addWidget(splitter)

        self.load_orders()

    # === ЛОГИКА ФИЛЬТРАЦИИ (ПОИСКА) ===
    def filter_table(self, text):
        search_text = text.lower()
        for row in range(self.table_orders.rowCount()):
            row_visible = False
            # Пробегаемся по всем колонкам в строке
            for col in range(self.table_orders.columnCount()):
                item = self.table_orders.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break # Если нашли совпадение хоть в одной ячейке - оставляем строку
            # Скрываем или показываем строку
            self.table_orders.setRowHidden(row, not row_visible)

    def load_orders(self):
        self.table_orders.blockSignals(True)
        self.table_orders.setRowCount(0)
        try:
            orders = get_all_orders()
            for row, data in enumerate(orders):
                self.table_orders.insertRow(row)
                
                o_id, date, status, customer, seller, courier, total = data
                
                items = [
                    QTableWidgetItem(str(o_id)),
                    QTableWidgetItem(str(date).split('.')[0]), # Убираем микросекунды из даты
                    QTableWidgetItem(status),
                    QTableWidgetItem(customer),
                    QTableWidgetItem(seller),
                    QTableWidgetItem(courier),
                    QTableWidgetItem(f"{total:.2f}")
                ]
                
                status_item = items[2]
                if status == 'Новый':
                    status_item.setForeground(QColor("#89b4fa"))
                elif status == 'Оплачен':
                    status_item.setForeground(QColor("#a6e3a1"))
                elif status == 'Отменен':
                    status_item.setForeground(QColor("#f38ba8"))
                elif status == 'В доставке':
                    status_item.setForeground(QColor("#f9e2af"))

                for col, item in enumerate(items):
                    self.table_orders.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Сбой загрузки заказов:\n{e}")
        finally:
            self.table_orders.blockSignals(False)
            self.table_details.setRowCount(0) # Очищаем нижнюю таблицу при обновлении

    def load_details(self):
        selected_items = self.table_orders.selectedItems()
        if not selected_items:
            self.table_details.setRowCount(0)
            return

        row = selected_items[0].row()
        order_id = self.table_orders.item(row, 0).text()

        self.table_details.setRowCount(0)
        try:
            details = get_order_details(order_id)
            for r, data in enumerate(details):
                self.table_details.insertRow(r)
                art, name, price, qty, summa = data
                self.table_details.setItem(r, 0, QTableWidgetItem(art))
                self.table_details.setItem(r, 1, QTableWidgetItem(name))
                self.table_details.setItem(r, 2, QTableWidgetItem(f"{price:.2f}"))
                self.table_details.setItem(r, 3, QTableWidgetItem(str(qty)))
                self.table_details.setItem(r, 4, QTableWidgetItem(f"{summa:.2f}"))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить состав заказа:\n{e}")

    def show_status_menu(self, pos):
        item = self.table_orders.itemAt(pos)
        if not item: return
        
        row = item.row()
        order_id = self.table_orders.item(row, 0).text()
        current_status = self.table_orders.item(row, 2).text()

        menu = QMenu()
        menu.setStyleSheet("QMenu { font-size: 13px; }")
        
        # БЛОКИРОВКА: Если заказ отменен ИЛИ уже успешно доставлен — меню не создаем
        if current_status == 'Отменен':
            QMessageBox.information(self, "Информация", "Этот заказ отменен. Изменение статуса невозможно.")
            return
        elif current_status == 'Доставлен':
            QMessageBox.information(self, "Информация", "Этот заказ уже успешно доставлен. Изменение статуса заблокировано.")
            return
            
        # Для всех остальных промежуточных статусов ('Новый', 'Оплачен', 'В доставке') генерируем меню:
        act_new = menu.addAction("🔵 Перевести в 'Новый'")
        act_pay = menu.addAction("🟢 Перевести в 'Оплачен'")
        act_del = menu.addAction("🟡 Перевести в 'В доставке'")
        act_done = menu.addAction("🏁 Перевести в 'Доставлен'")
        menu.addSeparator()
        act_cancel = menu.addAction("❌ Отменить заказ (вернуть остатки)")
        
        action = menu.exec(self.table_orders.viewport().mapToGlobal(pos))
        
        new_status = None
        if action == act_new: new_status = "Новый"
        elif action == act_pay: new_status = "Оплачен"
        elif action == act_del: new_status = "В доставке"
        elif action == act_done: new_status = "Доставлен"
        elif action == act_cancel:
            reply = QMessageBox.question(self, 'Отмена', "Точно отменить заказ? Товары вернутся на склад.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                new_status = "Отменен"

        if new_status and new_status != current_status:
            try:
                update_order_status(order_id, new_status)
                self.load_orders()
                self.in_search.clear() # Очищаем поиск при смене статуса
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", f"Не удалось изменить статус:\n{e}")