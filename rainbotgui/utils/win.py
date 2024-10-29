from ctypes import windll, wintypes
import ctypes
from ctypes import windll, wintypes, byref, Structure, sizeof, POINTER, c_int
from ctypes.wintypes import HWND, HRGN, RECT

# Windows message constants
WM_NCLBUTTONDOWN = 0x00A1
HTCAPTION = 0x0002
WM_NCCALCSIZE = 0x0083
WM_NCHITTEST = 0x0084
WM_SYSCOMMAND = 0x0112
WM_SIZE = 0x0005
SC_MAXIMIZE = 0xF030 
SC_MINIMIZE = 0xF020
SC_CLOSE = 0xF060
SC_RESTORE = 0xF120
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_MAXIMIZEBOX = 0x00010000
WS_MINIMIZEBOX = 0x00020000
SWP_FRAMECHANGED = 0x0020
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_NOOWNERZORDER = 0x0200
GWL_STYLE = -16
GWL_EXSTYLE = -20
HTCLIENT = 1
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17


class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long)]

class MONITORINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_long),
                ('rcMonitor', RECT),
                ('rcWork', RECT),
                ('dwFlags', ctypes.c_long)]

    

    
# Determine if the system is 64-bit
is_64bits = ctypes.sizeof(ctypes.c_void_p) == 8

# Define LONG_PTR and ULONG_PTR based on the architecture
if is_64bits:
    LONG_PTR = ctypes.c_int64
    ULONG_PTR = ctypes.c_uint64
else:
    LONG_PTR = ctypes.c_long
    ULONG_PTR = ctypes.c_ulong

# Define SetWindowLongPtr and GetWindowLongPtr
SetWindowLongPtr = ctypes.windll.user32.SetWindowLongPtrW
GetWindowLongPtr = ctypes.windll.user32.GetWindowLongPtrW
SetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int, LONG_PTR]
SetWindowLongPtr.restype = LONG_PTR
GetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int]
GetWindowLongPtr.restype = LONG_PTR