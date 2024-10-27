import sys
import json
import shutil
import time
from datetime import datetime, timedelta
import numpy as np
import os
import asyncio
import resources
import websockets
from qasync import QEventLoop, asyncSlot
from rainbotAPI_client import RainBot_Websocket
from designe import Ui_MainWindow 
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtCore import QIODevice, QBuffer, QTimer, Qt, QPropertyAnimation, QRect, QEasingCurve, QRectF, pyqtSlot, pyqtSignal
from PyQt6.QtMultimedia import QMediaDevices, QAudioSource, QAudioFormat
from PyQt6.QtWidgets import QMainWindow, QApplication, QDockWidget ,QPushButton, QWidget,QVBoxLayout, QHBoxLayout,QMessageBox, QSlider, QLabel, QTextEdit, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QFileDialog
from PyQt6.QtGui import QIcon, QPainter, QColor, QPainterPath, QCursor, QGuiApplication,  QTextDocument, QTextCursor
from ctypes import windll, wintypes
import ctypes
from win import *



class MainWindow(QMainWindow):
    searchRequested = pyqtSignal(str, bool)
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
        self.is_maximized = False
        self.mouse_start_position = None
        self.window_start_position = None
        self.window_start_size = None
        self.minimized_buttons_texts_dict = {}
        self.logs_was_loaded = False
        self.find_label_hidden = False

        # # 
        # # init function/ on load 
        # #

        self.ui.textBrowser.setFontPointSize(11)
        self.ui.textBrowser.setFontFamily("JetBrains Mono,Helvetica")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.switch_tab(3, 500)
        self.buttons_hover_init()
        self.toggle_find()
        self.window_resizing_frame()


        # # 
        # # widgets init
        # #
        

        self.setMouseTracking(True)
        self.ui.centralwidget.setMouseTracking(True)

        self.ui.label_6.setText("")
        self.ui.label_7.setText("")

        self.ui.wbsocket_btn.setChecked(True)

        self.ui.build_info.setText("Build: 1.3.0")
        self.ui.websck_status.hide()


        

        self.setDisabled_tabs(True)

        # #
        # # connectors
        # #

        self.ui.headerBar.mousePressEvent = self.label_mouse_press_event


        self.ui.LineSenDCommand.returnPressed.connect(self.sent_console_command)
        self.ui.send_btn.clicked.connect(self.sent_console_command)

        self.ui.conect_websc.clicked.connect(self.connectWS)

        self.ui.menuButton.clicked.connect(self.left_menu_minimize)

        self.ui.minimize_btn.clicked.connect(self.minimize_window)
        self.ui.close_btn.clicked.connect(self.close_window_like_windows)
        self.ui.fullscreen_btn.clicked.connect(self.toggle_fullscreen)

        
        self.ui.terminal_btn.clicked.connect(lambda: self.switch_tab(0))
        self.ui.stats_btn.clicked.connect(lambda: self.switch_tab(1))
        self.ui.logs_btn.clicked.connect(lambda: self.switch_tab(2))
        self.ui.Settings_btn.clicked.connect(lambda: self.switch_tab(4))
        self.ui.wbsocket_btn.clicked.connect(lambda: self.switch_tab(3))
        self.ui.server_btn.clicked.connect(lambda: self.switch_tab(5))

        self.ui.button_find_in_console.clicked.connect(self.toggle_find)
        self.ui.upBotton.clicked.connect(self.onUpClicked)
        self.ui.downBotton.clicked.connect(self.onDownClicked)
        self.searchRequested.connect(self.onSearchRequested)



        # #
        # # websocket
        # # 
        self.websocket_client = RainBot_Websocket()
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
            self.ui.server_btn: {"default": ":/MainIcons/icons/serverW.png", "hover": ":/MainIcons/icons/serverB.png", "checkable": True},
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
            if child.objectName() != 'find_label_2':
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
                    self.animate_button(button, QtCore.QSize(50, 16777215))
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
    def animate_button(self, button, button_size):
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



    def toggle_fullscreen(self):
        hwnd = int(self.winId())
        GWL_STYLE = -16
        GWL_EXSTYLE = -20
        style = GetWindowLongPtr(hwnd, GWL_STYLE)

        if not self.is_maximized:
            self.update_window_styles(0)
            # Save the current window position and size
            rect = RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            self.saved_rect = (rect.left, rect.top, rect.right, rect.bottom)
            self.saved_style = style

            # Modify window style to remove borders and title bar
            style &= ~(0x00C00000 | 0x00040000)  # Remove WS_CAPTION and WS_THICKFRAME
            style |= 0x80000000  # Add WS_POPUP
            SetWindowLongPtr(hwnd, GWL_STYLE, style)

            # Get monitor info
            hMonitor = ctypes.windll.user32.MonitorFromWindow(hwnd, 0x00000002)  # MONITOR_DEFAULTTONEAREST
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            ctypes.windll.user32.GetMonitorInfoW(hMonitor, ctypes.byref(mi))

            # Set window to fullscreen
            ctypes.windll.user32.SetWindowPos(
                hwnd, None,
                mi.rcMonitor.left, mi.rcMonitor.top,
                mi.rcMonitor.right - mi.rcMonitor.left,
                mi.rcMonitor.bottom - mi.rcMonitor.top,
                0x0040)  # SWP_NOZORDER

            # Inform the GUI framework about the change
            self.setGeometry(
                mi.rcMonitor.left, mi.rcMonitor.top,
                mi.rcMonitor.right - mi.rcMonitor.left,
                mi.rcMonitor.bottom - mi.rcMonitor.top
            )
            self.is_maximized = True
        else:
            self.update_window_styles(8)
            # Restore original window style
            style = self.saved_style
            SetWindowLongPtr(hwnd, GWL_STYLE, style)

            # Restore window size and position
            x, y, right, bottom = self.saved_rect
            width = right - x
            height = bottom - y

            # Adjust window rectangle to account for the non-client area
            window_rect = RECT()
            window_rect.left = x
            window_rect.top = y
            window_rect.right = x + width
            window_rect.bottom = y + height

            # Get extended window style
            exStyle = GetWindowLongPtr(hwnd, GWL_EXSTYLE)

            # Adjust the window rectangle to include the non-client area
            ctypes.windll.user32.AdjustWindowRectEx(ctypes.byref(window_rect), style, False, exStyle)

            # Set window position and size
            ctypes.windll.user32.SetWindowPos(
                hwnd, None,
                window_rect.left, window_rect.top,
                window_rect.right - window_rect.left,
                window_rect.bottom - window_rect.top,
                0x0040)  # SWP_NOZORDER

            # Inform the GUI framework about the change
            self.setGeometry(
                window_rect.left, window_rect.top,
                window_rect.right - window_rect.left,
                window_rect.bottom - window_rect.top
            )
            self.is_maximized = False

        # Force a layout update and repaint
        self.update()
        self.repaint()


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
    
    def close_window_like_windows(self):
        # Получаем дескриптор окна
        hwnd = int(self.winId())
        hWnd = wintypes.HWND(hwnd)

        # Определяем константы
        WM_SYSCOMMAND = 0x0112
        SC_CLOSE = 0xF060

        # Отправляем сообщение WM_SYSCOMMAND с параметром SC_CLOSE
        windll.user32.PostMessageW(hWnd, WM_SYSCOMMAND, SC_CLOSE, 0)



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


    def onSearchRequested(self, text, forward):
        self.findInTextBrowser(text, forward)

    def findInTextBrowser(self, text, forward=True):
        cursor = self.ui.textBrowser.textCursor()
        options = QTextDocument.FindFlag(0)
        if not forward:
            options |= QTextDocument.FindFlag.FindBackward

        found = self.ui.textBrowser.find(text, options)
        if not found:
            if forward:
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                
            else:
                cursor.movePosition(QTextCursor.MoveOperation.End)

            self.ui.textBrowser.setTextCursor(cursor)
            found = self.ui.textBrowser.find(text, options)
            if not found:
                QMessageBox.information(self, "Search", f"Cannot find '{text}'")

    def toggle_find(self):
        if not self.find_label_hidden:
            self.ui.find_label_2.hide()
            self.find_label_hidden = True
        else:
            self.ui.find_label_2.show()
            self.find_label_hidden = False
    def onUpClicked(self):
        text = self.ui.Find_line.text()
        if text:
            self.ui.Find_line.selectAll()
            self.searchRequested.emit(text, False)

    def onDownClicked(self):
        text = self.ui.Find_line.text()
        if text:
            self.ui.Find_line.selectAll()
            self.searchRequested.emit(text, True)

    def window_resizing_frame(self):
        hwnd = int(self.winId())
        GWL_STYLE = -16
        WS_CAPTION = 0x00C00000
        WS_THICKFRAME = 0x00040000
        WS_MAXIMIZEBOX = 0x00010000
        WS_MINIMIZEBOX = 0x00020000

        # Modify the window style to include WS_THICKFRAME
        style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, GWL_STYLE)
        style = style & ~WS_CAPTION | WS_THICKFRAME | WS_MAXIMIZEBOX | WS_MINIMIZEBOX
        ctypes.windll.user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style)

        SWP_FRAMECHANGED = 0x0020
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOZORDER = 0x0004

        # Apply the changes
        ctypes.windll.user32.SetWindowPos(
            hwnd, None, 0, 0, 0, 0,
            SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER
        )







        ##
        ## EVENTS
        ##


    def nativeEvent(self, eventType, message):
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())

            if msg.message == WM_NCCALCSIZE:
                # Remove the standard frame by returning 0
                return True, 0

            elif msg.message == WM_NCHITTEST:
                # Handle the hit test to allow resizing
                pos = QtCore.QPoint(
                    ctypes.c_short(msg.lParam & 0xFFFF).value,
                    ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
                )
                pos = self.mapFromGlobal(pos)
                w, h = self.width(), self.height()
                x, y = pos.x(), pos.y()
                lx = x
                rx = w - x
                ty = y
                by = h - y

                # Define the resize border width
                border_width = 8

                # Determine the region for resizing
                if ty <= border_width and lx <= border_width:
                    return True, HTTOPLEFT
                elif ty <= border_width and rx <= border_width:
                    return True, HTTOPRIGHT
                elif by <= border_width and lx <= border_width:
                    return True, HTBOTTOMLEFT
                elif by <= border_width and rx <= border_width:
                    return True, HTBOTTOMRIGHT
                elif lx <= border_width:
                    return True, HTLEFT
                elif rx <= border_width:
                    return True, HTRIGHT
                elif ty <= border_width:
                    return True, HTTOP
                elif by <= border_width:
                    return True, HTBOTTOM
                else:
                    return True, HTCLIENT

        # If the event was not handled, return False and 0
        return False, 0

    
    def label_mouse_press_event(self, event):
        """Simulate the Windows title bar click to move the window."""
        if event.button() == Qt.MouseButton.LeftButton:
            hwnd = int(self.winId())
            ctypes.windll.user32.ReleaseCapture()
            ctypes.windll.user32.SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0)





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

    def resizeEvent(self, event):
        super().resizeEvent(event)





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
            
            
            await self.websocket_client.connect(uri='ws://192.168.0.106:8765')

            self.ui.textBrowser.clear()
            
            await asyncio.sleep(2)
            if self.websocket_client.isConnected():
                await self.load_logs()
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