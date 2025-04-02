from PyQt6.QtCharts import (
    QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
)
from PyQt6.QtWidgets import (
    QGraphicsView, QToolTip
)
from PyQt6.QtCore import (
    QDateTime, Qt, QMargins, QPointF
)
from PyQt6.QtGui import (
    QColor, QPainter, QBrush, QFont, QPen, QCursor
)
from PyQt6 import QtWidgets, QtCore

stats_texts ={
    "voice_online": "Voice online",
    "offline": "Offline",
    "voice_afk": "Voice AFK",
    "voice_alone": "Voice alone",
    "voice_deaf": "Full mute",
    "voice_mute": "Mute",
    "online": "Online",
}


class CustomChartView(QChartView):
    def __init__(self, chart, timeline_data, parent=None, date_str = ''):
        super().__init__(chart, parent)
        self.full_chart = chart
        self.timeline_data = timeline_data
        self.full_series = chart.series()
        self.zoomed_in = False
        self.zoomed_series = None
        self.setMouseTracking(True)
        self.annotations = []  # Список для хранения аннотаций
        self.date_str = date_str
    def mouseDoubleClickEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return  # Учитываем только двойной клик левой кнопкой мыши
        
        chart_pos = self.chart().mapToValue(QPointF(event.pos()))
        x_click = chart_pos.x()
        
        if self.zoomed_in:
            self.resetChart()
            self.zoomed_in = False
        else:
            for series in self.chart().series():
                pts = series.points()
                if len(pts) < 2:
                    continue
                start_x = pts[0].x()
                end_x = pts[1].x()
                if start_x <= x_click <= end_x:
                    self.zoomed_series = series
                    self.zoomInToSeries(series)
                    self.zoomed_in = True
                    break
        super().mouseDoubleClickEvent(event)
    
    def zoomInToSeries(self, series: QLineSeries):
        chart = self.chart()
        for s in list(chart.series()):
            chart.removeSeries(s)
        for ax in list(chart.axes()):
            chart.removeAxis(ax)
        
        pts = series.points()
        start_val = pts[0].x()
        end_val = pts[1].x()
        start_dt = QDateTime.fromMSecsSinceEpoch(int(start_val))
        end_dt = QDateTime.fromMSecsSinceEpoch(int(end_val))
        
        chart.addSeries(series)
        status = "Unknown"
        for seg in self.timeline_data:
            seg_start = QDateTime.fromString(seg['start_time'], Qt.DateFormat.ISODate)
            if abs(seg_start.toMSecsSinceEpoch() - start_val) < 1000:
                status = seg['state']
                break
        axisX = QDateTimeAxis()
        axisX.setFormat("HH:mm:ss")
        axisX.setRange(start_dt, end_dt)
        axisX.setTitleText(stats_texts.get(status, 'Unknown'))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        axisX.setTitleFont(font)
        axisX.setGridLineVisible(False)
        axisX.setLabelsBrush(QBrush(QColor("white")))
        axisX.setTitleBrush(QBrush(QColor("white")))
        chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axisX)
        
        axisY = QValueAxis()
        axisY.setRange(0, 10)
        axisY.hide()
        chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axisY)

        
        
        chart.update()
    
    def resetChart(self):
        chart = self.chart()
        for annotation in self.annotations:
            chart.scene().removeItem(annotation)
        self.annotations.clear()
        
        for s in list(chart.series()):
            chart.removeSeries(s)
        for ax in list(chart.axes()):
            chart.removeAxis(ax)
        
        for s in self.full_series:
            chart.addSeries(s)
        
        axisX = QDateTimeAxis()
        axisX.setFormat("HH:mm")
        min_time = min(seg['start_time'] for seg in self.timeline_data)
        max_time = max(seg['end_time'] for seg in self.timeline_data)
        start_dt = QDateTime.fromString(min_time, Qt.DateFormat.ISODate)
        end_dt = QDateTime.fromString(max_time, Qt.DateFormat.ISODate)
        axisX.setRange(start_dt, end_dt)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        axisX.setTitleText(self.date_str)
        axisX.setTitleFont(font)
        axisX.setGridLineVisible(False)
        axisX.setLabelsBrush(QBrush(QColor("white")))
        axisX.setTitleBrush(QBrush(QColor("white")))
        chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
        for s in chart.series():
            s.attachAxis(axisX)
        
        axisY = QValueAxis()
        axisY.setRange(0, 10)
        axisY.hide()
        chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)
        for s in chart.series():
            s.attachAxis(axisY)
        
        chart.update()


