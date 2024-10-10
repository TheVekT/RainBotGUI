import sys
import json
import shutil
import time
from datetime import datetime, timedelta
import numpy as np
import wave
import os
import asyncio
import resources
from qasync import QEventLoop, asyncSlot
from rainbotAPI_client import RainBot_Websocket
from datetime import datetime
from designe import Ui_MainWindow 
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import QIODevice, QBuffer, QTimer, Qt, QPropertyAnimation, QRect, QEasingCurve, QRectF, pyqtSlot
from PyQt6.QtMultimedia import QMediaDevices, QAudioSource, QAudioFormat
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox,QPushButton, QWidget, QSlider, QLabel, QTextEdit, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QFileDialog
from PyQt6.QtGui import QIcon, QPainter, QColor, QPainterPath, QCursor, QGuiApplication

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)



        # #
        # # atributes
        # #
        self.left_menu_minimized = False
        self.animations = []
        self.wasMaximized = False
        self.is_dragging = False
        self.is_resizing = False
        self.mouse_start_position = None
        self.window_start_position = None
        self.window_start_size = None
        self.minimized_buttons_texts_dict = {}
        self.logs_was_loaded = False


        # # 
        # # init function/ on load 
        # #

        self.ui.textBrowser.setFontPointSize(11)
        self.ui.textBrowser.setFontFamily("JetBrains Mono,Helvetica")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setDisabled_tabs(True)
        self.switch_tab(3, 500)
        self.buttons_hover_init()

        # # 
        # # widgets init
        # #
                    # resize handler init
        self.resize_handle = QLabel(self)
        self.resize_handle.setGeometry(self.width() - 8, self.height() - 8, 8, 8)
        self.resize_handle.setStyleSheet("background-color: #FFDAB9;\n"
                                         "border-radius: 4px;\n"
                                         )
        self.resize_handle.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SizeFDiagCursor))
        self.resize_handle.setMouseTracking(True)
        self.resize_handle.show()

        self.setMouseTracking(True)
        self.ui.centralwidget.setMouseTracking(True)

        self.ui.label_6.setText("")
        self.ui.label_7.setText("")

        self.ui.wbsocket_btn.setChecked(True)

        self.ui.build_info.setText("Build: 1.2.2")
        self.ui.websck_status.hide()


        # #
        # # connectors
        # #

        self.ui.headerBar.mousePressEvent = self.label_mouse_press_event
        self.ui.headerBar.mouseMoveEvent = self.label_mouse_move_event
        self.ui.headerBar.mouseReleaseEvent = self.label_mouse_release_event

        self.ui.LineSenDCommand.returnPressed.connect(self.sent_console_command)
        self.ui.send_btn.clicked.connect(self.sent_console_command)

        self.ui.conect_websc.clicked.connect(self.connectWS)

        self.ui.menuButton.clicked.connect(self.left_menu_minimize)

        self.ui.minimize_btn.clicked.connect(self.minimize_window)
        self.ui.close_btn.clicked.connect(self.close_window)
        self.ui.fullscreen_btn.clicked.connect(self.toggle_fullscreen)

        
        self.ui.terminal_btn.clicked.connect(lambda: self.switch_tab(0))
        self.ui.stats_btn.clicked.connect(lambda: self.switch_tab(1))
        self.ui.logs_btn.clicked.connect(lambda: self.switch_tab(2))
        self.ui.Settings_btn.clicked.connect(lambda: self.switch_tab(4))
        self.ui.wbsocket_btn.clicked.connect(lambda: self.switch_tab(3))


        # #
        # # websocket
        # # 
        self.websocket_client = RainBot_Websocket("ws://192.168.0.106:8765")
                # Подключаем сигнал нового лога к слоту обновления UI
        self.websocket_client.new_log_signal.connect(self.handle_new_log_message)
        self.websocket_client.connection_closed.connect(self.WS_on_diconnect)
