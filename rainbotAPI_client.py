import asyncio
import websockets
import json
from urllib.parse import urlparse
from PyQt6.QtCore import QObject, pyqtSignal
class RainBot_Websocket(QObject):
    new_log_signal = pyqtSignal(str)
    connection_closed = pyqtSignal()
    def __init__(self, uri):
        super().__init__()  # Важно вызвать родительский конструктор
        self.uri = uri
        self.websocket = None
        self.logs_queue = asyncio.Queue()  # Очередь для хранения логов
        
    def ip(self):
        """Возвращает IP-адрес сервера, к которому подключен WebSocket."""
        parsed_url = urlparse(self.uri)
        return parsed_url.hostname

    def port(self):
        """Возвращает порт сервера, к которому подключен WebSocket."""
        parsed_url = urlparse(self.uri)
        return parsed_url.port

    async def connect(self):
        """Подключение к WebSocket-серверу."""
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"Подключено к серверу: {self.uri}")
            # Запуск фоновой задачи для получения сообщений
            asyncio.create_task(self.receive_messages())
        except Exception as e:
            print(f"Ошибка при подключении: {e}")

    async def send_command(self, command):
        """Отправка команды с одним аргументом (строкой) на сервер."""
        if self.websocket:
            try:
                await self.websocket.send(command)
                print(f"Отправлено сообщение: {command}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")
        else:
            print("Нет активного соединения с сервером.")

    async def disconnect(self):
        """Отключение от WebSocket-сервера."""
        if self.websocket:
            try:
                await self.websocket.close()
                print("Соединение закрыто.")
            except Exception as e:
                print(f"Ошибка при закрытии соединения: {e}")
        else:
            print("Нет активного соединения для закрытия.")

    def isConnected(self):
        """Проверка подключения к серверу WebSocket."""
        return self.websocket is not None and self.websocket.open

    async def receive_messages(self):
        """Фоновая задача для получения всех сообщений с сервера."""
        try:
            while True:
                message = await self.websocket.recv()
                # Пытаемся распарсить сообщение как JSON
                try:
                    data = json.loads(message)
                    if 'type' in data and data['type'] == 'logs':
                        await self.logs_queue.put(data['logs'])  # Кладем логи в очередь
                    elif 'type' in data and data['type'] == 'new_log_message':
                        self.new_log_signal.emit(data['logs'])
                    else:
                        print(f"Получено другое сообщение: {data}")
                except json.JSONDecodeError:
                    print(f"Ошибка при разборе сообщения: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("Соединение с сервером закрыто.")
            self.connection_closed.emit()
        except Exception as e:
            print(f"Ошибка при получении сообщений: {e}")

    async def get_logs(self):
        """Запрос на получение логов."""
        # Отправляем команду для получения логов
        await self.send_command("@get_logs")
        # Ожидаем получения логов из очереди
        logs = await self.logs_queue.get()
        return logs