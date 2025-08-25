# -*- coding: utf-8 -*-
def get_active_process_name() -> str:
    # ทำให้ง่าย: ไม่บังคับตรวจชื่อโปรเซส (อนุญาตหมด)
    return ""

def is_process_allowed(active_name: str, allowlist: list[str], denylist: list[str]) -> bool:
    if denylist:
        return False  # ถ้าใช้จริงควรหาชื่อโปรเซสแล้วเทียบ denylist
    return True
