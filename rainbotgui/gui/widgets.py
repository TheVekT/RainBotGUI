from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QPropertyAnimation, QEasingCurve, QRectF, Qt
from PyQt6.QtGui import QTextDocument, QTextCursor, QKeyEvent
from PyQt6.QtWidgets import QTextBrowser, QLayout
from rainbotgui.gui.resources import resources


class Find_Widget(QObject):
    """
    Find_Widget is a custom widget for search functionality within a QTextBrowser.
    """
    searchRequested = pyqtSignal(str, bool)

    def __init__(self, parent, layout, pos: int, browser: QtWidgets.QTextBrowser):
        """
        Initializes the Find_Widget with the parent, layout, position, and browser.
        
        Args:
            parent (QWidget): The parent widget.
            layout (QLayout): The layout where this widget will be inserted.
            pos (int): The position in the layout where this widget will be inserted.
            browser (QTextBrowser): The QTextBrowser where the search will be performed.
        """
        super().__init__(parent)
        self.browser = browser
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.layout = layout
        self.parentWidget = parent
        self.find_label_2 = QtWidgets.QFrame(parent=self.parentWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.find_label_2.sizePolicy().hasHeightForWidth())
        self.find_label_2.setSizePolicy(sizePolicy)
        self.find_label_2.setMinimumSize(QtCore.QSize(180, 0))
        self.find_label_2.setMaximumSize(QtCore.QSize(300, 50))
        self.find_label_2.setStyleSheet("background-color: rgba(40, 40, 40, 100)")
        self.find_label_2.setObjectName("find_label_2")
        self.find_label = QtWidgets.QHBoxLayout(self.find_label_2)
        self.find_label.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
        self.find_label.setContentsMargins(0, 0, 0, 0)
        self.find_label.setSpacing(3)
        self.find_label.setObjectName("find_label")
        self.Find_line = QtWidgets.QLineEdit(parent=self.find_label_2)
        self.Find_line.setMinimumSize(QtCore.QSize(0, 50))
        self.Find_line.setMaximumSize(QtCore.QSize(16777215, 50))
        self.Find_line.setStyleSheet("selection-background-color:  #FFDAB9;\n"
                                     "selection-color: black;\n"
                                     "background-color: rgba(0,0,0,0);\n"
                                     "color: white;\n"
                                     "font-size: 12px;\n"
                                     "border-radius: 4px;\n"
                                     "padding-left: 5px;")
        self.Find_line.setObjectName("Find_line")
        self.find_label.addWidget(self.Find_line)
        self.find_updown_btns_2 = QtWidgets.QFrame(parent=self.find_label_2)
        self.find_updown_btns_2.setMaximumSize(QtCore.QSize(16777215, 50))
        self.find_updown_btns_2.setStyleSheet("background: rgba(0,0,0,0)")
        self.find_updown_btns_2.setObjectName("find_updown_btns_2")
        self.find_updown_btns = QtWidgets.QVBoxLayout(self.find_updown_btns_2)
        self.find_updown_btns.setContentsMargins(1, 1, 1, 1)
        self.find_updown_btns.setSpacing(1)
        self.find_updown_btns.setObjectName("find_updown_btns")
        self.upButton = QtWidgets.QPushButton(parent=self.find_updown_btns_2)
        self.upButton.setMinimumSize(QtCore.QSize(16, 16))
        self.upButton.setMaximumSize(QtCore.QSize(16, 16))
        self.upButton.setStyleSheet("QPushButton{\n"
                                    "    border-radius: 3px;\n"
                                    "    background-color: rgba(0,0,0,0);\n"
                                    "    color: white;\n"
                                    "    font-size: 13px;\n"
                                    "    border: none;\n"
                                    "}\n"
                                    "QPushButton:hover{\n"
                                    "    color: black;\n"
                                    "    background-color: #FFDAB9;\n"
                                    "}\n"
                                    "")
        self.upButton.setObjectName("upButton")
        self.find_updown_btns.addWidget(self.upButton)
        self.downButton = QtWidgets.QPushButton(parent=self.find_updown_btns_2)
        self.downButton.setMinimumSize(QtCore.QSize(16, 16))
        self.downButton.setMaximumSize(QtCore.QSize(16, 16))
        self.downButton.setStyleSheet("QPushButton{\n"
                                      "    border-radius: 3px;\n"
                                      "    background-color: rgba(0,0,0,0);\n"
                                      "    color: white;\n"
                                      "    font-size: 13px;\n"
                                      "    border: none;\n"
                                      "}\n"
                                      "QPushButton:hover{\n"
                                      "    color: black;\n"
                                      "    background-color: #FFDAB9;\n"
                                      "}\n"
                                      "")
        self.downButton.setObjectName("downButton")
        self.find_updown_btns.addWidget(self.downButton)
        self.find_label.addWidget(self.find_updown_btns_2)
        self.horizontalLayout.addWidget(self.find_label_2)
        self.layout.insertWidget(pos, self.find_label_2)
        self.retranslateUi()
        self.upButton.clicked.connect(self.onUpClicked)
        self.downButton.clicked.connect(self.onDownClicked)
        self.find_label_2.hide()
        self.searchRequested.connect(self.search_in_terminal)
    def retranslateUi(self):
        """
        Sets the text for the UI elements.
        """
        _translate = QtCore.QCoreApplication.translate
        self.Find_line.setPlaceholderText(_translate("Form", "Find text"))
        self.upButton.setText(_translate("Form", "▲"))
        self.downButton.setText(_translate("Form", "▼"))

    def onUpClicked(self):
        """
        Slot to handle the upward search button click.
        Emits the searchRequested signal with the search text and direction (False for upward).
        """
        text = self.Find_line.text()
        if text:
            self.Find_line.selectAll()
            self.searchRequested.emit(text, False)

    def onDownClicked(self):
        """
        Slot to handle the downward search button click.
        Emits the searchRequested signal with the search text and direction (True for downward).
        """
        text = self.Find_line.text()
        if text:
            self.Find_line.selectAll()
            self.searchRequested.emit(text, True)

    def search_in_terminal(self, text, forward):
        """
        Slot to perform the search in the QTextBrowser when the searchRequested signal is emitted.
        
        Args:
            text (str): The search text.
            forward (bool): The direction of the search (True for forward, False for backward).
        """
        self.findInTextBrowser(text, forward)

    def findInTextBrowser(self, text, forward=True):
        """
        Performs the search in the QTextBrowser.
        
        Args:
            text (str): The search text.
            forward (bool): The direction of the search (True for forward, False for backward).
        """
        cursor = self.browser.textCursor()
        options = QtGui.QTextDocument.FindFlag(0)
        if not forward:
            options |= QtGui.QTextDocument.FindFlag.FindBackward

        found = self.browser.find(text, options)
        if not found:
            if forward:
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.Start)
            else:
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)

            self.browser.setTextCursor(cursor)
            found = self.browser.find(text, options)
            if not found:
                self.Find_line.setText("No result.")
                self.Find_line.selectAll()





