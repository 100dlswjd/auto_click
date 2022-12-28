import sys
import win32con
import ctypes
import mouse
import os

from ctypes import wintypes, windll
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtGui import QCloseEvent, QPixmap
from ui.main_form import Ui_MainWindow

from threading import Thread, Event

WM_HOTKEY = 0x00312


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Mainwindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Mainwindow, self).__init__()
        self.setupUi(self)
        myappid = 'auto click' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.start_flag = False

        self.pushButton_start.clicked.connect(self.btn_start_handler)

        user32 = windll.user32
        self.RegisterHotKey = user32["RegisterHotKey"]
        self.RegisterHotKey.argtypes = (wintypes.HWND, wintypes.INT, wintypes.UINT, wintypes.UINT)
        self.RegisterHotKey.restype = wintypes.BOOL

        self.UnregisterHotKey = user32["UnregisterHotKey"]
        self.UnregisterHotKey.argtypes = (wintypes.HWND, wintypes.INT)
        self.UnregisterHotKey.restype = wintypes.BOOL

        self.RegisterHotKey(self.winId(), 1, 0, win32con.VK_F8)

        self.work_thread = Thread(target= self.work_proc)
        self.program_event = Event()
        self.exit_event = Event()
        self.exit_event.set()
        self.work_thread.start()

    def work_proc(self):
        while self.program_event.is_set() == False:
            while self.exit_event.is_set() == False:
                mouse.click()
                self.exit_event.wait(1/self.spinBox_count.value())
            self.program_event.wait(0.5)

    def btn_start_handler(self):
        self.start_flag = not self.start_flag
        if self.start_flag:
            self.pushButton_start.setText("중지 F8")
            self.spinBox_count.setEnabled(False)
            self.exit_event.clear()
        else:
            self.pushButton_start.setText("시작 F8")
            self.spinBox_count.setEnabled(True)
            self.exit_event.set()

    def hotkey_proc(self, wParam, lParam):
        if wParam == 1:
            self.pushButton_start.click()

    def nativeEvent(self, eventType, message):
        if eventType == "windows_generic_MSG":
            msg = wintypes.MSG.from_address(message.__int__())
            if msg.message == WM_HOTKEY:
                self.hotkey_proc(msg.wParam, msg.lParam)

        return super().nativeEvent(eventType, message)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.program_event.set()
        self.exit_event.set()
        return super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Mainwindow()
    window.show()
    app.setWindowIcon(QPixmap(resource_path("src/icon/cursor.ico")))    
    app.setStyle("Fusion")
    app.exec()