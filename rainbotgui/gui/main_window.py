
import asyncio
import ctypes
from ctypes import windll, wintypes
from qasync import QEventLoop, asyncSlot

from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRectF, pyqtSlot
from PyQt6.QtWidgets import QMainWindow,QPushButton, QWidget, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QVBoxLayout, QCalendarWidget
from PyQt6.QtGui import QIcon, QPainter, QColor, QPainterPath

from rainbotgui.gui.resources import resources
from rainbotgui.utils.win import *
from rainbotgui.utils.btns_style import get_btns_style_settings
from rainbotgui.network.rainbotAPI_client import RainBot_Websocket
from rainbotgui.gui.main_window_ui import Ui_MainWindow
from rainbotgui.gui.pages_func import Terminal_Page, Websocket_Page, logs_Page, Settings_Page, Stats_Page
from rainbotgui.gui.widgets import Info_Notify, Success_Notify, Error_Notify, discord_member_button

class MainWindow(QMainWindow):
    websocket_setup = QtCore.pyqtSignal()
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # #
        # # atributes
        # #
        self.notify_queue = []
        self.left_menu_minimized = False
        self.animations = []
        self.is_maximized = False
        self.window_start_position = None
        self.minimized_buttons_texts_dict = {}
        self.saved_style = None

        
        
        # # 
        # # init function/ on load 
        # #

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.switch_tab(3, 500)
        self.buttons_hover_init()
        
        self.window_resizing_frame()
        self.websocket_client = RainBot_Websocket()

        # # 
        # # widgets init
        # #
        

        
        self.setMouseTracking(True)
        self.ui.centralwidget.setMouseTracking(True)

        self.set_build_version()
        
        self.setDisabled_tabs(True)

        # #
        # # connectors
        # #

        self.ui.headerBar.mousePressEvent = self.label_mouse_press_event



        self.ui.menuButton.clicked.connect(self.left_menu_minimize)
        self.ui.minimize_btn.clicked.connect(self.minimize_window)
        self.ui.close_btn.clicked.connect(self.close_window)
        self.ui.fullscreen_btn.clicked.connect(self.toggle_fullscreen)

        
        self.ui.terminal_btn.clicked.connect(lambda: self.switch_tab(0))
        self.ui.stats_btn.clicked.connect(lambda: self.switch_tab(1))
        self.ui.logs_btn.clicked.connect(lambda: self.switch_tab(2))
        self.ui.Settings_btn.clicked.connect(lambda: self.switch_tab(4))
        self.ui.wbsocket_btn.clicked.connect(lambda: self.switch_tab(3))
        self.ui.server_btn.clicked.connect(lambda: self.switch_tab(5))
        
        
        self.setup_pages()
        
        # #
        # # websocket
        # # 

        pass


###########                        ###########
###########    End of __init__     ###########       
###########                        ###########  
###########    Metods              ###########       
###########                        ###########


        ##
        ##  Gui functional
        ##
    def setup_pages(self):
        self.terminal_page = Terminal_Page(self.websocket_client, self.ui, self)
        self.websocket_page = Websocket_Page(self.websocket_client, self.ui, self)
        self.logs_page = logs_Page(self.websocket_client, self.ui, self)
        self.stats_page = Stats_Page(self.websocket_client, self.ui, self)
        self.settings_page = Settings_Page(self.websocket_client, self.ui, self)
        self.settings_page.load_settings()

    def buttons_hover_init(self):
        self.BUTTON_STYLE_SETTINGS = get_btns_style_settings(self.ui)
        # Привязываем начальные иконки и события к кнопкам
        for button, icons in self.BUTTON_STYLE_SETTINGS.items():
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
            if child.objectName() not in ('find_label_2'):
                if isinstance(child, QCalendarWidget) or child.objectName() in ('qt_calendar_yearedit', 'qt_calendar_prevmonth', 'qt_calendar_nextmonth'):
                    continue
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
                button.setIcon(QIcon(self.BUTTON_STYLE_SETTINGS[button]["hover"]))
            super(MainWindow, self).enterEvent(event)
        return on_button_hover
    
    # Универсальная функция для создания leaveEvent
    def create_leave_event(self, button):
        def on_button_leave(event):
            # Если кнопка не находится в состоянии checked, меняем иконку на default
            if not button.isChecked():
                button.setIcon(QIcon(self.BUTTON_STYLE_SETTINGS[button]["default"]))
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
            button.setIcon(QIcon(self.BUTTON_STYLE_SETTINGS[button]["hover"]))
        else:
            # Если кнопка становится неактивной, возвращаем иконку по умолчанию
            button.setIcon(QIcon(self.BUTTON_STYLE_SETTINGS[button]["default"]))



    def toggle_fullscreen(self):
        hwnd = int(self.winId())
        hWnd = wintypes.HWND(hwnd)

        if not self.is_maximized:
            # Максимизируем окно стандартным способом
            self.update_window_styles(0)
            windll.user32.PostMessageW(hWnd, WM_SYSCOMMAND, SC_MAXIMIZE, 0)
            self.is_maximized = True
        else:
            # Восстанавливаем окно стандартным способом
            self.update_window_styles(8)
            windll.user32.PostMessageW(hWnd, WM_SYSCOMMAND, SC_RESTORE, 0)
            self.is_maximized = False

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
    
    def close_window(self):
        # Получаем дескриптор окна
        hwnd = int(self.winId())
        hWnd = wintypes.HWND(hwnd)
        # Отправляем сообщение WM_SYSCOMMAND с параметром SC_CLOSE
        windll.user32.PostMessageW(hWnd, WM_SYSCOMMAND, SC_CLOSE, 0)

    def minimize_window(self):
        # Получаем дескриптор окна
        hwnd = int(self.winId())
        hWnd = wintypes.HWND(hwnd)
        # Отправляем сообщение WM_SYSCOMMAND с параметром SC_MINIMIZE
        windll.user32.PostMessageW(hWnd, WM_SYSCOMMAND, SC_MINIMIZE, 0)


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





    def window_resizing_frame(self):
        hwnd = int(self.winId())

        # Modify the window style to include WS_THICKFRAME
        style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, GWL_STYLE)
        style = style & ~WS_CAPTION | WS_THICKFRAME | WS_MAXIMIZEBOX | WS_MINIMIZEBOX
        ctypes.windll.user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style)

        # Apply the changes
        ctypes.windll.user32.SetWindowPos(
            hwnd, None, 0, 0, 0, 0,
            SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER
        )

    def set_build_version(self):
        from rainbotgui import __version__
        self.ui.build_info.setText(__version__)


            

        ##
        ## EVENTS
        ##
    

    
    
    
    
    

    def nativeEvent(self, eventType, message):
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            if msg.message == WM_NCCALCSIZE:
                # Remove the standard frame by returning 0
                return True, 0
            elif msg.message == WM_SIZE:  # WM_SIZE
                if msg.wParam == 2:  # SIZE_MAXIMIZED
                    if not self.is_maximized:
                        self.is_maximized = True
                        self.update_window_styles(0)
                elif msg.wParam == 0:  # SIZE_RESTORED
                    if self.is_maximized:
                        self.is_maximized = False
                        self.update_window_styles(8)

            elif msg.message == WM_NCHITTEST and not self.is_maximized:
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

                border_width = 8

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
        

        painter.setBrush(QColor(0, 0, 0))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)


        rect = self.rect()
        radius = 10
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)
        painter.drawPath(path)


        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOver)
        painter.setBrush(self.palette().window())
        painter.drawPath(path)

    def resizeEvent(self, event):
        super().resizeEvent(event)

