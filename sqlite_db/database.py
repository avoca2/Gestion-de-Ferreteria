import sqlite3
import hashlib
import secrets
from config import Config

class SQLiteDatabase:
    def __init__(self, db_path=Config.SQLITE_DB_PATH):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establecer conexión con SQLite"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def disconnect(self):
        """Cerrar conexión con SQLite"""
        if self.connection:
            self.connection.close()
    
    def create_tables(self):
        """Crear tablas iniciales incluyendo usuarios"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            nombre_completo VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            rol VARCHAR(20) DEFAULT 'cajero',
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultimo_login DATETIME,
            salt VARCHAR(50) NOT NULL
        )
        """)
        
        # Tabla de productos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo VARCHAR(50) UNIQUE NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            categoria VARCHAR(50),
            precio_compra DECIMAL(10,2) NOT NULL,
            precio_venta DECIMAL(10,2) NOT NULL,
            stock INTEGER DEFAULT 0,
            stock_minimo INTEGER DEFAULT 5,
            proveedor VARCHAR(100),
            fecha_ingreso DATE DEFAULT CURRENT_DATE
        )
        """)
        
        # Tabla de clientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut VARCHAR(20) UNIQUE NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            telefono VARCHAR(20),
            email VARCHAR(100),
            direccion TEXT,
            tipo_cliente VARCHAR(20) DEFAULT 'normal',
            fecha_registro DATE DEFAULT CURRENT_DATE
        )
        """)
        
        # Tabla de ventas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_folio VARCHAR(50) UNIQUE NOT NULL,
            cliente_id INTEGER,
            usuario_id INTEGER,
            fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
            subtotal DECIMAL(10,2) NOT NULL,
            iva DECIMAL(10,2) NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            metodo_pago VARCHAR(20),
            estado VARCHAR(20) DEFAULT 'completada',
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """)
        
        # Tabla de detalle de ventas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            total_linea DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
        """)
        
        # Insertar usuario admin por defecto si no existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256(('admin123' + salt).encode()).hexdigest()
            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol, salt)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('admin', password_hash, 'Administrador Principal', 'admin@donwilly.cl', 'admin', salt))
        
        conn.commit()
        print("Tablas SQLite creadas exitosamente")
        print("Usuario por defecto creado: admin / admin123")
    
    def get_connection(self):
        """Obtener conexión activa"""
        if not self.connection:
            self.connect()
        return self.connection
    
    def verificar_usuario(self, username, password):
        """Verificar credenciales de usuario"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, password_hash, nombre_completo, rol, salt, activo 
                FROM usuarios 
                WHERE username = ? AND activo = 1
            """, (username,))
            
            usuario = cursor.fetchone()
            
            if usuario:
                # Verificar contraseña
                password_hash = hashlib.sha256((password + usuario['salt']).encode()).hexdigest()
                
                if password_hash == usuario['password_hash']:
                    # Actualizar último login
                    cursor.execute("""
                        UPDATE usuarios 
                        SET ultimo_login = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (usuario['id'],))
                    conn.commit()
                    
                    return {
                        'id': usuario['id'],
                        'username': usuario['username'],
                        'nombre_completo': usuario['nombre_completo'],
                        'rol': usuario['rol'],
                        'activo': usuario['activo']
                    }
            
            return None
            
        except Exception as e:
            print(f"Error al verificar usuario: {e}")
            return None
        finally:
            self.disconnect()