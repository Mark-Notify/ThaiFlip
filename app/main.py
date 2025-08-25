# -*- coding: utf-8 -*-
import sys, os, json, time, platform
from threading import Thread, Event

import pyperclip
import keyboard
from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSystemTrayIcon, QMenu, QCheckBox
)
from mappings import convert_text_auto

APP_NAME = "ThaiFlip"
VERSION = "1.0.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")

def load_settings() -> dict:
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_settings(cfg: dict):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

IS_WINDOWS = platform.system() == "Windows"
if IS_WINDOWS:
    from util_win import get_active_process_name, is_process_allowed
else:
    from util_posix import get_active_process_name, is_process_allowed

# ---------- วาดไอคอนสถานะ (ซ้อนสี/เครื่องหมาย) ----------
def make_status_icon(base_icon: QIcon | None, running: bool) -> QIcon:
    size = 24
    pm = (base_icon.pixmap(size, size) if base_icon and not base_icon.isNull()
          else QPixmap(size, size))
    if pm.isNull():
        pm = QPixmap(size, size)
        pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing, True)
    r = 9
    cx, cy = pm.width() - r + 1, pm.height() - r + 1
    p.setBrush(QColor(28,185,65) if running else QColor(220,44,44))
    p.setPen(Qt.NoPen)
    p.drawEllipse(cx - r, cy - r, 2*r, 2*r)
    if running:
        pen = QPen(QColor(255,255,255)); pen.setWidth(2); p.setPen(pen)
        p.drawLine(cx - 5, cy, cx - 2, cy + 3)
        p.drawLine(cx - 2, cy + 3, cx + 4, cy - 4)
    p.end()
    out = QIcon(); out.addPixmap(pm); return out
# ------------------------------------------------------------

class BackgroundHotkeys:
    def __init__(self, state: dict):
        self.state = state
        self.stop_evt = Event()

    def _enabled(self) -> bool:
        return bool(self.state.get("enabled", True))

    def _check_allowed(self) -> bool:
        if not self._enabled():
            return False
        active = get_active_process_name()
        return is_process_allowed(active, self.state.get("allowlist", []), self.state.get("denylist", []))

    def _fix_selection(self):
        if not self._check_allowed():
            self.state["last_action"] = "Stopped/Blocked"
            return
        try:
            old_clip = pyperclip.paste()
            keyboard.send("ctrl+c"); time.sleep(0.05)
            selected = pyperclip.paste() or ""
            if not selected.strip():
                self.state["last_action"] = "No selection"; return
            fixed = convert_text_auto(selected)
            if fixed != selected:
                pyperclip.copy(fixed); keyboard.write(fixed)
                self.state["last_action"] = "Fixed selection"
            else:
                self.state["last_action"] = "No change"
            pyperclip.copy(old_clip)
        except Exception as e:
            self.state["last_action"] = f"Error: {e}"

    def _fix_last_word(self):
        if not self._check_allowed():
            self.state["last_action"] = "Stopped/Blocked"
            return
        try:
            old_clip = pyperclip.paste()
            keyboard.send("ctrl+shift+left"); time.sleep(0.03)
            keyboard.send("ctrl+c"); time.sleep(0.03)
            word = pyperclip.paste() or ""
            if not word.strip():
                keyboard.send("right"); self.state["last_action"] = "No word"; return
            fixed = convert_text_auto(word)
            if fixed != word:
                pyperclip.copy(fixed); keyboard.write(fixed)
                self.state["last_action"] = "Fixed last word"
            else:
                keyboard.send("right"); self.state["last_action"] = "No change"
            pyperclip.copy(old_clip)
        except Exception as e:
            self.state["last_action"] = f"Error: {e}"

    def _auto_mode_worker(self):
        keys = set(self.state.get("auto_keys", ["space","enter"]))
        while not self.stop_evt.is_set():
            if self.state.get("auto_mode") and self._enabled():
                try:
                    if any(keyboard.is_pressed(k) for k in keys):
                        old_clip = pyperclip.paste()
                        keyboard.send("ctrl+shift+left"); time.sleep(0.01)
                        keyboard.send("ctrl+c"); time.sleep(0.01)
                        word = pyperclip.paste() or ""
                        fixed = convert_text_auto(word)
                        if fixed != word:
                            pyperclip.copy(fixed); keyboard.write(fixed)
                            self.state["last_action"] = "Auto fixed"
                        keyboard.send("right")
                        pyperclip.copy(old_clip); time.sleep(0.08)
                except:
                    pass
            time.sleep(0.03)

    def start(self, hk_last: str, hk_sel: str):
        keyboard.add_hotkey(hk_last, self._fix_last_word, suppress=False)
        keyboard.add_hotkey(hk_sel, self._fix_selection, suppress=False)
        self.auto_thread = Thread(target=self._auto_mode_worker, daemon=True)
        self.auto_thread.start()

    def stop(self):
        self.stop_evt.set()
        keyboard.unhook_all_hotkeys()

