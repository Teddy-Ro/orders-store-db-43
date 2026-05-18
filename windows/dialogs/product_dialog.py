from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QComboBox
from database.queries import add_product, update_product, get_all_suppliers

class ProductDialog(QDialog):
    def __init__(self, parent=None, prod_data=None):
        super().__init__(parent)
        self.prod_id = prod_data[0] if prod_data else None
        self.setWindowTitle("Редактирование товара" if prod_data else "Новый товар")
        self.setFixedSize(350, 300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.in_art = QLineEdit()
        self.in_name = QLineEdit()
        self.in_pprice = QLineEdit()
        self.in_sprice = QLineEdit()
        self.in_stock = QLineEdit()
        self.combo_sup = QComboBox()

        # Загружаем поставщиков в ComboBox
        self.combo_sup.addItem("Без поставщика (NULL)", None)
        suppliers = get_all_suppliers()
        for sup in suppliers:
            self.combo_sup.addItem(f"{sup[1]} (ID: {sup[0]})", sup[0]) # Отображаем имя, но прячем ID

        form.addRow("Артикул *:", self.in_art)
        form.addRow("Название *:", self.in_name)
        form.addRow("Цена закупки *:", self.in_pprice)
        form.addRow("Цена продажи *:", self.in_sprice)
        form.addRow("Остаток (шт):", self.in_stock)
        form.addRow("Поставщик:", self.combo_sup)
        layout.addLayout(form)

        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_save.clicked.connect(self.save_data)
        layout.addWidget(self.btn_save)

        if prod_data:
            self.in_art.setText(str(prod_data[1]))
            self.in_name.setText(str(prod_data[2]))
            self.in_pprice.setText(str(prod_data[3]))
            self.in_sprice.setText(str(prod_data[4]))
            self.in_stock.setText(str(prod_data[5]))
            
            # Ищем поставщика в комбобоксе по ID и выбираем его
            sup_id_str = str(prod_data[6]) if prod_data[6] else None
            for i in range(self.combo_sup.count()):
                if str(self.combo_sup.itemData(i)) == sup_id_str:
                    self.combo_sup.setCurrentIndex(i)
                    break

    def save_data(self):
        art = self.in_art.text().strip()
        name = self.in_name.text().strip()
        
        # Заменяем запятые на точки для дробных чисел
        str_pprice = self.in_pprice.text().strip().replace(',', '.')
        str_sprice = self.in_sprice.text().strip().replace(',', '.')
        str_stock = self.in_stock.text().strip()

        # Валидация
        if not art or not name:
            QMessageBox.warning(self, "Ошибка", "Артикул и Название обязательны!")
            return

        try:
            p_price = float(str_pprice)
            s_price = float(str_sprice)
            stock = int(str_stock) if str_stock else 0
            if p_price < 0 or s_price < 0 or stock < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цены должны быть числами (например 10.50), а остаток - целым числом больше нуля!")
            return

        # Получаем ID поставщика (спрятанный в ComboBox)
        sup_id = self.combo_sup.currentData()

        try:
            if self.prod_id: update_product(self.prod_id, art, name, p_price, s_price, stock, sup_id)
            else: add_product(art, name, p_price, s_price, stock, sup_id)
            self.accept()
        except Exception as e:
            if "unique" in str(e).lower(): QMessageBox.warning(self, "Ошибка", "Товар с таким Артикулом уже существует!")
            else: QMessageBox.critical(self, "Ошибка", f"Ошибка БД:\n{e}")