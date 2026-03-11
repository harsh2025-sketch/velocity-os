import ctypes

FindWindowW = ctypes.windll.user32.FindWindowW
EnumWindows = ctypes.windll.user32.EnumWindows
GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW
GetWindowTextW = ctypes.windll.user32.GetWindowTextW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
ShowWindow = ctypes.windll.user32.ShowWindow
SW_SHOW = 5


def list_visible_windows():
    titles = []
    def callback(hwnd, lparam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value
                if title:
                    titles.append((hwnd, title))
        return True
    CMPFUNC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    EnumWindows(CMPFUNC(callback), 0)
    return titles


def bring_to_front_by_substring(substring: str) -> bool:
    """Bring a window to front by partial title match."""
    substring = (substring or "").strip().lower()
    if not substring:
        return False
    for hwnd, title in list_visible_windows():
        if substring in title.lower():
            try:
                SetForegroundWindow(hwnd)
                ShowWindow(hwnd, SW_SHOW)
                return True
            except Exception:
                pass
    return False


def bring_any_editor_to_front() -> bool:
    """Try common editor window titles (Notepad, VS Code)."""
    for key in ["notepad", "untitled - notepad", "visual studio code", "code"]:
        if bring_to_front_by_substring(key):
            return True
    return False
