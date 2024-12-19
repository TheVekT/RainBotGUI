import asyncio
from qasync import QEventLoop, asyncSlot
from PyQt6.QtCore import Qt, QEvent, QObject
from PyQt6 import QtGui, QtWidgets
from rainbotgui.gui.resources import resources
from rainbotgui.network.rainbotAPI_client import RainBot_Websocket
from rainbotgui.gui.main_window_ui import Ui_MainWindow
from rainbotgui.gui.widgets import Info_Notify, Success_Notify, Error_Notify, logfile_widget, Find_Widget

class Terminal_Page(QObject):
    def __init__(self, wbsocet_obj: RainBot_Websocket, ui: Ui_MainWindow, main_win):
        super().__init__()
        self.ui = ui
        self.used_commands = []
        self.unique_commands = []  # Список уникальных подряд команд для переключения
        self.command_index = -1  # Индекс текущей команды в unique_commands
        self.websocket_client = wbsocet_obj
        self.ui.textBrowser.setFontPointSize(11)
        self.ui.textBrowser.setFontFamily("JetBrains Mono,Helvetica")
        self.find_in_terminal = Find_Widget(
            parent=self.ui.buttons_in_terminal,
            layout=self.ui.verticalLayout_6,
            pos=3,
            browser=self.ui.textBrowser
        )
        self.ui.LineSenDCommand.installEventFilter(self)
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
        if source == self.ui.LineSenDCommand and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                self.navigate_command_history(up=True)
                return True
            elif event.key() == Qt.Key.Key_Down:
                self.navigate_command_history(up=False)
                return True

        return super().eventFilter(source, event)

    def update_unique_commands(self):
        """Обновление списка уникальных подряд команд."""
        self.unique_commands = []
        prev_command = None
        for command in self.used_commands:
            if command != prev_command:
                self.unique_commands.append(command)
                prev_command = command

    def navigate_command_history(self, up: bool):
        """Навигация по истории уникальных команд."""
        if not self.unique_commands:
            return

        if up:
            self.command_index = max(0, self.command_index - 1)
            command = self.unique_commands[self.command_index]
            self.ui.LineSenDCommand.setText(command)
        else:
            if self.command_index < len(self.unique_commands) - 1:
                self.command_index += 1
                command = self.unique_commands[self.command_index]
                self.ui.LineSenDCommand.setText(command)
            else:
                self.command_index = len(self.unique_commands)  # Выходим за пределы истории
                self.ui.LineSenDCommand.clear()

        self.ui.LineSenDCommand.setCursorPosition(len(self.ui.LineSenDCommand.text()))

    @asyncSlot()
    async def sent_console_command(self):
        text = self.ui.LineSenDCommand.text()
        if text != "" and text.startswith("/"):
            if text == "/disconnect":
                await self.websocket_client.disconnect()
                self.ui.textBrowser.append(text)
                self.ui.LineSenDCommand.clear()
                return

            await self.websocket_client.send_command(text)
            self.ui.textBrowser.append(f'>>> {text}')
            self.used_commands.append(text)
            self.update_unique_commands()
            self.command_index = len(self.unique_commands)  # Сбрасываем индекс на конец списка
            self.ui.LineSenDCommand.clear()
        elif text != "" and not text.startswith("/"):
            self.ui.textBrowser.append("[Terminal] Commands must start with '/'")
            self.ui.LineSenDCommand.clear()
            
    def handle_new_log_message(self, log_message):
        """Метод для обработки нового сообщения."""
        self.ui.textBrowser.append(log_message)

        
        









class Websocket_Page(QObject):
    def __init__(self, wbsocet_obj: RainBot_Websocket, ui: Ui_MainWindow, main_win):
        super().__init__()
        self.ui = ui
        self.main_win = main_win
        self.websocket_client =  wbsocet_obj
        self.ui.label_6.setText("")
        self.ui.label_7.setText("")
        self.ui.wbsocket_btn.setChecked(True)
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
        Info_Notify("Disconnected", "Lost connection with websocket server", parent=self.main_win)

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
                Success_Notify("Success connected", "Successfully connected to websocket server", f"Connect on {self.websocket_client.ip()}:{self.websocket_client.port()}", parent=self.main_win)
                await self.load_logs()
                self.ui.label_5.setPixmap(QtGui.QPixmap(":/MainIcons/icons/connected.png"))
                self.ui.label_6.setText(f"<html><head/><body><p><span style=\" color:#89b086;\">Connected to:  </span><span style=\" font-weight:600; color:#69c5ca;\">{self.websocket_client.ip()}</span></p></body></html>")
                self.ui.label_7.setText(f"<html><head/><body><p><span style=\" color:#89b086;\">on port:  </span><span style=\" font-weight:600; color:#69c5ca;\">{self.websocket_client.port()}</span></p></body></html>")
                self.ui.label_6.show()
                self.ui.label_7.show()
                self.ui.conect_websc.setText("Connected")
                self.ui.conect_websc.setDisabled(False)
                self.main_win.setDisabled_tabs(False)
            else:
                Error_Notify("Сonnection failed", "Cannot connect to websocket server", f"try was on {self.websocket_client.ip()}:{self.websocket_client.port()}", parent=self.main_win)
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









class logs_Page(QObject):
    def __init__(self, wbsocet_obj: RainBot_Websocket, ui: Ui_MainWindow, main_win):
        super().__init__()
        self.ui = ui
        self.main_win = main_win
        self.websocket_client = wbsocet_obj
        self.ui.logBrowser.setFocus()
        self.find_in_logfile = Find_Widget(self.ui.logs_frame2, self.ui.horizontalLayout_14, 0, self.ui.logBrowser)
        self.find_in_logfile.find_label_2.show()
        self.find_in_logfile.find_label_2.setStyleSheet("background-color: rgba(10, 10, 10, 255)")
        self.websocket_client.connection_opened.connect(self.get_acrchived_logs)
        self.ui.logs_level_chooser.currentIndexChanged.connect(self.create_logfile_widgets)
        self.ui.logBrowser.setFontPointSize(11)
        self.ui.logBrowser.setFontFamily("JetBrains Mono,Helvetica")
        self.scrollButtons = QtWidgets.QButtonGroup(self.ui.scrollAreaWidgetContents_2)
        
        
    def create_logfile_widgets(self):
        self.ui.logBrowser.clear()
        log_level = self.ui.logs_level_chooser.currentText()
        for el in self.ui.scrollAreaWidgetContents_2.children():
            if isinstance(el, logfile_widget):
                el.deleteLater()
        if log_level == "Select log level" or log_level == "":
            return
        for log in self.avaliable_logs['data'][log_level][::-1]:
            log_widget = logfile_widget(log['filename'], log['date'], log['folder'], 
                                        parent=self.ui.scrollAreaWidgetContents_2, 
                                        websocket_client=self.websocket_client, 
                                        ui=self.ui, 
                                        layout=self.ui.verticalLayout_17)
            self.scrollButtons.addButton(log_widget.log_btn)

        
    @asyncSlot()
    async def get_acrchived_logs(self):
        await asyncio.sleep(1)
        self.avaliable_logs = await self.websocket_client.get_archived_logs(7)
        self.ui.logs_level_chooser.removeItem(0)
        self.ui.logs_level_chooser.addItem("Select log level")
        for level in self.avaliable_logs['data']:
            self.ui.logs_level_chooser.addItem(level)

                
            
            