class DockWidget(QWidget):
    def __init__(self, state: dict, cfg: dict, on_toggle):
        super().__init__()
        self.state, self.cfg, self.on_toggle = state, cfg, on_toggle
        self.setWindowTitle(APP_NAME)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(260, 180)

        root = QVBoxLayout(self); root.setContentsMargins(12,12,12,12)
        ttl = QLabel(f"{APP_NAME}  v{VERSION}"); ttl.setStyleSheet("font-weight:600;")
        root.addWidget(ttl)

        self.status = QLabel("Hotkeys loading…"); self.status.setWordWrap(True); root.addWidget(self.status)

        row = QHBoxLayout()
        self.pin = QCheckBox("Always on top"); self.pin.setChecked(True)
        self.pin.stateChanged.connect(self._toggle_pin); row.addWidget(self.pin)

        self.auto = QCheckBox("Auto mode (experimental)")
        self.auto.setChecked(bool(cfg.get("auto_mode", False)))
        self.auto.stateChanged.connect(self._toggle_auto); row.addWidget(self.auto)
        root.addLayout(row)

        btns = QHBoxLayout()
        b_fix = QPushButton("Fix selection"); b_fix.clicked.connect(lambda: keyboard.send(self.state.get("hk_sel"))); btns.addWidget(b_fix)
        self.btn_toggle = QPushButton("Stop" if self.state.get("enabled", True) else "Start")
        self.btn_toggle.clicked.connect(self._toggle_start_stop); btns.addWidget(self.btn_toggle)
        b_hide = QPushButton("Hide panel"); b_hide.clicked.connect(self.hide); btns.addWidget(b_hide)
        root.addLayout(btns)

        self.setStyleSheet("""
            QWidget { background: rgba(30,30,35,0.85); color: #fff; border-radius: 16px; }
            QPushButton { padding: 6px 10px; border: 1px solid rgba(255,255,255,0.15);
                          border-radius: 10px; background: rgba(255,255,255,0.06); }
            QPushButton:hover { background: rgba(255,255,255,0.12); }
            QCheckBox { padding: 2px 4px; }
        """)

        self.timer = QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(400)
        self._dock_right()

    def _dock_right(self):
        scr = QApplication.primaryScreen().availableGeometry()
        x = scr.right() - self.width() - int(self.cfg.get("panel_right_offset", 12))
        y = scr.top() + int(self.cfg.get("panel_top_offset", 12))
        self.setGeometry(QRect(x, y, self.width(), self.height()))

    def _toggle_pin(self, state):
        flags = self.windowFlags()
        flags = flags | Qt.WindowStaysOnTopHint if state == Qt.Checked else flags & ~Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags); self.show()

    def _toggle_auto(self, state):
        enabled = state == Qt.Checked
        self.state["auto_mode"] = enabled
        self.cfg["auto_mode"] = enabled
        save_settings(self.cfg)

    def _toggle_start_stop(self):
        self.on_toggle()
        self.btn_toggle.setText("Stop" if self.state.get("enabled", True) else "Start")

    def _tick(self):
        hk_lw = self.state.get("hk_last"); hk_sel = self.state.get("hk_sel")
        msg = self.state.get("last_action", "Ready")
        en = self.state.get("enabled", True)
        self.status.setText(f"Hotkeys: {hk_lw} | {hk_sel}\nStatus: {'Running' if en else 'Stopped'}\n{msg}")

