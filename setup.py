from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {
    "packages": ["tkinter", "sqlite3", "hashlib", "secrets", "datetime"],
    "include_files": ["config.py", ".env"]
}

setup(
    name="DonWillyFerreteria",
    version="1.0",
    description="Sistema de Gestión Ferretería Don Willy",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="icon.ico")]
)