###########                        ###########
###########    End of __init__     ###########       
###########                        ###########  
###########    Metods              ###########       
###########                        ###########



        ##
        ##  Gui functional
        ##


    def buttons_hover_init(self):
        self.buttons_icons = {
            self.ui.terminal_btn: {"default": ":/MainIcons/icons/terminalW.png", "hover": ":/MainIcons/icons/terminalB.png", "checkable": True},
            self.ui.menuButton: {"default": ":/MainIcons/icons/sideBarW.png", "hover": ":/MainIcons/icons/sideBarB.png", "checkable": False},
            self.ui.Settings_btn: {"default": ":/MainIcons/icons/settingsW.png", "hover": ":/MainIcons/icons/settingsB.png", "checkable": True},
            self.ui.wbsocket_btn: {"default": ":/MainIcons/icons/websocketW.png", "hover": ":/MainIcons/icons/websocketB.png", "checkable": True},
            self.ui.logs_btn: {"default": ":/MainIcons/icons/logsW.png", "hover": ":/MainIcons/icons/logsB.png", "checkable": True},
            self.ui.stats_btn: {"default": ":/MainIcons/icons/statsW.png", "hover": ":/MainIcons/icons/statsB.png", "checkable": True},
            self.ui.com_help_btn: {"default": ":/MainIcons/icons/command_helpW.png", "hover": ":/MainIcons/icons/command_helpB.png", "checkable": False},
            self.ui.send_btn: {"default": ":/MainIcons/icons/sendW.png", "hover": ":/MainIcons/icons/sendB.png", "checkable": False},
        }

        # Привязываем начальные иконки и события к кнопкам
        for button, icons in self.buttons_icons.items():
            button.setIcon(QIcon(icons["default"]))
            button.setCheckable(icons["checkable"])  # Устанавливаем состояние checkable
            button.enterEvent = self.create_enter_event(button)
            button.leaveEvent = self.create_leave_event(button)

            # Если кнопка checkable, привязываем слот для отслеживания состояния checked
            if icons["checkable"]:
                button.toggled.connect(self.update_icon_on_toggle)


    # Функция для переключения вкладки и анимации
    @pyqtSlot(int)
    def switch_tab(self, index, duration=200):
        # Установить текущий индекс вкладки
        self.ui.CentralTabs.setCurrentIndex(index)
        
        # Получить текущий виджет (вкладку)
        current_widget = self.ui.CentralTabs.widget(index)

        # Анимация fade in для каждого дочернего элемента
        for child in current_widget.findChildren(QWidget):
            self.fade_in_animation(child, duration)


    # Функция анимации fade in
    def fade_in_animation(self, widget, duration):
        # Устанавливаем эффект прозрачности
        opacity_effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(opacity_effect)

        # Делаем виджет невидимым перед анимацией
        widget.setVisible(True)
        opacity_effect.setOpacity(0)  # Изначально виджет невидим

        # Настраиваем анимацию для эффекта прозрачности
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(duration)  # Длительность анимации
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # Плавность анимации
        animation.setStartValue(0)
        animation.setEndValue(1)

        # Храним анимацию, чтобы избежать её удаления
        self.animations.append(animation)

        # Обработчик завершения анимации
        def on_animation_finished():
            # Убираем эффект прозрачности после завершения
            widget.setGraphicsEffect(None)

        # Привязываем обработчик к завершению анимации
        animation.finished.connect(on_animation_finished)
        
        # Запуск анимации
        animation.start()
    # Универсальная функция для создания enterEvent
    def create_enter_event(self, button):
        def on_button_hover(event):
            if not button.isChecked():  # Только если кнопка не находится в состоянии checked
                button.setIcon(QIcon(self.buttons_icons[button]["hover"]))
            super(MainWindow, self).enterEvent(event)
        return on_button_hover
    
    # Универсальная функция для создания leaveEvent
    def create_leave_event(self, button):
        def on_button_leave(event):
            # Если кнопка не находится в состоянии checked, меняем иконку на default
            if not button.isChecked():
                button.setIcon(QIcon(self.buttons_icons[button]["default"]))
            super(MainWindow, self).leaveEvent(event)
        return on_button_leave
    def left_menu_minimize(self):
        if not self.left_menu_minimized:  # Свернуть меню
            self.animate_menu(QtCore.QSize(60, 0), QtCore.QSize(50, 0))
            for button in self.ui.left_btns.children():
                if isinstance(button, QPushButton):
                    self.animate_leftMenu_button(button, QtCore.QSize(50, 16777215))
                    self.minimized_buttons_texts_dict[button.objectName()] = button.text()
                    
                    button.setText("")
            self.left_menu_minimized = True
        else:  # Развернуть меню
            self.animate_menu(QtCore.QSize(300, 0), QtCore.QSize(280, 0))
            for button in self.ui.left_btns.children():
                if isinstance(button, QPushButton):
                    button.setMaximumSize(QtCore.QSize(280, 16777215))
                    button.setText(self.minimized_buttons_texts_dict.get(button.objectName(), ""))
            self.left_menu_minimized = False

    def animate_menu(self, side_size, btns_size):
        # Анимация для self.ui.leftSide
        animation1 = QPropertyAnimation(self.ui.leftSide, b"minimumSize")
        animation1.setDuration(200)
        animation1.setStartValue(self.ui.leftSide.minimumSize())
        animation1.setEndValue(side_size)
        animation1.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Анимация для self.ui.left_btns
        animation2 = QPropertyAnimation(self.ui.left_btns, b"minimumSize")
        animation2.setDuration(200)
        animation2.setStartValue(self.ui.left_btns.minimumSize())
        animation2.setEndValue(btns_size)
        animation2.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Запуск анимации и сохранение ссылок на них
        self.animations.append(animation1)
        self.animations.append(animation2)
        animation1.start()
        animation2.start()
    def animate_leftMenu_button(self, button, button_size):
        # Анимация для self.ui.leftSide
        animation1 = QPropertyAnimation(button, b"maximumSize")
        animation1.setDuration(200)
        animation1.setStartValue(self.ui.leftSide.maximumSize())
        animation1.setEndValue(button_size)
        animation1.setEasingCurve(QEasingCurve.Type.OutQuad)
        # Запуск анимации и сохранение ссылок на них
        self.animations.append(animation1)
        animation1.start()
    # Слот для обновления иконки при изменении состояния checked
    def update_icon_on_toggle(self, checked):
        button = self.sender()  # Получаем кнопку, которая вызвала сигнал
        if checked:
            # Если кнопка активна (checked), сохраняем иконку hover
            button.setIcon(QIcon(self.buttons_icons[button]["hover"]))
        else:
            # Если кнопка становится неактивной, возвращаем иконку по умолчанию
            button.setIcon(QIcon(self.buttons_icons[button]["default"]))



    def toggle_fullscreen(self, normal=False):
        if self.isMaximized():
            # Вернуться в обычный режим
            self.showNormal()
            self.update_window_styles(border_radius=8)
        elif normal:
            # Вернуться в обычный режим вручную
            self.showNormal()
            self.update_window_styles(border_radius=8)
        else:
            # Перейти в полноэкранный режим
            self.showMaximized()
            self.update_window_styles(border_radius=0)


    # Функция для обновления стилей в зависимости от состояния окна
    def update_window_styles(self, border_radius):
        # Устанавливаем стили окна
        self.setStyleSheet(f"QWidget{{"
                        f"background-color: rgb(4, 4, 4);"
                        f"font-family: 'JetBrains Mono', Helvetica;"
                        f"border-radius: {border_radius}px;}}")

        # Устанавливаем стили заголовка
        self.ui.headerBar.setStyleSheet(f"border-radius: 0;"
                                        f"background-color: black;"
                                        f"border-top-right-radius: {border_radius}px;"
                                        f"border-top-left-radius: {border_radius}px;")

        # Устанавливаем стили кнопки закрытия
        self.ui.close_btn.setStyleSheet(f"QPushButton{{"
                                        f"border-top-right-radius: {border_radius}px;"
                                        f"border-top-left-radius: 0px;}}"
                                        f"QPushButton:hover{{"
                                        f"background-color: rgb(170, 0, 0);}}")
    def minimize_window(self):
        if self.isMaximized():
            self.showNormal()
            self.wasMaximized = True
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(100)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)

        # Запускаем анимацию и скрываем окно по завершении
        self.animation.start()
        self.animation.finished.connect(self.showMinimized)
    
    def close_window(self):
        if self.isMaximized():
            self.showNormal()
        current_height = self.height() 

        # Получаем текущие координаты окна
        current_x = self.x()
        current_y = self.y()
        current_width = self.width()

        # Настраиваем анимацию изменения геометрии
        self.animation2 = QPropertyAnimation(self, b'geometry')
        self.animation2.setDuration(100)
        self.animation2.setStartValue(QRect(current_x, current_y, current_width, current_height))
        self.animation2.setEndValue(QRect(current_x+30, current_y+30, current_width-60, current_height-60))
        
        # Запускаем анимацию и скрываем окно по завершении
        
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(100)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        # Запускаем анимацию и скрываем окно по завершении
        self.animation.start()
        self.animation2.start()
        self.animation.finished.connect(lambda: self.close())


    def restore_window(self):
        if self.wasMaximized == True:
            self.showMaximized()
            self.wasMaximized = False
        elif self.wasMaximized == False:
        # Восстанавливаем окно и делаем его видимым
            self.showNormal()

        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(100)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def setDisabled_tabs(self, disable: bool):
        for i in range(self.ui.CentralTabs.count()):
            tab_widget = self.ui.CentralTabs.widget(i)
            
            # Проверяем, не является ли вкладка исключением по имени
            if tab_widget.objectName() != "websocket_tab":
                # Создаем эффект прозрачности
                opacity_effect = QGraphicsOpacityEffect()

                # Если передано значение True, уменьшаем прозрачность до 20%
                if disable:
                    opacity_effect.setOpacity(0.2)  # 20% прозрачности
                    tab_widget.setGraphicsEffect(opacity_effect)
                else:
                    # Удаляем эффект, сбрасывая его
                    tab_widget.setGraphicsEffect(None)  # Удаляем эффект прозрачности

                # Отключаем или включаем виджеты внутри вкладки
                for child in tab_widget.findChildren(QWidget):
                    child.setDisabled(disable)


    def set_neon_glow(self, frame, color="#00FF00", enable=True):
        """
        Создает анимированное неоновое свечение для существующего элемента QFrame.

        :param frame: QFrame элемент, на котором будет применен эффект.
        :param color: Цвет свечения в формате HEX (по умолчанию зеленый).
        :param enable: Включение или отключение эффекта.
        """
        if enable:
            # Создаем эффект тени для имитации свечения
            shadow_effect = QGraphicsDropShadowEffect()
            shadow_effect.setBlurRadius(0)  # Начальный радиус свечения
            shadow_effect.setColor(QColor(color))
            shadow_effect.setOffset(0, 0)  # Центрируем свечение


            
            # Применяем эффект к переданному элементу
            frame.setGraphicsEffect(shadow_effect)

            # Анимация для увеличения радиуса свечения
            self.animation = QPropertyAnimation(shadow_effect, b"blurRadius")
            self.animation.setDuration(1000)  # Длительность анимации
            self.animation.setStartValue(0)  # Начальное значение (без свечения)
            self.animation.setEndValue(100)  # Максимальное свечение
            self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Кривая для плавного эффекта
            self.animation.start()
        else:
            # Убираем эффект свечения
            frame.setGraphicsEffect(None)





        ##
        ## EVENTS
        ##


    
    def label_mouse_press_event(self, event):
        """Запоминаем начальные позиции при нажатии на метку."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.mouse_start_position = event.globalPosition().toPoint()
            self.window_start_position = self.frameGeometry().topLeft()


    def label_mouse_move_event(self, event):
        """Перемещаем окно при перемещении мыши."""
        if self.is_dragging:
            if self.isMaximized():
                self.toggle_fullscreen(True)
            delta = event.globalPosition().toPoint() - self.mouse_start_position
            self.move(self.window_start_position + delta)


    def label_mouse_release_event(self, event):
        """Прекращаем перетаскивание при отпускании кнопки."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False


    def resizeEvent(self, event):
        """Переопределение события изменения размера окна для обновления позиции лейбла."""
        super().resizeEvent(event)
        self.resize_handle.move(self.width() - 8, self.height() - 8)


    def mousePressEvent(self, event):
        """Отслеживание начала изменения размера окна."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Проверяем, нажата ли мышь на нашем resize_handle
            if self.resize_handle.geometry().contains(event.pos()):
                self.is_resizing = True
                self.old_pos = event.globalPosition().toPoint()  # Обновлено на globalPosition()


    def mouseMoveEvent(self, event):
        """Изменение размера окна при перемещении мыши."""
        if self.is_resizing:
            delta = event.globalPosition().toPoint() - self.old_pos  # Обновлено на globalPosition()
            global_pos = event.globalPosition().toPoint()  # Глобальные координаты курсора
            local_pos = self.mapFromGlobal(global_pos)
            if global_pos.x() > self.old_pos.x():
                new_width = self.width() + delta.x() if self.resize_handle.x() < local_pos.x() else self.width()
            else:
                new_width = self.width() + delta.x()
            if global_pos.y() > self.old_pos.y():
                new_height = self.height() + delta.y() if self.resize_handle.y() < local_pos.y() else self.height()
            else:
                new_height = self.height() + delta.y()
            # Устанавливаем новый размер окна
            self.ui.textBrowser.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            self.resize(new_width, new_height)
            self.old_pos = event.globalPosition().toPoint()  # Обновляем позицию


    def mouseReleaseEvent(self, event):
        """Остановка изменения размера при отпускании мыши."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_resizing = False
            self.ui.textBrowser.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Устанавливаем цвет фона окна
        painter.setBrush(QColor(255, 255, 255))  # Белый фон, если необходимо
        painter.setPen(QtCore.Qt.PenStyle.NoPen)

        # Рисуем скругленный прямоугольник
        rect = self.rect()
        radius = 20
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)
        painter.drawPath(path)

        # Если хотите рисовать что-то поверх скругленного прямоугольника, например, фон
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOver)
        painter.setBrush(self.palette().window())
        painter.drawPath(path)


    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            if self.windowState() == Qt.WindowState.WindowNoState:
                self.restore_window()




        ##
        ## Websocket
        ##
    @asyncSlot()
    async def load_logs(self):
        logs = await self.websocket_client.get_logs()
        for log_str in logs:
            # Используем insertHtml, чтобы добавить логи с HTML-разметкой
            self.ui.textBrowser.append(log_str)




    @asyncSlot()
    async def sent_console_command(self):
        if self.ui.LineSenDCommand.text() != "":
            if self.ui.LineSenDCommand.text() == "/disconnect":
                await self.websocket_client.disconnect()
                self.ui.textBrowser.append(self.ui.LineSenDCommand.text())
                self.ui.LineSenDCommand.clear()
                return
            await self.websocket_client.send_command(self.ui.LineSenDCommand.text())
            self.ui.textBrowser.append(self.ui.LineSenDCommand.text())
            self.ui.LineSenDCommand.clear()

    @asyncSlot()
    async def WS_on_diconnect(self):
        self.ui.label_5.setPixmap(QtGui.QPixmap(":/MainIcons/icons/noconnected.png"))
        self.ui.conect_websc.setText("Connect")
        await self.websocket_client.disconnect()
        self.ui.label_6.setText("")
        self.ui.label_7.setText("")
        self.setDisabled_tabs(True)
        self.ui.conect_websc.setChecked(False)
        self.ui.websck_status.hide()

    @asyncSlot()
    async def connectWS(self):
        """Асинхронное подключение к WebSocket-серверу."""
        if not self.websocket_client.isConnected():
            self.ui.conect_websc.setText("Connecting...")
            self.ui.conect_websc.setDisabled(True)
            await self.websocket_client.connect()
            self.ui.textBrowser.clear()
            await self.load_logs()
            await asyncio.sleep(2)
            if self.websocket_client.isConnected():
                self.ui.label_5.setPixmap(QtGui.QPixmap(":/MainIcons/icons/connected.png"))
                self.ui.label_6.setText(f"<html><head/><body><p><span style=\" color:#89b086;\">Connected to:  </span><span style=\" font-weight:600; color:#69c5ca;\">{self.websocket_client.ip()}</span></p></body></html>")
                self.ui.label_7.setText(f"<html><head/><body><p><span style=\" color:#89b086;\">on port:  </span><span style=\" font-weight:600; color:#69c5ca;\">{self.websocket_client.port()}</span></p></body></html>")
                self.ui.label_6.show()
                self.ui.label_7.show()
                self.ui.conect_websc.setText("Connected")
                self.ui.conect_websc.setDisabled(False)
                self.setDisabled_tabs(False)
                self.ui.websck_status.show()
            else:
                self.ui.label_5.setPixmap(QtGui.QPixmap(":/MainIcons/icons/connectError.png"))
                await asyncio.sleep(3)
                self.ui.conect_websc.setText("Connect")
                self.ui.label_6.setText("")
                self.ui.label_7.setText("")
                self.ui.label_5.setPixmap(QtGui.QPixmap(":/MainIcons/icons/noconnected.png"))
                self.ui.conect_websc.setChecked(False)
                self.ui.conect_websc.setDisabled(False)
                self.setDisabled_tabs(True)
        else:
            self.ui.label_5.setPixmap(QtGui.QPixmap(":/MainIcons/icons/noconnected.png"))
            self.ui.conect_websc.setText("Connect")
            await self.websocket_client.disconnect()
            self.ui.label_6.setText("")
            self.ui.label_7.setText("")
            self.setDisabled_tabs(True)
    def handle_new_log_message(self, log_message):
        """Метод для обработки нового сообщения."""
        self.ui.textBrowser.append(log_message)
        # Здесь вы можете обновить элементы интерфейса с полученным сообщением
            

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Используем qasync для асинхронного событийного цикла
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        sys.exit(loop.run_forever())