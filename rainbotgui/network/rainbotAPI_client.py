import asyncio
import websockets
import json
from urllib.parse import urlparse
from PyQt6.QtCore import QObject, pyqtSignal

class RainBot_Websocket(QObject):
    new_log_signal = pyqtSignal(str)
    connection_closed = pyqtSignal()

    def __init__(self, uri=None):
        super().__init__()
        self.uri = uri
        self.websocket = None
        self.logs_queue = asyncio.Queue()

    def ip(self):
        """Returns the IP address of the connected server."""
        parsed_url = urlparse(self.uri)
        return parsed_url.hostname

    def port(self):
        """Returns the port of the connected server."""
        parsed_url = urlparse(self.uri)
        return parsed_url.port

    async def connect(self, uri=None, connection_type="gui_client"):
        """Connects to the WebSocket server and sends the connection type."""
        if uri:
            self.uri = uri
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"Connected to server: {self.uri}")
            # Send initial connection type message
            initial_message = {
                "connection-type": connection_type
            }
            await self.websocket.send(json.dumps(initial_message))
            # Start background task to receive messages
            asyncio.create_task(self.receive_messages())
        except Exception as e:
            print(f"Connection error: {e}")

    async def send_command(self, command):
        """Sends a command to the server."""
        if self.websocket:
            try:
                await self.websocket.send(command)
                print(f"Sent message: {command}")
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
        """Checks if the client is connected to the server."""
        return self.websocket is not None and self.websocket.open

    async def receive_messages(self):
        """Background task to receive messages from the server."""
        try:
            while True:
                message = await self.websocket.recv()
                # Try to parse the message as JSON
                try:
                    data = json.loads(message)
                    if 'type' in data and data['type'] == 'logs':
                        match data['type']:
                            case 'logs':
                                await self.logs_queue.put(data['message'])
                            case 'new_log_message':
                                self.new_log_signal.emit(data['message'])
                    else:
                        print(f"Received other message: {data}")
                except json.JSONDecodeError:
                    print(f"Error parsing message: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection to server closed.")
            self.connection_closed.emit()
        except Exception as e:
            print(f"Error receiving messages: {e}")

    async def get_logs(self):
        """Requests logs from the server."""
        await self.send_command("@get_logs")
        logs = await self.logs_queue.get()
        return logs
