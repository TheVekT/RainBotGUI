import asyncio
import time
from PyQt6.QtCore import QThread, pyqtSignal

class DiscordMemberWorker(QThread):
    # Сигнал передает словарь с данными участника
    member_data_ready = pyqtSignal(dict)
    
    def __init__(self, websocket_client, main_loop, parent=None):
        super().__init__(parent)
        self.websocket_client = websocket_client
        self.main_loop = main_loop  # Главный event loop (UI)
        
    def run(self):
        try:
            # Вызываем get_discord_members через главный event loop
            future = asyncio.run_coroutine_threadsafe(
                self.websocket_client.get_discord_members(), self.main_loop
            )
            # Ждем результат (с таймаутом, например, 10 секунд)
            data = future.result(timeout=10)
        except Exception as e:
            print("Ошибка получения данных:", e)
            return
        
        # Эмитируем сигнал для каждого участника
        for member_id, member_data in data.items():
            self.member_data_ready.emit({
                'member_id': member_id,
                'nickname': member_data['nickname'],
                'avatar_url': member_data['avatar_url'],
                'status': member_data['status']
            })
            # Используем time.sleep вместо self.msleep чтобы не запускать QThread-таймеры
            time.sleep(0.03)