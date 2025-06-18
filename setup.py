import sys
import os
from cx_Freeze import setup, Executable

# --- Automação para incluir todos os recursos ---
# Esta lista será usada pelo 'add-data' do PyInstaller, mas mantemos aqui para cx_Freeze se necessário
recursos_dir = "recursos"
recursos_incluidos = []
if os.path.exists(recursos_dir):
    recursos_incluidos = [os.path.join(recursos_dir, f) for f in os.listdir(recursos_dir)]

# --- Opções do Build para PyInstaller (ou cx_Freeze) ---
build_exe_options = {
    "packages": ["pygame", "time", "sys", "os", "math", "random", "sqlite3", "datetime", "pyttsx3", "speech_recognition", "aifc", "chunk", "audioop"],
    "include_files": recursos_incluidos,
    "excludes": ["tkinter"]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Tetrizos",
    version="1.0",
    description="Jogo Tetrizos",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)