import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.gridspec import GridSpec

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QDateEdit, QPushButton, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, QGridLayout, QMessageBox)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont
from database.queries import (get_analytics_kpis, get_top_products, 
                              get_sales_trend, get_order_status_distribution, get_top_sellers_rating)

class PageAnalytics(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # --- ВЕРХНЯЯ ПАНЕЛЬ ФИЛЬТРОВ ПО ДАТАМ ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("<b>Период анализа с:</b>"))
        
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addMonths(-2)) 
        filter_layout.addWidget(self.date_start)

        filter_layout.addWidget(QLabel("<b>по:</b>"))
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_end)

        # АППАРАТНАЯ БЛОКИРОВКА ОТРИЦАТЕЛЬНОГО ПЕРИОДА
        self.date_start.dateChanged.connect(lambda d: self.date_end.setMinimumDate(d))
        self.date_end.dateChanged.connect(lambda d: self.date_start.setMaximumDate(d))
        
        self.date_end.setMinimumDate(self.date_start.date())
        self.date_start.setMaximumDate(self.date_end.date())

        self.btn_apply = QPushButton("🔄 Применить фильтр")
        self.btn_apply.setStyleSheet("padding: 5px 15px; font-weight: bold; background-color: #38bdf8; color: black; border-radius:4px;")
        self.btn_apply.clicked.connect(self.refresh_analytics)
        filter_layout.addWidget(self.btn_apply)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Стэк вкладок
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # ВКЛАДКА 1: Числовые показатели
        self.tab_numbers = QWidget()
        self.setup_numbers_tab()
        self.tabs.addTab(self.tab_numbers, "📈 Сводные KPI и ТОПы")

        # ВКЛАДКА 2: Аналитический Дашборд
        self.tab_charts = QWidget()
        self.setup_charts_tab()
        self.tabs.addTab(self.tab_charts, "📊 Аналитический Дашборд")

        self.refresh_analytics()

    def setup_numbers_tab(self):
        vbox = QVBoxLayout(self.tab_numbers)
        
        kpi_widget = QFrame()
        kpi_widget.setStyleSheet("QFrame { background-color: rgba(255,255,255,0.02); border: 1px solid #313244; border-radius: 6px; }")
        kpi_grid = QGridLayout(kpi_widget)
        kpi_grid.setSpacing(15)
        
        self.lbl_revenue = QLabel("0.00 руб.")
        self.lbl_profit = QLabel("0.00 руб.")
        self.lbl_rate = QLabel("0.0%")
        self.lbl_avg_check = QLabel("0.00 руб.")
        self.lbl_total_orders = QLabel("0 шт.")
        
        for lbl in [self.lbl_revenue, self.lbl_profit, self.lbl_rate, self.lbl_avg_check, self.lbl_total_orders]:
            lbl.setFont(QFont("Arial", 15, QFont.Weight.Bold))
            lbl.setStyleSheet("border: none; color: #a6e3a1;")
        
        self.lbl_rate.setStyleSheet("border: none; color: #f9e2af;")
        self.lbl_total_orders.setStyleSheet("border: none; color: #89b4fa;")

        kpi_grid.addWidget(QLabel("💰 ВЫРУЧКА ЗА ПЕРИОД:"), 0, 0)
        kpi_grid.addWidget(self.lbl_revenue, 1, 0)
        kpi_grid.addWidget(QLabel("📈 ЧИСТАЯ ПРИБЫЛЬ:"), 0, 1)
        kpi_grid.addWidget(self.lbl_profit, 1, 1)
        kpi_grid.addWidget(QLabel("🏁 УСПЕШНОСТЬ ДОСТАВОК:"), 0, 2)
        kpi_grid.addWidget(self.lbl_rate, 1, 2)
        
        kpi_grid.addWidget(QLabel("🛒 СРЕДНИЙ ЧЕК ЗАКАЗА:"), 2, 0)
        kpi_grid.addWidget(self.lbl_avg_check, 3, 0)
        kpi_grid.addWidget(QLabel("📋 ВСЕГО ОФОРМЛЕНО ЗАКАЗОВ:"), 2, 1)
        kpi_grid.addWidget(self.lbl_total_orders, 3, 1)
        
        vbox.addWidget(kpi_widget)
        vbox.addWidget(QLabel("<h3>🔥 Топ-5 самых прибыльных товаров</h3>"))

        self.table_top = QTableWidget(0, 4)
        self.table_top.setHorizontalHeaderLabels(["Артикул", "Название товара", "Продано (шт)", "Общая сумма продаж"])
        self.table_top.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_top.horizontalHeader().setStretchLastSection(True)
        vbox.addWidget(self.table_top)

    def setup_charts_tab(self):
        vbox = QVBoxLayout(self.tab_charts)
        self.fig = plt.figure(figsize=(11, 8))
        self.canvas = FigureCanvas(self.fig)
        vbox.addWidget(self.canvas)

    def refresh_analytics(self):
        if self.date_start.date() > self.date_end.date():
            QMessageBox.warning(self, "Ошибка периода", "Дата начала периода не может быть позже даты окончания!")
            return

        s_date = self.date_start.date().toString("yyyy-MM-dd")
        e_date = self.date_end.date().toString("yyyy-MM-dd")

        # 1. Загрузка KPI
        rev, prof, rate, avg_check, total_orders = get_analytics_kpis(s_date, e_date)
        self.lbl_revenue.setText(f"{rev:,.2f} руб.".replace(",", " "))
        self.lbl_profit.setText(f"{prof:,.2f} руб.".replace(",", " "))
        self.lbl_rate.setText(f"{rate}%")
        self.lbl_avg_check.setText(f"{avg_check:,.2f} руб.".replace(",", " "))
        self.lbl_total_orders.setText(f"{total_orders} шт.")

        # 2. Таблица ТОП товаров
        self.table_top.setRowCount(0)
        for row, data in enumerate(get_top_products(s_date, e_date)):
            self.table_top.insertRow(row)
            self.table_top.setItem(row, 0, QTableWidgetItem(str(data[0])))
            self.table_top.setItem(row, 1, QTableWidgetItem(str(data[1])))
            self.table_top.setItem(row, 2, QTableWidgetItem(str(data[2])))
            self.table_top.setItem(row, 3, QTableWidgetItem(f"{data[3]:.2f} руб."))
        self.table_top.resizeColumnsToContents()

        # 3. ОТРИСОВКА ДАШБОРДА
        self.fig.clear()
        self.fig.patch.set_facecolor('#1e1e2e')
        
        # УВЕЛИЧИЛИ wspace до 0.55, чтобы графики разъехались и освободили место легенде
        gs = GridSpec(2, 2, figure=self.fig, height_ratios=[1.1, 1.0], wspace=2, hspace=0.45)
        
        ax_trend = self.fig.add_subplot(gs[0, :])   
        ax_status = self.fig.add_subplot(gs[1, 0])  
        ax_sellers = self.fig.add_subplot(gs[1, 1]) 

        for ax in [ax_trend, ax_status, ax_sellers]:
            ax.set_facecolor('#181825')

        # --- ГРАФИК 1: Линейные тренды ---
        trend_data = get_sales_trend(s_date, e_date)
        if trend_data:
            days = [str(d[0].strftime('%d.%m')) for d in trend_data]
            revenues = [float(d[1]) for d in trend_data]
            profits = [float(d[2]) for d in trend_data]
            
            x_ticks_indices = list(range(0, len(days), max(1, len(days) // 8)))
            x_ticks_labels = [days[i] for i in x_ticks_indices]
            
            ax_trend.plot(days, revenues, color='#89b4fa', label='Валовая выручка', linewidth=2.5, marker='o', markersize=3)
            ax_trend.plot(days, profits, color='#a6e3a1', label='Чистая прибыль', linewidth=2, linestyle='--')
            
            ax_trend.set_xticks(x_ticks_indices)
            ax_trend.set_xticklabels(x_ticks_labels, color='#cdd6f4', fontsize=8)
            ax_trend.tick_params(axis='y', colors='#cdd6f4', labelsize=8)
            ax_trend.grid(True, color='#313244', linestyle=':', alpha=0.5)
            ax_trend.legend(facecolor='#11111b', edgecolor='#313244', labelcolor='#cdd6f4', loc='upper left', fontsize=8)
            ax_trend.set_title("Динамика финансовой эффективности предприятия", color='#cdd6f4', fontsize=10, fontweight='bold')
        else:
            ax_trend.text(0.5, 0.5, "Данные отсутствуют", color='#a6adc8', ha='center', va='center')

        # --- ГРАФИК 2: Распределение статусов заказов (Pie Chart) ---
        status_data = get_order_status_distribution(s_date, e_date)
        if status_data:
            labels = [str(d[0]) for d in status_data]
            sizes = [int(d[1]) for d in status_data]
            total_orders_count = sum(sizes)
            colors = ['#a6e3a1', '#f38ba8', '#89b4fa', '#f9e2af', '#cba6f7', '#f5e0dc']
            
            # УВЕЛИЧИЛИ РАДИУС: с 0.65 до 0.95, чтобы сделать сам круг гораздо крупнее
            wedges, _ = ax_status.pie(
                sizes, labels=None, startangle=90, radius=0.95,
                colors=colors[:len(sizes)]
            )
            
            # УБИРАЕМ ЛИШНИЕ ОТСТУПЫ ВОКРУГ КРУГА: жестко кадрируем оси от -1.0 до 1.0, 
            # чтобы график не сжимался автоматическими внутренними полями Matplotlib
            ax_status.set_xbound(-1.0, 1.0)
            ax_status.set_ybound(-1.0, 1.0)
            
            legend_labels = [f"{l} ({s} шт., {s/total_orders_count*100:.1f}%)" for l, s in zip(labels, sizes)]
            
            # Чуть-чуть отодвигаем bbox_to_anchor (с 0.8 до 0.95), чтобы большая диаграмма не наезжала на текст
            ax_status.legend(
                wedges, legend_labels, loc="center left", bbox_to_anchor=(0.95, 0.5),
                facecolor='#11111b', edgecolor='#313244', labelcolor='#cdd6f4', title_fontsize=9, fontsize=8
            )
            ax_status.set_title("Структура и состояние заказов", color='#cdd6f4', fontsize=10, fontweight='bold')
        else:
            ax_status.text(0.5, 0.5, "Данные отсутствуют", color='#a6adc8', ha='center', va='center')

        # --- ГРАФИК 3: Рейтинг продавцов с цифрами внутри столбиков ---
        seller_data = get_top_sellers_rating(s_date, e_date)
        if seller_data:
            names = [str(d[0]).split(' ')[0] for d in seller_data] 
            sums = [float(d[1]) for d in seller_data]
            
            bars = ax_sellers.barh(names, sums, color='#cba6f7', height=0.5, edgecolor='#89b4fa', alpha=0.9)
            ax_sellers.tick_params(axis='both', colors='#cdd6f4', labelsize=8)
            ax_sellers.grid(True, axis='x', color='#313244', linestyle=':', alpha=0.5)
            
            max_sum = max(sums) if sums else 1
            for bar in bars:
                width = bar.get_width()
                
                # Умное позиционирование: если столбик слишком узкий (например, 0 продаж), 
                # пишем текст снаружи. Если широкий — пишем внутри столбика.
                if width > max_sum * 0.2:
                    # Внутри столбика: смещение влево, цвет текста темный (#11111b) для идеальной контрастности
                    ax_sellers.text(width - (max_sum * 0.02), bar.get_y() + bar.get_height()/2, f'{width:,.0f} р.', 
                                    va='center', ha='right', color='#11111b', fontsize=8, fontweight='bold')
                else:
                    # Снаружи столбика: смещение вправо, цвет светлый
                    ax_sellers.text(width + (max_sum * 0.02), bar.get_y() + bar.get_height()/2, f'{width:,.0f} р.', 
                                    va='center', ha='left', color='#cdd6f4', fontsize=8, fontweight='bold')
                                
            ax_sellers.set_title("Лидеры продаж среди продавцов", color='#cdd6f4', fontsize=10, fontweight='bold')
        else:
            ax_sellers.text(0.5, 0.5, "Данные отсутствуют", color='#a6adc8', ha='center', va='center')

        self.canvas.draw()