from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QTextDocument, QTextCursor, QKeyEvent
from PyQt6.QtWidgets import QTextBrowser, QLayout


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
