
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ui/themes/basalt.json', 'src/ui/themes')
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='VidGrabber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/ui/icons/icon.icns'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VidGrabber',
)

app = BUNDLE(
    coll,
    name='VidGrabber.app',
    icon='src/ui/icons/icon.icns',
    bundle_identifier='com.ohey.vidgrabber',

    info_plist={
        'CFBundleName': 'VidGrabber',
        'CFBundleDisplayName': 'VidGrabber',
        'CFBundleExecutable': 'VidGrabber',
        'CFBundlePackageType': 'APPL',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025 Ohey. All rights reserved.',
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13',
    },
)