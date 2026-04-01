#!/usr/bin/env python3
"""
Creador de paquete portable para Don Willy Ferretería
Versión para Linux/macOS que crea paquete para Windows
"""

import os
import shutil
import zipfile
from datetime import datetime

def crear_portable():
    print("🔥 Creando paquete portable para Windows desde Linux/macOS...")
    
    # Crear estructura de carpetas
    portable_dir = "DonWilly_Portable_Windows"
    
    if os.path.exists(portable_dir):
        print("⚠️  Eliminando versión anterior...")
        shutil.rmtree(portable_dir)
    
    print("📁 Creando estructura de carpetas...")
    os.makedirs(os.path.join(portable_dir, "app"))
    os.makedirs(os.path.join(portable_dir, "data"))
    os.makedirs(os.path.join(portable_dir, "backups"))
    os.makedirs(os.path.join(portable_dir, "logs"))
    
    # 1. Primero crear el .exe si no existe
    exe_path = "dist/DonWillyFerreteria.exe"
    if not os.path.exists(exe_path):
        print("🔨 Creando ejecutable con PyInstaller...")
        resultado = os.system("pyinstaller --onefile --windowed --clean --name DonWillyFerreteria main.py")
        if resultado != 0:
            print("❌ Error al crear el ejecutable")
            return
    
    # 2. Copiar el .exe
    if os.path.exists(exe_path):
        destino = os.path.join(portable_dir, "app", "DonWillyFerreteria.exe")
        shutil.copy2(exe_path, destino)
        print(f"✓ Ejecutable copiado a: {destino}")
    else:
        print("❌ No se encontró el ejecutable en dist/")
        print("   Ejecuta primero: pyinstaller --onefile --windowed --name DonWillyFerreteria main.py")
        return
    
    # 3. Crear archivos de apoyo
    
    # Iniciar.bat (para Windows)
    bat_content = """@echo off
chcp 65001 > nul
title Ferretería Don Willy
echo ========================================
echo   FERRETERÍA DON WILLY
echo   Sistema Portable
echo ========================================
echo.

:: Crear carpetas necesarias
if not exist "data\\" mkdir data
if not exist "backups\\" mkdir backups
if not exist "logs\\" mkdir logs

:: Ejecutar aplicación
echo Iniciando sistema...
echo.
start "" "app\\DonWillyFerreteria.exe"

echo Aplicación iniciada. Puede cerrar esta ventana.
pause
"""
    
    bat_path = os.path.join(portable_dir, "Iniciar.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)
    print(f"✓ Archivo Iniciar.bat creado")
    
    # LEAME.txt
    fecha = datetime.now().strftime("%d/%m/%Y")
    readme_content = f"""FERRETERÍA DON WILLY - VERSIÓN PORTABLE
Fecha: {fecha}

INSTRUCCIONES:
1. Copie esta carpeta completa a cualquier ubicación
2. Ejecute "Iniciar.bat"
3. ¡Listo! No requiere instalación

USUARIO POR DEFECTO:
- Usuario: admin
- Contraseña: admin123

CARACTERÍSTICAS:
√ Totalmente portable (USB, nube, disco duro)
√ No requiere instalación
√ Datos en carpeta "data"
√ Windows 7/8/10/11 compatible

Para soporte: contacto@donwilly.cl
"""
    
    readme_path = os.path.join(portable_dir, "LEAME.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"✓ Archivo LEAME.txt creado")
    
    # 4. Crear ZIP para distribución
    zip_name = f"DonWilly_Portable_{datetime.now().strftime('%Y%m%d')}.zip"
    print(f"📦 Creando archivo ZIP: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Nombre relativo dentro del ZIP
                arcname = os.path.relpath(file_path, os.path.dirname(portable_dir))
                zipf.write(file_path, arcname)
    
    print(f"\n✅ ¡PAQUETE CREADO EXITOSAMENTE!")
    print("=" * 50)
    print(f"📂 Carpeta creada: {portable_dir}/")
    print(f"📦 Archivo ZIP: {zip_name}")
    print("=" * 50)
    print("\n📋 Para distribuir en Windows:")
    print(f"   1. Envía el archivo '{zip_name}'")
    print(f"   2. El usuario debe descomprimirlo")
    print(f"   3. Ejecutar 'Iniciar.bat'")
    print("\n⚡ Tamaño estimado del .exe:", os.path.getsize(exe_path) // 1024, "KB")

def verificar_dependencias():
    """Verificar que PyInstaller está instalado"""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("❌ PyInstaller no está instalado")
        print("   Instala con: pip install pyinstaller")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("  CREADOR DE PAQUETE PORTABLE")
    print("  Ferretería Don Willy")
    print("=" * 50)
    
    if not verificar_dependencias():
        exit(1)
    
    crear_portable()