class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv); self.app.setQuitOnLastWindowClosed(False)
        self.cfg = load_settings()

        self.state = {
            "auto_mode": bool(self.cfg.get("auto_mode", False)),
            "last_action": "Ready",
            "hk_last": self.cfg.get("hotkey_fix_last_word", "alt+`"),
            "hk_sel": self.cfg.get("hotkey_fix_selection", "alt+shift+`"),
            "allowlist": list(self.cfg.get("allowlist_processes", [])),
            "denylist": list(self.cfg.get("denylist_processes", [])),
            "auto_keys": list(self.cfg.get("auto_mode_trigger_keys", ["space","enter"])),
            "enabled": bool(self.cfg.get("enabled", True)),
        }

        # Dock panel
        self.dock = DockWidget(self.state, self.cfg, on_toggle=self._toggle)
        if bool(self.cfg.get("show_panel_on_start", True)): self.dock.show()

        # Tray & เมนู
        icon_path = os.path.join(BASE_DIR, "assets", "thaiflip.ico")
        self.base_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
        self.tray = QSystemTrayIcon(self._status_icon()); self.tray.setToolTip(APP_NAME)
        menu = QMenu()
        self.act_start = QAction("Start"); self.act_stop = QAction("Stop"); self.act_exit = QAction("Exit")
        self.act_start.triggered.connect(self._start); self.act_stop.triggered.connect(self._stop); self.act_exit.triggered.connect(self._quit)
        menu.addAction(self.act_start); menu.addAction(self.act_stop); menu.addSeparator(); menu.addAction(self.act_exit)
        self.tray.setContextMenu(menu); self.tray.show()
        self.state["update_tray_icon"] = self._refresh_tray_icon
        self._sync_menu_state()

        # Hotkeys
        self.hotkeys = BackgroundHotkeys(self.state)
        self.hotkeys.start(self.state["hk_last"], self.state["hk_sel"])

    # Tray helpers
    def _status_icon(self) -> QIcon:
        return make_status_icon(self.base_icon, bool(self.state.get("enabled", True)))

    def _refresh_tray_icon(self):
        self.tray.setIcon(self._status_icon()); self._sync_menu_state()

    def _sync_menu_state(self):
        en = bool(self.state.get("enabled", True))
        self.act_start.setEnabled(not en); self.act_stop.setEnabled(en)

    # Toggle from dock
    def _toggle(self):
        self.state["enabled"] = not self.state.get("enabled", True)
        self.cfg["enabled"] = self.state["enabled"]; save_settings(self.cfg)
        self.state["last_action"] = "Running" if self.state["enabled"] else "Stopped"
        self._refresh_tray_icon()

    def _start(self):
        self.state["enabled"] = True; self.cfg["enabled"] = True; save_settings(self.cfg)
        self.state["last_action"] = "Running"; self._refresh_tray_icon()

    def _stop(self):
        self.state["enabled"] = False; self.cfg["enabled"] = False; save_settings(self.cfg)
        self.state["last_action"] = "Stopped"; self._refresh_tray_icon()

    def _quit(self):
        self.hotkeys.stop(); self.tray.hide(); self.app.quit()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    # แนะนำ Run as Administrator บน Windows เพื่อให้ keyboard hook ได้ทั่วระบบ
    TrayApp().run()
