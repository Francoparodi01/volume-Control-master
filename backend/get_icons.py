import ctypes
import os
from PIL import Image
from ctypes import wintypes
import win32gui
import win32ui
import win32con

def get_window_icon(hwnd):
    """Obtiene el icono de la ventana dada por su identificador de ventana (hwnd)"""
    hicon = ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_GETICON, win32con.ICON_SMALL, 0)
    if hicon == 0:
        hicon = ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_GETICON, win32con.ICON_BIG, 0)
    if hicon == 0:
        hicon = ctypes.windll.user32.GetClassLongPtrW(hwnd, win32con.GCL_HICON)

    if hicon == 0:
        return None

    icon_info = win32gui.GetIconInfo(hicon)
    width, height = win32con.SM_CXSMICON, win32con.SM_CYSMICON

    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, width, height)
    hdc = hdc.CreateCompatibleDC()

    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0, 0), hicon)

    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)

    im = Image.frombuffer('RGBA', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRA', 0, 1)
    return im


def save_icon(im, path):
    """Guarda la imagen del icono en el sistema de archivos."""
    try:
        im.save(path)
        print(f"Icono guardado en {path}")
    except Exception as e:
        print(f"Error al guardar el icono: {e}")

def enum_windows_callback(hwnd, windows):
    """Callback para listar todas las ventanas abiertas."""
    if win32gui.IsWindowVisible(hwnd):
        length = win32gui.GetWindowTextLength(hwnd)
        window_name = win32gui.GetWindowText(hwnd)
        if length > 0 and window_name:
            icon = get_window_icon(hwnd)
            if icon:
                windows[window_name] = icon

def get_all_icons():
    """Obtiene todos los iconos de las ventanas abiertas."""
    windows = {}
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows


if __name__ == "__main__":
    icons = get_all_icons()
    if not os.path.exists('icons'):
        os.makedirs('icons')

    for name, icon in icons.items():
        icon_path = os.path.join('icons', f"{name}.png")
        save_icon(icon, icon_path)
