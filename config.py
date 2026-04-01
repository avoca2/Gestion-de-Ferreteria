import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Obtener ruta base del proyecto
BASE_DIR = Path(__file__).parent

class Config:
    # Configuración SQLite
    SQLITE_DB_PATH = str(BASE_DIR / "don_willy.db")
    
    # Configuración MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = "don_willy_ferreteria"
    
    # Configuración general
    EMPRESA_NOMBRE = "FERRETERÍA DON WILLY"
    IVA_PORCENTAJE = 0.19  # 19% IVA
    
    # Configuración de usuarios y roles
    ROLES = {
        'admin': 'Administrador',
        'cajero': 'Cajero/Vendedor',
        'inventario': 'Gestor de Inventario',
        'consulta': 'Solo Consulta'
    }
    
    PERMISOS = {
        'admin': ['productos', 'clientes', 'ventas', 'reportes', 'usuarios', 'configuracion'],
        'cajero': ['ventas', 'clientes_consulta', 'productos_consulta'],
        'inventario': ['productos', 'reportes_inventario'],
        'consulta': ['productos_consulta', 'clientes_consulta', 'reportes_consulta']
    }
    
    # Configuración de interfaz
    PRIMARY_COLOR = "#2c3e50"     # Azul oscuro
    SECONDARY_COLOR = "#3498db"   # Azul claro
    SUCCESS_COLOR = "#27ae60"     # Verde
    DANGER_COLOR = "#e74c3c"      # Rojo
    WARNING_COLOR = "#f39c12"     # Naranja
    LIGHT_BG = "#ecf0f1"          # Fondo claro
    DARK_TEXT = "#2c3e50"         # Texto oscuro
    
    # Rutas de assets
    ASSETS_DIR = str(BASE_DIR / "assets")
    LOGO_PATH = str(BASE_DIR / "assets" / "logo.png")
    
    @staticmethod
    def crear_directorios():
        """Crear directorios necesarios"""
        import os
        os.makedirs(Config.ASSETS_DIR, exist_ok=True)
    
    @staticmethod
    def verificar_permiso(rol, permiso):
        """Verificar si un rol tiene un permiso específico"""
        if rol not in Config.PERMISOS:
            return False
        return permiso in Config.PERMISOS[rol]

# Crear directorios al importar
Config.crear_directorios()