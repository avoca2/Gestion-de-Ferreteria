#!/usr/bin/env python3
"""
Versión portable que funciona desde USB o carpeta
"""

import os
import sys
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def crear_version_portable():
    """Crear versión portable completa"""
    
    print("Creando versión portable...")
    
    # Nombre de la versión
    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    nombre_portable = f"DonWilly_Portable_{fecha}"
    
    # Directorio de trabajo
    portable_dir = Path("portable") / nombre_portable
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # Archivos principales
    archivos_principales = [
        'main.py',
        'config.py',
        '.env',
        'requirements.txt'
    ]
    
    # Copiar archivos
    for archivo in archivos_principales:
        if Path(archivo).exists():
            shutil.copy2(archivo, portable_dir / archivo)
            print(f"✓ {archivo}")
    
    # Crear archivo de inicio automático
    crear_launcher(portable_dir)
    
    # Crear estructura de carpetas
    (portable_dir / 'data').mkdir(exist_ok=True)
    (portable_dir / 'backups').mkdir(exist_ok=True)
    (portable_dir / 'logs').mkdir(exist_ok=True)
    
    # Actualizar config.py para portable
    config_portable = '''import os
from pathlib import Path

# Ruta portable
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

class Config:
    # Base de datos en carpeta data
    SQLITE_DB_PATH = str(BASE_DIR / "data" / "don_willy.db")
    
    # MongoDB opcional
    MONGO_URI = "mongodb://localhost:27017/"
    MONGO_DB_NAME = "don_willy_ferreteria"
    
    # Configuración general
    EMPRESA_NOMBRE = "FERRETERÍA DON WILLY"
    IVA_PORCENTAJE = 0.19
    
    # Colores de interfaz
    PRIMARY_COLOR = "#2c3e50"
    SECONDARY_COLOR = "#3498db"
    SUCCESS_COLOR = "#27ae60"
    DANGER_COLOR = "#e74c3c"
    WARNING_COLOR = "#f39c12"
    LIGHT_BG = "#ecf0f1"
    DARK_TEXT = "#2c3e50"
    
    # Rutas
    LOGS_DIR = str(BASE_DIR / "logs")
    BACKUP_DIR = str(BASE_DIR / "backups")
    
    @staticmethod
    def verificar_directorios():
        """Crear directorios necesarios"""
        import os
        os.makedirs(os.path.dirname(Config.SQLITE_DB_PATH), exist_ok=True)
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)

# Verificar directorios al importar
Config.verificar_directorios()
'''
    
    with open(portable_dir / 'config_portable.py', 'w', encoding='utf-8') as f:
        f.write(config_portable)
    
    # Crear README portable
    readme = f'''FERRETERÍA DON WILLY - VERSIÓN PORTABLE
Versión: {fecha}
============================================

INSTRUCCIONES:
1. Descomprima esta carpeta en cualquier ubicación
2. Ejecute "Iniciar Don Willy.bat"
3. ¡Listo! No requiere instalación

CARACTERÍSTICAS PORTABLES:
✓ Funciona desde USB, disco duro o nube
✓ No modifica el registro de Windows
✓ Datos guardados en carpeta local
✓ Compatible con Windows 7/8/10/11

ESTRUCTURA:
- Iniciar Don Willy.bat   (Lanzador)
- main.py                 (Aplicación principal)
- data/                   (Base de datos)
- backups/                (Copias de seguridad)
- logs/                   (Registros del sistema)

NOTAS:
- Los datos se guardan en la carpeta "data"
- Realice copias periódicas de la carpeta completa
- Para actualizar, reemplace solo los archivos .py

© 2024 Ferretería Don Willy - Versión Portable
'''
    
    with open(portable_dir / 'LEAME.txt', 'w', encoding='utf-8') as f:
        f.write(readme)
    
    # Crear ZIP
    print("\nCreando archivo ZIP portable...")
    zip_path = f"dist/{nombre_portable}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, portable_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✅ Versión portable creada: {zip_path}")
    
    # Limpiar
    shutil.rmtree(portable_dir)
    
    return zip_path

def crear_launcher(directorio):
    """Crear lanzador batch para Windows"""
    
    # Lanzador .bat
    launcher_bat = '''@echo off
chcp 65001 > nul
title Ferreteria Don Willy - Sistema de Gestion
echo ========================================
echo   FERRETERIA DON WILLY
echo   Sistema de Gestion - Version Portable
echo ========================================
echo.
echo Iniciando sistema...

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado.
    echo.
    echo Instalando Python automaticamente...
    powershell -Command "Start-Process 'https://www.python.org/downloads/'"
    echo Por favor instale Python y vuelva a intentar.
    pause
    exit /b 1
)

REM Verificar dependencias
echo Verificando dependencias...
pip install --quiet python-dotenv pillow >nul 2>&1

REM Iniciar aplicacion
echo Iniciando aplicacion principal...
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo iniciar la aplicacion.
    echo.
    echo Soluciones posibles:
    echo 1. Verifique que Python este instalado
    echo 2. Ejecute: pip install -r requirements.txt
    echo 3. Contacte a soporte tecnico
    pause
)
'''
    
    # Lanzador .vbs (para ocultar consola)
    launcher_vbs = '''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c Iniciar Don Willy.bat", 0, True
'''
    
    # Guardar archivos
    with open(directorio / 'Iniciar Don Willy.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_bat)
    
    with open(directorio / 'Iniciar.vbs', 'w', encoding='utf-8') as f:
        f.write(launcher_vbs)
    
    print("✓ Lanzadores creados")

if __name__ == "__main__":
    print("CONSTRUCTOR DE VERSIÓN PORTABLE")
    print("=" * 50)
    
    zip_file = crear_version_portable()
    
    print("\n" + "=" * 50)
    print("✅ PORTABLE CREADO EXITOSAMENTE")
    print("=" * 50)
    print(f"\nArchivo: {zip_file}")
    print("\nInstrucciones para el usuario:")
    print("1. Descomprima el ZIP en cualquier carpeta")
    print("2. Ejecute 'Iniciar Don Willy.bat'")
    print("3. ¡Listo! Funciona sin instalación")