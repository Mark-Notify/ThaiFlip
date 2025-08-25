# -*- coding: utf-8 -*-
import ctypes
import psutil
from ctypes import wintypes

user32 = ctypes.windll.user32

def get_active_process_name() -> str:
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ""
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        p = psutil.Process(pid.value)
        return (p.name() or "").lower()
    except Exception:
        return ""

def is_process_allowed(active_name: str, allowlist: list[str], denylist: list[str]) -> bool:
    name = (active_name or "").lower()
    if any(name == d.lower() for d in denylist):
        return False
    if not allowlist:
        return True
    return any(name == a.lower() for a in allowlist)
