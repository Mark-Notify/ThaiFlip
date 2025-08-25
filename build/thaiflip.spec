# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app_dir = os.path.join(base, "app")
assets_dir = os.path.join(app_dir, "assets")
icon_path = os.path.join(assets_dir, "thaiflip.ico")

a = Analysis(
    [os.path.join(app_dir, 'main.py')],
    pathex=[app_dir],
    binaries=[],
    datas=[
        (os.path.join(app_dir, 'settings.json'), 'settings.json'),
        (icon_path, 'assets')
    ],
    hiddenimports=collect_submodules('PySide6'),
    hookspath=[], runtime_hooks=[], excludes=[], noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name='ThaiFlip', debug=False, strip=False, upx=True,
    console=False, icon=icon_path if os.path.exists(icon_path) else None
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='ThaiFlip')
