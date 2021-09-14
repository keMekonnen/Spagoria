from typing import Optional
from ctypes import wintypes, windll, create_unicode_buffer

#I dont understand this, props go to this person:https://stackoverflow.com/users/8874388/mitch-mcmabers . effing hero

def getForegroundWindowTitle() -> Optional[str]:
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    
    if buf.value:
        return buf.value
    else:
        return None

print(getForegroundWindowTitle())