def build_timeline_chart(timeline_data, date_str):
    """
    timeline_data: список словарей с ключами 'state', 'start_time', 'end_time'
    date_str: строка даты в формате "yyyy-MM-dd"
    """
    # Создаем диаграмму
    chart = QChart()
    chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
    chart.setBackgroundBrush(QBrush(QColor(6, 6, 6)))
    chart.setMargins(QMargins(0, 0, 0, 60))
    chart.setTitle("Timeline of statistics")
    font = QFont()
    font.setPointSize(14)
    chart.setTitleFont(font)
    chart.setTitleBrush(QBrush(QColor(255, 255, 255, 200)))
    chart.legend().hide()
    
    # Функция выбора цвета по состоянию
    def state_color(state: str) -> QColor:
        mapping = {
            "offline": QColor("#6e6e6e"),
            "voice_online": QColor("#00ffdd"),
            "voice_mute": QColor("#aeff00"),
            "voice_deaf": QColor("#ff5500"),
            "voice_afk": QColor("#ff00d0"),
            "voice_alone": QColor("#a200ff"),
            "online": QColor("#288c00"),
        }
        return mapping.get(state, QColor(6, 6, 6))
    
    # Собираем данные для оси X (в мс) и длительности (для вычисления x)
    x_values = []
    durations = []
    colors = []
    for segment in timeline_data:
        seg_start = QDateTime.fromString(segment['start_time'], Qt.DateFormat.ISODate)
        seg_end   = QDateTime.fromString(segment['end_time'], Qt.DateFormat.ISODate)
        duration = seg_start.secsTo(seg_end)
        x_val = seg_start.toMSecsSinceEpoch()
        x_values.append(x_val)
        durations.append(duration)
        colors.append(state_color(segment['state']))

    # Настраиваем ось X (QDateTimeAxis)
    axisX = QDateTimeAxis()
    axisX.setFormat("HH:mm")
    min_time = min(segment['start_time'] for segment in timeline_data)
    max_time = max(segment['end_time'] for segment in timeline_data)
    start_dt = QDateTime.fromString(min_time, Qt.DateFormat.ISODate)
    end_dt = QDateTime.fromString(max_time, Qt.DateFormat.ISODate)
    axisX.setRange(start_dt, end_dt)
    font = QFont()
    font.setPointSize(12)
    font.setBold(True)
    axisX.setTitleText(date_str)
    axisX.setTitleFont(font)
    axisX.setGridLineVisible(False)
    axisX.setLabelsBrush(QBrush(QColor("white")))
    axisX.setTitleBrush(QBrush(QColor("white")))
    chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)

    # Ось Y задается вручную (например, от 0 до 20), чтобы линия располагалась на нужном уровне (например, y = 3)
    axisY = QValueAxis()
    axisY.setRange(0, 10)
    axisY.hide()
    chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)

    # Функция-обработчик для сигнала hovered
    def handle_hover(point, state):
        if state:
            time = QDateTime.fromMSecsSinceEpoch(int(point.x()))
            text = time.toString("HH:mm:ss")
            pos = QCursor.pos()
            pos.setY(pos.y() - 50)  # смещение на 20 пикселей вверх
            pos.setX(pos.x() - 20)
            QToolTip.showText(pos, text)
        else:
            QToolTip.hideText()

    for i, x_val in enumerate(x_values):
        series = QLineSeries()
        series.append(x_val, 3)
        series.append(x_val + durations[i] * 1000, 3)
        pen = QPen(colors[i], 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
        series.setPen(pen)
        chart.addSeries(series)
        series.attachAxis(axisX)
        series.attachAxis(axisY)
        # Подключаем сигнал hovered для отображения tooltip
        series.hovered.connect(handle_hover)

    chart_view = CustomChartView(chart, timeline_data, date_str=date_str)
    chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
    chart_view.setRubberBand(QChartView.RubberBand.HorizontalRubberBand)
    chart_view.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
    chart_view.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
    chart_view.setMouseTracking(True)
    return chart_view