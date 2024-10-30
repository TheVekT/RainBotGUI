from PyQt6 import QtCore, QtGui, QtWidgets


class Find_Widget(object):
    def __init__(self, parent, layout, pos):
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
        self.upBotton = QtWidgets.QPushButton(parent=self.find_updown_btns_2)
        self.upBotton.setMinimumSize(QtCore.QSize(16, 16))
        self.upBotton.setMaximumSize(QtCore.QSize(16, 16))
        self.upBotton.setStyleSheet("QPushButton{\n"
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
        self.upBotton.setObjectName("upBotton")
        self.find_updown_btns.addWidget(self.upBotton)
        self.downBotton = QtWidgets.QPushButton(parent=self.find_updown_btns_2)
        self.downBotton.setMinimumSize(QtCore.QSize(16, 16))
        self.downBotton.setMaximumSize(QtCore.QSize(16, 16))
        self.downBotton.setStyleSheet("QPushButton{\n"
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
        self.downBotton.setObjectName("downBotton")
        self.find_updown_btns.addWidget(self.downBotton)
        self.find_label.addWidget(self.find_updown_btns_2)
        self.horizontalLayout.addWidget(self.find_label_2)
        layout.insertWidget(pos, self.find_label_2)
        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.Find_line.setPlaceholderText(_translate("Form", "Find text"))
        self.upBotton.setText(_translate("Form", "▲"))
        self.downBotton.setText(_translate("Form", "▼"))
