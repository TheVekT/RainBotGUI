import sys
import json
import shutil
import time
from datetime import datetime, timedelta
import numpy as np
import wave
import os
from datetime import datetime
from designe import Ui_MainWindow 
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import QIODevice, QBuffer, QTimer, Qt, QPropertyAnimation, QRect, QEasingCurve, QRectF, pyqtSlot
from PyQt6.QtMultimedia import QMediaDevices, QAudioSource, QAudioFormat
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox,QPushButton, QWidget, QSlider, QLabel, QComboBox, QGraphicsOpacityEffect, QFileDialog
from PyQt6.QtGui import QIcon, QPainter, QColor, QPainterPath

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        # Переменные для хранения состояния перетаскивания окна
        
        self.is_dragging = False
        self.mouse_start_position = None
        self.window_start_position = None
        # Подключаем mouse-ивенты для метки
        self.ui.headerBar.mousePressEvent = self.label_mouse_press_event
        self.ui.headerBar.mouseMoveEvent = self.label_mouse_move_event
        self.ui.headerBar.mouseReleaseEvent = self.label_mouse_release_event
        self.left_menu_minimized = False

        self.ui.menuButton.clicked.connect(self.left_menu_minimize)
        self.ui.minimize_btn.clicked.connect(self.minimize_window)
        self.ui.close_btn.clicked.connect(self.close_window)
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
        # Пример добавления кнопок для переключения табов
        self.ui.terminal_btn.clicked.connect(lambda: self.switch_tab(0))
        self.ui.stats_btn.clicked.connect(lambda: self.switch_tab(1))
        self.ui.logs_btn.clicked.connect(lambda: self.switch_tab(2))
        self.ui.Settings_btn.clicked.connect(lambda: self.switch_tab(4))
        self.ui.wbsocket_btn.clicked.connect(lambda: self.switch_tab(3))
        self.animations = []
        self.switch_tab(3, 500)
        self.ui.wbsocket_btn.setChecked(True)
        
        self.minimized_buttons_texts_dict = {}
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
    
    def label_mouse_press_event(self, event):
        """Запоминаем начальные позиции при нажатии на метку."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.mouse_start_position = event.globalPosition().toPoint()
            self.window_start_position = self.frameGeometry().topLeft()

    def label_mouse_move_event(self, event):
        """Перемещаем окно при перемещении мыши."""
        if self.is_dragging:
            delta = event.globalPosition().toPoint() - self.mouse_start_position
            self.move(self.window_start_position + delta)

    def label_mouse_release_event(self, event):
        """Прекращаем перетаскивание при отпускании кнопки."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

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
    def minimize_window(self):
        self.hide()  # Скрываем текущее окно
    def close_window(self):
        self.close()
    def is_on_edge(self, pos):
        """Проверяем, находимся ли на краю окна для изменения размера."""
        margin = 10  # Задаем область чувствительности к краю
        rect = self.rect()
        return pos.x() >= rect.width() - margin or pos.y() >= rect.height() - margin

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
