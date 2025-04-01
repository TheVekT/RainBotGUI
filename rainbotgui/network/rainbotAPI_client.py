import asyncio
import websockets
import json
from urllib.parse import urlparse
from PyQt6.QtCore import QObject, pyqtSignal

class RainBot_Websocket(QObject):
    new_log_signal = pyqtSignal(str)
    connection_opened = pyqtSignal()
    connection_closed = pyqtSignal()

    def __init__(self, uri=None):
        super().__init__()
        self.uri = uri
        self.websocket = None

        self.logs_queue = asyncio.Queue()
   
        self.archived_logs_queue = asyncio.Queue()

        self.log_file_content_queue = asyncio.Queue()
        self.discord_members_queue = asyncio.Queue()
        self.registered_functions: dict = {}
        self.discord_member_stat_queue = asyncio.Queue()

    def ip(self):
        """Returns the IP address of the connected server."""
        parsed_url = urlparse(self.uri)
        return parsed_url.hostname

    def port(self):
        """Returns the port of the connected server."""
        parsed_url = urlparse(self.uri)
        return parsed_url.port

    async def connect(self, uri=None, connection_type="gui_client"):
        if uri:
            self.uri = uri
        try:
            self.websocket = await websockets.connect(self.uri, max_size=16777216)
            print(f"Connected to server: {self.uri}")
            self.connection_opened.emit()
            # Отправляем начальное сообщение в JSON-формате
            initial_message = {
                "request": "INIT_CONNECTION",
                "arguments": {
                    "connection_type": connection_type
                }
            }
            await self.websocket.send(json.dumps(initial_message))
            asyncio.create_task(self.receive_messages())
        except Exception as e:
            print(f"Connection error: {e}")

    async def send_command(self, command_json: str):
        if self.websocket:
            try:
                await self.websocket.send(command_json)
                print(f"Sent message: {command_json}")
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("No active connection to the server.")

    async def disconnect(self):
        """Disconnects from the WebSocket server."""
        if self.websocket:
            try:
                await self.websocket.close()
                print("Connection closed.")
            except Exception as e:
                print(f"Error closing connection: {e}")
        else:
            print("No active connection to close.")

    def isConnected(self):
        from websockets.protocol import State
        """Checks if the client is connected to the server."""
        return self.websocket is not None and self.websocket.state == State.OPEN

    async def receive_messages(self):
        """Background task to receive messages from the server."""
        try:
            while True:
                message = await self.websocket.recv()
                # Try to parse the message as JSON
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    if msg_type:
                        match msg_type:
                            case 'logs':
                                await self.logs_queue.put(data['message'])

                            case'new_log_message':
                                # Новый лог-сообщение
                                self.new_log_signal.emit(data['message'])

                            case 'archived_logs':
                                await self.archived_logs_queue.put(data)

                            case 'log_file_content':
                                # Содержимое конкретного лог-файла
                                # data['content'] содержит текст файла
                                await self.log_file_content_queue.put(data['content'])
                                
                            case 'registered_functions':
                                self.registered_functions['registered_functions'] = data['data']
                            case 'response':
                                # Ответ на команду
                                # Здесь можно обработать ответ, если нужно
                                response = data.get('message', 'No message')
                                print(f"Response: {response}")
                            case 'error':
                                # Сообщение об ошибке
                                error_message = data.get('message', 'Unknown error')
                                print(f"Server error: {error_message}")
                                # Можно выбросить исключение или обработать иначе
                                # Здесь для простоты - бросим исключение:
                                raise Exception(f"Server error: {error_message}")
                            case 'discord_members':
                                # Список участников Discord
                                members = data.get('message', [])
                                await self.discord_members_queue.put(members)
                            case 'discord_member_stat':
                                # Статистика участника Discord
                                member_stat = data.get('message', {})
                                await self.discord_member_stat_queue.put(member_stat)
                    else:
                        # Неизвестное или другое сообщение
                        print(f"Received other message: {data}")

                except json.JSONDecodeError:
                    print(f"Error parsing message: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection to server closed.")
            self.connection_closed.emit()
        except Exception as e:
            print(f"Error receiving messages: {e}")
    async def slash_command(self, command: str):
        payload = {"request": "SLASH_COMMAND", "arguments": {"command": command}}
        await self.send_command(json.dumps(payload))
    
    async def set_registered_functions(self):
        payload = {"request": "REGISTERED_FUNCTIONS", "arguments": {}}
        await self.send_command(json.dumps(payload))

    async def get_logs(self):
        payload = {"request": "GET_LOGS", "arguments": {}}
        await self.send_command(json.dumps(payload))
        logs = await self.logs_queue.get()
        return logs

    async def get_archived_logs(self, days: int):
        payload = {
            "request": "GET_ARCHIVED_LOGS",
            "arguments": {"days": days}
        }
        await self.send_command(json.dumps(payload))
        archived_logs = await self.archived_logs_queue.get()
        return archived_logs

    async def get_log_file_content(self, folder: str, filename: str):
        payload = {
            "request": "GET_LOG_FILE",
            "arguments": {"folder": folder, "filename": filename}
        }
        await self.send_command(json.dumps(payload))
        content = await self.log_file_content_queue.get()
        print(f"Received log file content: {content[:50]}...")
        return content
    
    async def get_discord_members(self):
        payload = {
            "request": "GET_DISCORD_MEMBERS",
            "arguments": {}
        }
        await self.send_command(json.dumps(payload))
        data = await self.discord_members_queue.get()
        return data
    
    async def get_discord_member_stat(self, member_id: int, date: str):
        """Получить статистику участника Discord за определенную дату format: YYYY.MM.DD ."""
        payload = {
            "request": "GET_DISCORD_MEMBER_STAT",
            "arguments": {"member_id": member_id, "date": date}
        }
        await self.send_command(json.dumps(payload))
        data = await self.discord_member_stat_queue.get()
        return data