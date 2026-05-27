from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QHeaderView, QAbstractItemView, QSplitter, QMenu, QPushButton, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt, QMarginsF
from PyQt6.QtGui import QColor, QPdfWriter, QTextDocument, QPageSize, QPageLayout
import os
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
        
        # === ПАНЕЛЬ ИНСТРУМЕНТОВ ===
        toolbar = QHBoxLayout()
        lbl_orders = QLabel("ИСТОРИЯ ЗАКАЗОВ")
        lbl_orders.setStyleSheet("color: #a6adc8; font-weight: bold; font-size: 11px;")
        toolbar.addWidget(lbl_orders)
        
        toolbar.addWidget(QLabel("🔍 Поиск:"))
        self.in_search = QLineEdit()
        self.in_search.setPlaceholderText("Найти заказ, клиента или статус...")
        self.in_search.setFixedWidth(250)
        self.in_search.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.in_search)

        toolbar.addStretch()

        self.btn_print_selected = QPushButton("Печать выбранных")
        self.btn_print_all = QPushButton("Печать всех")
        
        self.btn_print_selected.clicked.connect(self.print_selected_receipts)
        self.btn_print_all.clicked.connect(self.print_all_receipts)
        
        toolbar.addWidget(self.btn_print_selected)
        toolbar.addWidget(self.btn_print_all)
        
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_orders)
        toolbar.addWidget(self.btn_refresh)
        
        vbox_top.addLayout(toolbar)

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

    def filter_table(self, text):
        search_text = text.lower()
        for row in range(self.table_orders.rowCount()):
            row_visible = False
            for col in range(self.table_orders.columnCount()):
                item = self.table_orders.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break
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
                    QTableWidgetItem(str(date).split('.')[0]), 
                    QTableWidgetItem(status),
                    QTableWidgetItem(customer),
                    QTableWidgetItem(seller if seller else "Не назначен"),
                    QTableWidgetItem(courier if courier else "Не назначен"),
                    QTableWidgetItem(f"{total:.2f}")
                ]
                
                status_item = items[2]
                if status == 'Новый': status_item.setForeground(QColor("#89b4fa"))
                elif status == 'Оплачен': status_item.setForeground(QColor("#a6e3a1"))
                elif status == 'Отменен': status_item.setForeground(QColor("#f38ba8"))
                elif status == 'В доставке': status_item.setForeground(QColor("#f9e2af"))

                for col, item in enumerate(items):
                    self.table_orders.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Сбой загрузки заказов:\n{e}")
        finally:
            self.table_orders.blockSignals(False)
            self.table_details.setRowCount(0)

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
        
        if current_status == 'Отменен':
            QMessageBox.information(self, "Информация", "Этот заказ отменен. Изменение статуса невозможно.")
            return
        elif current_status == 'Доставлен':
            QMessageBox.information(self, "Информация", "Этот заказ уже успешно доставлен. Изменение статуса заблокировано.")
            return
            
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
                self.in_search.clear()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", f"Не удалось изменить статус:\n{e}")

    def print_selected_receipts(self):
        """Собирает индексы только выделенных пользователем строк"""
        selected_rows = list(set([index.row() for index in self.table_orders.selectedIndexes()]))
        self.export_multiple_pdfs(selected_rows)

    def print_all_receipts(self):
        """Собирает индексы только тех строк, которые реально видны на экране (не скрыты поиском)"""
        visible_rows = []
        for row in range(self.table_orders.rowCount()):
            if not self.table_orders.isRowHidden(row):
                visible_rows.append(row)
        self.export_multiple_pdfs(visible_rows)

    def export_multiple_pdfs(self, rows_to_print):
        """Генерирует ОДИН сводный PDF-отчет в виде компактной таблицы реестра с переносами строк"""
        if not rows_to_print:
            QMessageBox.warning(self, "Внимание", "Нет заказов для включения в отчет. Выделите нужные строки.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить сводный отчет", "Сводный_отчет_по_заказам.pdf", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        from database.queries import get_order_details
        from PyQt6.QtGui import QPageLayout

        # HTML-верстка с уменьшенными на пару пунктов шрифтами и структурированными переносами
        html_content = """
        <html>
        <head>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; color: #111111; margin: 15pt; }
            h1 { text-align: center; color: #111111; font-size: 20pt; margin-bottom: 4pt; text-transform: uppercase; font-weight: bold; }
            .subtitle { text-align: center; color: #444444; font-size: 11pt; margin-bottom: 20pt; font-style: italic; }
            
            .report-table { width: 100%; border-collapse: collapse; font-size: 10.5pt; }
            .report-table th { background-color: #2c3e50; color: #ffffff; font-weight: bold; padding: 10pt 8pt; border: 2px solid #34495e; font-size: 11pt; text-align: center; }
            .report-table td { padding: 8pt 7pt; border: 1px solid #7f8c8d; vertical-align: middle; }
            
            /* Информационная строка-заголовок для каждого отдельного заказа */
            .order-header-row { background-color: #d5dbdb; font-weight: bold; color: #1b2631; font-size: 11.5pt; }
            .order-label { color: #566573; font-weight: bold; }
            
            /* Итоговая строка внутри заказа */
            .order-subtotal-row { background-color: #f8f9f9; font-style: italic; color: #2c3e50; font-size: 10.5pt; }
            
            .grand-total-box { text-align: right; margin-top: 25pt; font-size: 16pt; font-weight: bold; color: #b03a2e; border-top: 3px double #b03a2e; padding-top: 8pt; }
        </style>
        </head>
        <body>
            <h1>Сводный реестр оформленных заказов</h1>
            <div class='subtitle'>Система учета Orders Store ERP • Сводный аналитический документ</div>
            
            <table class='report-table'>
                <thead>
                    <tr>
                        <th width='15%'>Артикул</th>
                        <th width='43%'>Наименование товарной спецификации</th>
                        <th width='14%'>Цена за ед.</th>
                        <th width='11%'>Количество</th>
                        <th width='17%'>Сумма позиции</th>
                    </tr>
                </thead>
                <tbody>
        """

        grand_total = 0.0

        for row in rows_to_print:
            order_id = self.table_orders.item(row, 0).text()
            date = self.table_orders.item(row, 1).text()
            status = self.table_orders.item(row, 2).text()
            customer = self.table_orders.item(row, 3).text()
            seller = self.table_orders.item(row, 4).text()
            courier = self.table_orders.item(row, 5).text()
            total_str = self.table_orders.item(row, 6).text()
            
            try:
                grand_total += float(total_str)
            except:
                pass

            try:
                details = get_order_details(order_id)
                if not details:
                    continue
                
                # Заголовок заказа: убрали разделители "|" и структурировали через теги <br>
                html_content += f"""
                <tr class='order-header-row'>
                    <td colspan='5' style='padding: 10pt 8pt; line-height: 1.4;'>
                        ЗАКАЗ № {order_id} от {date} <br>
                        <span class='order-label'>Статус наряда:</span> {status} <br>
                        <span class='order-label'>Клиент (ФИО):</span> {customer} <br>
                        <span class='order-label'>Оператор (Продавец):</span> {seller} <br>
                        <span class='order-label'>Служба доставки (Курьер):</span> {courier}
                    </td>
                </tr>
                """

                # Вывод товарных позиций наряда
                for data in details:
                    art, name, price, qty, summa = data
                    html_content += f"""
                    <tr>
                        <td align='center'><b>{art}</b></td>
                        <td>{name}</td>
                        <td align='right'>{price:.2f} руб.</td>
                        <td align='center'>{qty} шт.</td>
                        <td align='right'><b>{summa:.2f} руб.</b></td>
                    </tr>
                    """
                
                # Строка промежуточного итога по наряду
                html_content += f"""
                <tr class='order-subtotal-row'>
                    <td colspan='4' align='right' style='padding: 8pt 7pt;'>Промежуточный итог по наряду № {order_id}:</td>
                    <td align='right' style='color: #1b2631; font-weight: bold; padding: 8pt 7pt;'>{float(total_str):.2f} руб.</td>
                </tr>
                """
                    
            except Exception as e:
                print(f"Ошибка обработки состава заказа №{order_id}: {e}")

        html_content += f"""
                </tbody>
            </table>
            <div class='grand-total-box'>ОБЩИЙ ВАЛОВЫЙ ДОХОД ПО РЕЕСТРУ: {grand_total:.2f} руб.</div>
        </body>
        </html>
        """

        try:
            writer = QPdfWriter(file_path)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            writer.setPageOrientation(QPageLayout.Orientation.Landscape)
            writer.setResolution(300)
            writer.setPageMargins(QMarginsF(15, 15, 15, 15))

            doc = QTextDocument()
            doc.setHtml(html_content)
            doc.print(writer)
            
            QMessageBox.information(
                self, "Успех", 
                f"Сводный документ успешно сформирован компактным шрифтом!\n\nФайл сохранен:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка печати", f"Не удалось скомпилировать PDF-документ:\n{e}")