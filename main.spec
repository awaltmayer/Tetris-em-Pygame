# -*- mode: python ; coding: utf-8 -*-

# Define o nome da pasta de recursos
recursos = 'recursos'

# Coleta todos os arquivos da pasta de recursos
datas = []
for f in os.listdir(recursos):
    datas.append( (os.path.join(recursos, f), recursos) )

# Análise principal do script
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'aifc',
        'chunk',
        'audioop',
        'pyttsx3.drivers.sapi5'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Configuração do executável
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Tetrizos',  # Nome do seu arquivo .exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Garante que a tela preta do console não apareça
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Coleta de todos os arquivos para criar a pasta final
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Tetrizos_App', # Nome da pasta que será criada dentro de 'dist'
)