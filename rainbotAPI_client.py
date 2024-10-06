import asyncio
import websockets
from urllib.parse import urlparse
class RainBot_Websocket:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
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
        except Exception as e:
            print(f"Ошибка при подключении: {e}")

    async def send_command(self, str):
        """Отправка команды с одним аргументом (строкой) на сервер."""
        if self.websocket:
            try:
                message = str
                await self.websocket.send(message)
                print(f"Отправлено сообщение: {message}")
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