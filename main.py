import sys
import asyncio

from qasync import QEventLoop
from rainbotgui.gui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication



if __name__ == "__main__":
    app = QApplication(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()
    with loop:
        sys.exit(loop.run_forever())