class Notify_widget(QtCore.QObject):
    def __init__(self, parent=None, show_time: int = 5):
        super().__init__(parent)
        self.show_time = show_time
        self.Notification = QtWidgets.QWidget(parent=parent)
        self.Notification.setGeometry(QtCore.QRect(20, 20, 400, 130))
        self.Notification.setMinimumSize(QtCore.QSize(350, 130))
        self.Notification.setMaximumSize(QtCore.QSize(450, 130))
        self.Notification.setSizeIncrement(QtCore.QSize(0, 0))
        self.Notification.setStyleSheet("QWidget{\n"
                                        "    background-color: rgba(0, 0, 0, 220);\n"
                                        "    font-family: \"JetBrains Mono\", Helvetica;\n"
                                        "    border-radius: 8px;\n"
                                        "\n"
                                        "}")
        self.Notification.setObjectName("Notification")

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.Notification)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lay1 = QtWidgets.QWidget(parent=self.Notification)
        self.lay1.setMaximumSize(QtCore.QSize(16777215, 40))
        self.lay1.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.lay1.setObjectName("lay1")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.lay1)
        self.horizontalLayout_2.setContentsMargins(0, 0, 5, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Info_place = QtWidgets.QWidget(parent=self.lay1)
        self.Info_place.setStyleSheet("QWidget{\n"
                                      "    background-color: rgba(0, 0, 0, 0);\n"
                                      "    border-radius: 0px;\n"
                                      "}")
        self.Info_place.setObjectName("Info_place")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.Info_place)
        self.verticalLayout.setContentsMargins(0, 8, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lay2 = QtWidgets.QFrame(parent=self.Info_place)
        self.lay2.setObjectName("lay2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.lay2)
        self.horizontalLayout.setContentsMargins(8, 0, 10, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.notify_type_icon = QtWidgets.QLabel(parent=self.lay2)
        self.notify_type_icon.setMinimumSize(QtCore.QSize(30, 30))
        self.notify_type_icon.setMaximumSize(QtCore.QSize(30, 30))
        self.notify_type_icon.setText("")
        self.notify_type_icon.setPixmap(QtGui.QPixmap(":/MainIcons/icons/success_l.png"))
        self.notify_type_icon.setScaledContents(True)
        self.notify_type_icon.setObjectName("notify_type_icon")
        self.horizontalLayout.addWidget(self.notify_type_icon)
        self.notify_title = QtWidgets.QLabel(parent=self.lay2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.notify_title.sizePolicy().hasHeightForWidth())
        self.notify_title.setSizePolicy(sizePolicy)
        self.notify_title.setMinimumSize(QtCore.QSize(100, 0))
        self.notify_title.setMaximumSize(QtCore.QSize(16777215, 30))

        self.notify_title.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.notify_title.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.notify_title.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.notify_title.setScaledContents(False)
        self.notify_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.notify_title.setWordWrap(False)
        self.notify_title.setObjectName("notify_title")
        self.horizontalLayout.addWidget(self.notify_title)
        self.verticalLayout.addWidget(self.lay2, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.horizontalLayout_2.addWidget(self.Info_place)
        self.close_btn = QtWidgets.QPushButton(parent=self.lay1)
        self.close_btn.setMinimumSize(QtCore.QSize(32, 32))
        self.close_btn.setMaximumSize(QtCore.QSize(32, 32))
        self.close_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.close_btn.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.close_btn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/MainIcons/icons/close_notify.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.close_btn.setIcon(icon)
        self.close_btn.setIconSize(QtCore.QSize(32, 32))
        self.close_btn.setObjectName("close_btn")
        self.horizontalLayout_2.addWidget(self.close_btn)
        self.verticalLayout_2.addWidget(self.lay1)
        self.notify_text1 = QtWidgets.QLabel(parent=self.Notification)
        self.notify_text1.setMinimumSize(QtCore.QSize(100, 40))
        self.notify_text1.setStyleSheet("color: rgb(255, 255, 255);\n"
                                        "background-color: rgba(0, 0, 0, 0);\n"
                                        "padding-left: 10px;\n"
                                        "padding-right: 10px;")
        self.notify_text1.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.notify_text1.setScaledContents(False)
        self.notify_text1.setWordWrap(True)
        self.notify_text1.setObjectName("notify_text1")
        self.verticalLayout_2.addWidget(self.notify_text1)
        self.notify_text2 = QtWidgets.QLabel(parent=self.Notification)
        self.notify_text2.setMinimumSize(QtCore.QSize(100, 0))
        self.notify_text2.setMaximumSize(QtCore.QSize(16777215, 25))
        self.notify_text2.setStyleSheet("color: rgba(235, 235, 235, 180);\n"
                                        "background-color: rgba(0, 0, 0, 0);\n"
                                        "padding-left: 10px;\n"
                                        "padding-right: 10px;\n"
                                        "font-size: 10px;")
        self.notify_text2.setText("")
        self.notify_text2.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.notify_text2.setScaledContents(False)
        self.notify_text2.setWordWrap(False)
        self.notify_text2.setObjectName("notify_text2")
        self.verticalLayout_2.addWidget(self.notify_text2)
        self.timeline = QtWidgets.QProgressBar(parent=self.Notification)
        self.timeline.setMaximumSize(QtCore.QSize(16777215, 5))
        self.timeline.setProperty("value", 100)
        self.timeline.setObjectName("timeline")
        self.verticalLayout_2.addWidget(self.timeline)
        self.animations = []
        self.retranslateUi()
    
        self.close_btn.clicked.connect(self.close)

        if parent is not None:
            parent.installEventFilter(self)
        
        self.Notification.show()
        self.update_position()
        self.close_timer(show_time=show_time)
        
    def close_timer(self, show_time):
        animation1 = QPropertyAnimation(self.timeline, b"value")
        animation1.setDuration(show_time * 1000 - 200)
        animation1.setStartValue(100)
        animation1.setEndValue(0)
        animation1.setEasingCurve(QEasingCurve.Type.Linear)
        animation1.finished.connect(self.close)
        
        self.animations.append(animation1)
        animation1.start()

    def retranslateUi(self):
        self.notify_title.setText("Success")
        self.notify_text1.setText("This is small description of notify widget to test layouts")

    def close(self):
        def _close():
            self.Notification.close()
            self.Notification.deleteLater()
            self.deleteLater()
        animation2 = QPropertyAnimation(self.Notification, b"geometry")
        animation2.setDuration(120)
        animation2.setEasingCurve(QEasingCurve.Type.Linear)
        animation2.setStartValue(self.Notification.geometry())
        animation2.setEndValue(QtCore.QRect(self.Notification.x() + self.Notification.width(), self.Notification.y(), 0, self.Notification.height()))
        
        self.Notification.setMinimumWidth(0)
        self.notify_text1.setWordWrap(False)
        
        animation2.finished.connect(_close)
        self.animations.append(animation2)
        animation2.start()
        
        


    def set_notify_title(self, text):
        self.notify_title.setText(text)

    def set_notify_icon(self, icon_name):
        self.notify_type_icon.setPixmap(QtGui.QPixmap(f":/MainIcons/icons/{icon_name}"))

    def set_notify_theme_color(self, color):
        self.timeline.setStyleSheet("QProgressBar {\n"
                                    "    background: #000000;     \n"
                                    "    text-align: center;      \n"
                                    "    color: transparent;       \n"
                                    "    border-radius: 0px;\n"
                                    "    border-bottom-right-radius: 3px;\n"
                                    "    border-bottom-left-radius: 3px;\n"
                                    "}\n"
                                    "\n"
                                    "QProgressBar::chunk {\n"
                                    f"    background-color: {color}; \n"
                                    "    width: 1px;          \n"
                                    "    margin: 0px;              \n"
                                    "}")
        self.notify_title.setStyleSheet(f"color: {color};\n"
                                        "font-weight: bold;\n"
                                        "font-size: 13px;\n"
                                        "padding-left: 10px;\n"
                                        "padding-right: 10px;")

    def update_position(self):
        if self.parent():
            parent_w = self.parent().width()
            parent_h = self.parent().height()
            w = self.Notification.width()
            h = self.Notification.height()
            self.Notification.move(parent_w - w - 10, parent_h - h - 10)

    def eventFilter(self, watched, event):
        if watched == self.parent() and event.type() == QtCore.QEvent.Type.Resize:
            self.update_position()
        return super().eventFilter(watched, event)






class Success_Notify(Notify_widget):
    def __init__(self, title: str, text1: str, text2: str = '', show_time: int = 5, parent = None):
        super().__init__(parent, show_time)
        self.set_notify_theme_color("#75FB4C")
        self.set_notify_icon('success_l.png')
        self.set_notify_title(title)
        self.notify_text1.setText(text1)
        self.notify_text2.setText(text2)

        
class Info_Notify(Notify_widget):
    def __init__(self, title: str, text1: str, text2: str = '', show_time: int = 5, parent = None):
        super().__init__(parent, show_time)
        self.set_notify_theme_color("#FFDAB9")
        self.set_notify_icon('info_w.png')
        self.set_notify_title(title)
        self.notify_text1.setText(text1)
        self.notify_text2.setText(text2)

        
class Error_Notify(Notify_widget):
    def __init__(self, title: str, text1: str, text2: str = '', show_time: int = 5, parent = None):
        super().__init__(parent, show_time)
        self.set_notify_theme_color("#BB271A")
        self.set_notify_icon('error_r.png')
        self.set_notify_title(title)
        self.notify_text1.setText(text1)
        self.notify_text2.setText(text2)
