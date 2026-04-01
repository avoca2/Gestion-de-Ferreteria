#!/usr/bin/env python3
"""
Archivo de inicio para Don Willy Ferretería
"""

import os
import sys
import subprocess

def main():
    """Iniciar aplicación"""
    print("=" * 50)
    print("  FERRETERÍA DON WILLY")
    print("  Sistema de Gestión")
    print("=" * 50)
    
    # Verificar si estamos en un ejecutable
    if getattr(sys, 'frozen', False):
        # Ejecutable compilado
        application_path = sys._MEIPASS
    else:
        # Desarrollo normal
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Directorio: {application_path}")
    print("Iniciando aplicación...")
    
    # Importar e iniciar la aplicación
    try:
        from main import main as start_app
        start_app()
    except ImportError as e:
        print(f"Error al importar: {e}")
        print("Intentando método alternativo...")
        
        # Método alternativo
        os.chdir(application_path)
        import main
        main.main()
    
    print("\nAplicación finalizada")

if __name__ == "__main__":
    main()