from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QSpinBox, QFormLayout, QFrame
from database.seeder import generate_fake_data, clear_database_completely

class PageDeveloper(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        layout.addWidget(QLabel("<h2>🛠 Панель администратора / разработчика</h2>"))
        
        # --- БЛОК 1: ПАРАМЕТРЫ СИДЕРА (ЗАПОЛНЕНИЕ) ---
        box_seed = QFrame()
        box_seed.setStyleSheet("QFrame { background-color: rgba(255,255,255,0.01); border: 1px solid #313244; border-radius: 6px; }")
        vbox_seed = QVBoxLayout(box_seed)
        vbox_seed.addWidget(QLabel("<h3>⚡ Генерация тестовых данных (Seeder)</h3>"))
        
        form_layout = QFormLayout()
        self.spin_cust = QSpinBox()
        self.spin_cust.setRange(10, 200); self.spin_cust.setValue(40)
        
        self.spin_sup = QSpinBox()
        self.spin_sup.setRange(5, 50); self.spin_sup.setValue(10)
        
        self.spin_prod = QSpinBox()
        self.spin_prod.setRange(10, 150); self.spin_prod.setValue(40)
        
        self.spin_days = QSpinBox()
        self.spin_days.setRange(10, 365); self.spin_days.setValue(120)
        
        form_layout.addRow("Количество генерируемых клиентов:", self.spin_cust)
        form_layout.addRow("Количество генерируемых поставщиков:", self.spin_sup)
        form_layout.addRow("Количество генерируемых товаров:", self.spin_prod)
        form_layout.addRow("Глубина истории продаж (дней):", self.spin_days)
        vbox_seed.addLayout(form_layout)
        
        self.btn_seed = QPushButton("🎲 Заполнить базу данных случайными трендами")
        self.btn_seed.setStyleSheet("""
            QPushButton { background-color: #a6e3a1; color: black; padding: 10px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #94e2d5; }
        """)
        self.btn_seed.clicked.connect(self.run_seeder)
        vbox_seed.addWidget(self.btn_seed)
        
        layout.addWidget(box_seed)

        # --- БЛОК 2: ПОЛНАЯ ОЧИСТКА ---
        box_clear = QFrame()
        box_clear.setStyleSheet("QFrame { background-color: rgba(243, 139, 168, 0.03); border: 1px solid #f38ba8; border-radius: 6px; }")
        vbox_clear = QVBoxLayout(box_clear)
        vbox_clear.setSpacing(10)
        
        vbox_clear.addWidget(QLabel("<h3>🚨 Опасная зона (Удаление данных)</h3>"))
        vbox_clear.addWidget(QLabel("Данная функция полностью сотрет все заказы, товары, поставщиков и клиентов.\n"
                                    "В базе останется только один дефолтный аккаунт управляющего: <b>admin / admin</b>."))
        
        self.btn_clear = QPushButton("🗑 Полностью очистить базу данных")
        self.btn_clear.setStyleSheet("""
            QPushButton { background-color: #C96F00; color: black; padding: 12px; font-weight: bold; font-size: 13px; border-radius: 4px; }
            QPushButton:hover { background-color: #E33400; }
        """)
        self.btn_clear.clicked.connect(self.run_clear_db)
        vbox_clear.addWidget(self.btn_clear)
        
        layout.addWidget(box_clear)
        layout.addStretch()

    def run_seeder(self):
        reply = QMessageBox.question(
            self, "Перезапись данных", 
            "Внимание! Текущие записи будут стерты перед генерацией новых. Продолжить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.btn_seed.setEnabled(False)
            try:
                generate_fake_data(
                    num_customers=self.spin_cust.value(),
                    num_suppliers=self.spin_sup.value(),
                    num_products=self.spin_prod.value(),
                    days_of_history=self.spin_days.value()
                )
                QMessageBox.information(self, "Успех", "База данных успешно заполнена трендами!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Сбой операции:\n{e}")
            finally:
                self.btn_seed.setEnabled(True)

    def run_clear_db(self):
        # Первое предупреждение
        reply1 = QMessageBox.warning(
            self, "Подтверждение удаления", 
            "Вы абсолютно уверены, что хотите ПОЛНОСТЬЮ ОБНУЛИТЬ базу данных?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply1 == QMessageBox.StandardButton.Yes:
            # Второе жесткое предупреждение (защита от случайного клика)
            reply2 = QMessageBox.critical(
                self, "Финальная проверка", 
                "Это действие сотрет всю историю продаж и каталоги! Восстановление будет невозможно. Продолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply2 == QMessageBox.StandardButton.Yes:
                try:
                    clear_database_completely()
                    QMessageBox.information(self, "Успех", "База данных полностью очищена до исходного состояния!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка очистки", f"Не удалось очистить таблицы:\n{e}")