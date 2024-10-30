from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

class Find_Widget(QObject):
    searchRequested = pyqtSignal(str, bool)
    def __init__(self, parent, layout, pos):
        super().__init__(parent)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.find_label_2 = QtWidgets.QFrame(parent=parent)
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
        self.upButton.setObjectName("upBotton")
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
        self.downButton.setObjectName("downBotton")
        self.find_updown_btns.addWidget(self.downButton)
        self.find_label.addWidget(self.find_updown_btns_2)
        self.horizontalLayout.addWidget(self.find_label_2)
        layout.insertWidget(pos, self.find_label_2)
        self.retranslateUi()
        self.upButton.clicked.connect(self.onUpClicked)
        self.downButton.clicked.connect(self.onDownClicked)
        self.find_label_2.hide()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.Find_line.setPlaceholderText(_translate("Form", "Find text"))
        self.upButton.setText(_translate("Form", "▲"))
        self.downButton.setText(_translate("Form", "▼"))

    def onUpClicked(self):
        text = self.Find_line.text()
        if text:
            self.Find_line.selectAll()
            self.searchRequested.emit(text, False)

    def onDownClicked(self):
        text = self.Find_line.text()
        if text:
            self.Find_line.selectAll()
            self.searchRequested.emit(text, True)