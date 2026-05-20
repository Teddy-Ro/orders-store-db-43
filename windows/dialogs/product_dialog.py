from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QComboBox, QTextEdit
from database.queries import add_product, update_product, get_suppliers_for_dropdown

class ProductDialog(QDialog):
    def __init__(self, parent=None, prod_data=None):
        super().__init__(parent)
        self.prod_id = prod_data[0] if prod_data else None
        self.setWindowTitle("Редактирование товара" if prod_data else "Новый товар")
        self.setFixedSize(400, 350)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.in_art = QLineEdit()
        self.in_art.setPlaceholderText("Оставьте пустым для автогенерации")
        
        self.in_name = QLineEdit()
        self.in_pprice = QLineEdit()
        self.in_sprice = QLineEdit()
        self.in_stock = QLineEdit()
        self.in_unit = QLineEdit()
        self.in_unit.setText("шт.")
        
        self.combo_sup = QComboBox()
        self.load_suppliers()

        self.in_desc = QTextEdit()
        self.in_desc.setMaximumHeight(80)

        form.addRow("Артикул:", self.in_art)
        form.addRow("Название *:", self.in_name)
        form.addRow("Цена закупки *:", self.in_pprice)
        form.addRow("Цена продажи *:", self.in_sprice)
        form.addRow("Остаток *:", self.in_stock)
        form.addRow("Ед. измерения:", self.in_unit)
        form.addRow("Поставщик *:", self.combo_sup)
        form.addRow("Описание:", self.in_desc)
        layout.addLayout(form)

        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_save.setStyleSheet("background-color: #2da44e; color: white; padding: 5px; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_data)
        layout.addWidget(self.btn_save)

        if prod_data:
            # Распределяем данные согласно новым индексам без категории
            self.in_art.setText(str(prod_data[1]))
            self.in_name.setText(str(prod_data[2]))
            self.in_pprice.setText(str(prod_data[3]))
            self.in_sprice.setText(str(prod_data[4]))
            self.in_stock.setText(str(prod_data[5]))
            self.in_unit.setText(str(prod_data[6] or "шт."))
            self.in_desc.setText(str(prod_data[7] or ""))
            
            sup_id_str = str(prod_data[8]) if prod_data[8] else None
            for i in range(self.combo_sup.count()):
                if str(self.combo_sup.itemData(i)) == sup_id_str:
                    self.combo_sup.setCurrentIndex(i)
                    break

    def load_suppliers(self):
        self.combo_sup.clear()
        try:
            suppliers = get_suppliers_for_dropdown()
            for s_id, s_name in suppliers:
                self.combo_sup.addItem(s_name, s_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить поставщиков:\n{e}")

    def save_data(self):
        art = self.in_art.text().strip()
        name = self.in_name.text().strip()
        unit = self.in_unit.text().strip() or "шт."
        description = self.in_desc.toPlainText().strip()
        
        str_pprice = self.in_pprice.text().strip().replace(',', '.')
        str_sprice = self.in_sprice.text().strip().replace(',', '.')
        str_stock = self.in_stock.text().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Название товара обязательно!")
            return
            
        if self.combo_sup.currentIndex() == -1:
            QMessageBox.warning(self, "Ошибка", "Необходимо выбрать поставщика!")
            return

        try:
            p_price = float(str_pprice) if str_pprice else 0.0
            s_price = float(str_sprice) if str_sprice else 0.0
            stock = int(str_stock) if str_stock else 0
            if p_price < 0 or s_price < 0 or stock < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Проверьте корректность числовых полей!")
            return

        supplier_id = self.combo_sup.currentData()

        try:
            if self.prod_id:
                update_product(self.prod_id, art, name, p_price, s_price, stock, unit, supplier_id, description)
            else:
                add_product(art, name, p_price, s_price, stock, unit, supplier_id, description)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить:\n{e}")