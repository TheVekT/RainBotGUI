from PyQt6.QtCharts import (
    QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
)
from PyQt6.QtWidgets import (
    QGraphicsView, QToolTip
)
from PyQt6.QtCore import (
    QDateTime, Qt, QMargins
)
from PyQt6.QtGui import (
    QColor, QPainter, QBrush, QFont, QPen, QCursor
)

def build_timeline_chart(timeline_data, date_str):
    """
    timeline_data: список словарей с ключами 'state', 'start_time', 'end_time'
    date_str: строка даты в формате "yyyy-MM-dd"
    """
    # Создаем диаграмму
    chart = QChart()
    chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
    chart.setBackgroundBrush(QBrush(QColor(6, 6, 6)))
    chart.setMargins(QMargins(0, 0, 0, 100))
    chart.setTitle("Timeline of statistics")
    font = QFont()
    font.setPointSize(14)
    chart.setTitleFont(font)
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
    axisX.setGridLineVisible(False)
    chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)

    # Ось Y задается вручную (например, от 0 до 20), чтобы линия располагалась на нужном уровне (например, y = 3)
    axisY = QValueAxis()
    axisY.setRange(0, 20)
    axisY.hide()
    chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)

    # Функция-обработчик для сигнала hovered
    def handle_hover(point, state):
        if state:
            time = QDateTime.fromMSecsSinceEpoch(int(point.x()))
            text = time.toString("HH:mm")
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

    # Создаем QChartView, включаем сглаживание, зум и прокрутку
    chart_view = QChartView(chart)
    chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
    chart_view.setRubberBand(QChartView.RubberBand.HorizontalRubberBand)
    chart_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
    chart_view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
    chart_view.setMouseTracking(True)  # Включаем отслеживание мыши для получения hovered-событий

    return chart_view