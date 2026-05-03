# -*- mode: python ; coding: utf-8 -*-

import customtkinter
from pathlib import Path

block_cipher = None
ctk_data = Path(customtkinter.__file__).parent
project_root = Path(SPECPATH if 'SPECPATH' in dir() else '.').resolve()
assets_dir = project_root / 'assets'

a = Analysis(
    ['autoclicker.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        (str(ctk_data), 'customtkinter'),
        (str(assets_dir), 'assets'),
    ],
    hiddenimports=[
        'mouse',
        'keyboard',
        'pyautogui',
        'pygetwindow',
        'pystray',
        'pystray._win32',
        'customtkinter',
        'darkdetect',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'octoautoclicker',
        'octoautoclicker.app',
        'octoautoclicker.config',
        'octoautoclicker.models',
        'octoautoclicker.engines',
        'octoautoclicker.engines.clicker',
        'octoautoclicker.engines.macros',
        'octoautoclicker.engines.hotkeys',
        'octoautoclicker.engines.tray',
        'octoautoclicker.ui',
        'octoautoclicker.ui.main_window',
        'octoautoclicker.ui.clicker_view',
        'octoautoclicker.ui.macro_view',
        'octoautoclicker.ui.macro_editor',
        'octoautoclicker.ui.mini_controller',
        'octoautoclicker.ui.about_view',
        'octoautoclicker.ui.sequence_view',
        'octoautoclicker.ui.profiles_view',
        'octoautoclicker.ui.settings_view',
        'octoautoclicker.ui.stats_view',
        'octoautoclicker.ui.theme',
        'octoautoclicker.ui.widgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OctoAutoClicker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
    icon=str(assets_dir / 'octo-icon.ico'),
)
