#!/bin/bash
# Script para crear ejecutable Don Willy para Windows

echo "========================================="
echo "  CONSTRUCTOR DON WILLY PARA WINDOWS"
echo "========================================="

# Crear entorno virtual para construcción
echo "1. Creando entorno virtual..."
python3 -m venv build_env
source build_env/bin/activate

# Instalar dependencias
echo "2. Instalando dependencias..."
pip install --upgrade pip
pip install pyinstaller pillow python-dotenv pymongo pytz

# Crear directorio de distribución
echo "3. Preparando archivos..."
mkdir -p dist/windows
cp main.py config.py .env dist/windows/
cp -r assets dist/windows/ 2>/dev/null || mkdir -p dist/windows/assets

# Crear script de inicio para Windows
cat > dist/windows/iniciar.bat << 'EOF'
@echo off
chcp 65001 > nul
title Ferreteria Don Willy
echo ======================================
echo    FERRETERIA DON WILLY
echo    Sistema de Gestion
echo ======================================
echo.
echo Iniciando...
python main.py
pause
EOF

# Construir con PyInstaller
echo "4. Construyendo ejecutable..."
cd dist/windows
pyinstaller --onefile --windowed --name="DonWilly" --add-data="config.py:." --add-data=".env:." --add-data="assets:assets" --hidden-import=tkinter --hidden-import=sqlite3 --hidden-import=PIL main.py

# Mover ejecutable
mv dist/DonWilly.exe .
cd ../..

# Crear ZIP final
echo "5. Creando paquete final..."
cd dist
zip -r "DonWilly_Windows_$(date +%Y%m%d).zip" windows/
cd ..

echo "========================================="
echo "✅ CONSTRUCCIÓN COMPLETADA!"
echo "========================================="
echo ""
echo "Archivo creado: dist/DonWilly_Windows_*.zip"
echo ""
echo "Para usar en Windows:"
echo "1. Descomprima el ZIP"
echo "2. Ejecute 'DonWilly.exe'"
echo "3. ¡Listo!"
echo ""

# Limpiar
deactivate
rm -rf build_env

echo "Proceso finalizado."