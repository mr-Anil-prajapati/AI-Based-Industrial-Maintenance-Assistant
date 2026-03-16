# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path.cwd()
datas = [
    (str(project_root / "data"), "data"),
    (str(project_root / "rag_data"), "rag_data"),
    (str(project_root / "models"), "models"),
]

hiddenimports = [
    "chromadb",
    "llama_cpp",
    "backend.assistant_service",
    "backend.machine_analysis.rules",
    "backend.plc_interface.protocols",
]

a = Analysis(
    ["desktop_app/main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="IndustrialAIAssistant",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="IndustrialAIAssistant",
)
