import asyncio
from qasync import QEventLoop, asyncSlot
from PyQt6.QtCore import Qt, QEvent, QObject
from PyQt6 import QtGui
from rainbotgui.gui.resources import resources
from rainbotgui.gui.widgets import Find_Widget
from rainbotgui.network.rainbotAPI_client import RainBot_Websocket
from rainbotgui.gui.main_window_ui import Ui_MainWindow



class Terminal_Page(QObject):
    def __init__(self, wbsocet_obj: RainBot_Websocket, ui: Ui_MainWindow, main_win):
        super().__init__()
        self.ui = ui
        self.used_commands = []
        self.websocket_client = wbsocet_obj
        self.ui.textBrowser.setFontPointSize(11)
        self.ui.textBrowser.setFontFamily("JetBrains Mono,Helvetica")
        self.ui.wbsocket_btn.setChecked(True)
        self.find_in_terminal = Find_Widget(parent=self.ui.buttons_in_terminal, 
            layout=self.ui.verticalLayout_6, 
            pos=3,
            browser=self.ui.textBrowser)
        self.ui.LineSenDCommand.installEventFilter(main_win)
        self.ui.LineSenDCommand.returnPressed.connect(self.sent_console_command)
        self.ui.send_btn.clicked.connect(self.sent_console_command)
        self.ui.button_find_in_console.clicked.connect(self.toggle_find)
        self.websocket_client.new_log_signal.connect(self.handle_new_log_message)

    def toggle_find(self):
        if self.find_in_terminal.find_label_2.isHidden():
            self.find_in_terminal.find_label_2.show()
        else:
            self.find_in_terminal.find_label_2.hide()

    def eventFilter(self, source, event):
        # Проверяем, что событие связано с нашим QLineEdit
        if source == self.ui.LineSenDCommand:
            # Проверяем, что событие — это нажатие клавиши
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Up:
                    # self.return_command_ILE(True)
                    return True
                elif event.key() == Qt.Key.Key_Down:
                    # self.return_command_ILE(False)
                    return True

        # Передаём остальные события родительскому классу
        return super().eventFilter(source, event)
    
    @asyncSlot()
    async def sent_console_command(self):
        text = self.ui.LineSenDCommand.text()
        if text != "":
            if text == "/disconnect":
                await self.websocket_client.disconnect()
                self.ui.textBrowser.append(text)
                self.ui.LineSenDCommand.clear()
                return
            
            await self.websocket_client.send_command(text)
            self.ui.textBrowser.append(text)
            self.used_commands.append(text)
            self.ui.LineSenDCommand.clear()

    def handle_new_log_message(self, log_message):
        """Метод для обработки нового сообщения."""
        self.ui.textBrowser.append(log_message)
        # Здесь вы можете обновить элементы интерфейса с полученным сообщением
        
        
        









class Websocket_Page(QObject):
    def __init__(self, wbsocet_obj: RainBot_Websocket, ui: Ui_MainWindow, main_win):
        super().__init__()
        self.ui = ui
        self.main_win = main_win
        self.websocket_client =  wbsocet_obj
        self.ui.label_6.setText("")
        self.ui.label_7.setText("")
        self.ui.wbsocket_btn.setChecked(True)
        self.ui.websck_status.hide()
        self.ui.conect_websc.clicked.connect(self.connectWS)
        self.websocket_client.connection_closed.connect(self.WS_on_diconnect)

    @asyncSlot()
    async def load_logs(self):
        logs = await self.websocket_client.get_logs()
        for log_str in logs:
            # Используем insertHtml, чтобы добавить логи с HTML-разметкой
            self.ui.textBrowser.append(log_str)

    @asyncSlot()
    async def WS_on_diconnect(self):
        self.ui.label_5.setPixmap(QtGui.QPixmap(":/MainIcons/icons/noconnected.png"))
        self.ui.conect_websc.setText("Connect")
        await self.websocket_client.disconnect()
        self.ui.label_6.setText("")
        self.ui.label_7.setText("")
        self.main_win.setDisabled_tabs(True)
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
            await asyncio.sleep(1)
            
            if self.websocket_client.isConnected():
                await self.load_logs()
                self.ui.label_5.setPixmap(QtGui.QPixmap(":/MainIcons/icons/connected.png"))
                self.ui.label_6.setText(f"<html><head/><body><p><span style=\" color:#89b086;\">Connected to:  </span><span style=\" font-weight:600; color:#69c5ca;\">{self.websocket_client.ip()}</span></p></body></html>")
                self.ui.label_7.setText(f"<html><head/><body><p><span style=\" color:#89b086;\">on port:  </span><span style=\" font-weight:600; color:#69c5ca;\">{self.websocket_client.port()}</span></p></body></html>")
                self.ui.label_6.show()
                self.ui.label_7.show()
                self.ui.conect_websc.setText("Connected")
                self.ui.conect_websc.setDisabled(False)
                self.main_win.setDisabled_tabs(False)
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
                self.main_win.setDisabled_tabs(True)
        else:
            self.ui.label_5.setPixmap(QtGui.QPixmap(":/MainIcons/icons/noconnected.png"))
            self.ui.conect_websc.setText("Connect")
            await self.websocket_client.disconnect()
            self.ui.label_6.setText("")
            self.ui.label_7.setText("")
            self.main_win.setDisabled_tabs(True)

            
