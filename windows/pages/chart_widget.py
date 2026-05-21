from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush
from PyQt6.QtCore import Qt, QPointF

class SimpleLineChart(QWidget):
    def __init__(self):
        super().__init__()
        self.data_points = []
        self.setMinimumHeight(250)

    def set_data(self, data):
        self.data_points = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), QColor("#1e1e2e"))

        if not self.data_points:
            painter.setPen(QColor("#a6adc8"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Нет данных за выбранный период")
            return

        margin_left = 60
        margin_bottom = 40
        margin_top = 20
        margin_right = 20

        width = self.width() - margin_left - margin_right
        height = self.height() - margin_top - margin_bottom

        max_val = max([p[1] for p in self.data_points]) or 1.0
        max_val = max_val * 1.1

        # Рисуем сетку координат
        grid_pen = QPen(QColor("#313244"), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        painter.setFont(QFont("Arial", 8))
        
        # Горизонтальные линии сетки
        for i in range(5):
            y_curr = margin_top + height - (height * i / 4)
            val_curr = max_val * i / 4
            painter.drawLine(int(margin_left), int(y_curr), int(self.width() - margin_right), int(y_curr))
            painter.setPen(QPen(QColor("#a6adc8")))
            painter.drawText(5, int(y_curr + 4), f"{val_curr:.0f}")
            painter.setPen(grid_pen)

        # Вычисляем экранные координаты точек
        points = []
        step_x = width / (len(self.data_points) - 1) if len(self.data_points) > 1 else width
        
        for idx, (_, val) in enumerate(self.data_points):
            x = margin_left + idx * step_x
            y = margin_top + height - (height * val / max_val)
            points.append(QPointF(x, y))

        # Рисуем график-градиент (заливка под линией)
        if len(points) > 1:
            path_brush = QBrush(QColor(137, 180, 250, 40))
            painter.setBrush(path_brush)
            painter.setPen(Qt.PenStyle.NoPen)
            
            poly_points = [QPointF(margin_left, margin_top + height)]
            poly_points.extend(points)
            poly_points.append(QPointF(points[-1].x(), margin_top + height))
            painter.drawPolygon(poly_points)

        # Рисуем саму основную линию графика
        line_pen = QPen(QColor("#89b4fa"), 2, Qt.PenStyle.SolidLine)
        painter.setPen(line_pen)
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i+1])