from sqlite_db.database import SQLiteDatabase
from sqlite_db.models import Cliente
from mongodb_db.database import MongoDBDatabase
from mongodb_db.models import Movimiento

class ClienteService:
    def __init__(self):
        self.sqlite_db = SQLiteDatabase()
        self.mongo_db = MongoDBDatabase()
    
    def crear_cliente(self, cliente_data, usuario="admin"):
        """Crear un nuevo cliente"""
        conn = self.sqlite_db.connect()
        cursor = conn.cursor()
        
        try:
            cliente = Cliente(**cliente_data)
            
            cursor.execute('''
                INSERT INTO clientes 
                (rut, nombre, telefono, email, direccion, tipo_cliente)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                cliente.rut, cliente.nombre, cliente.telefono,
                cliente.email, cliente.direccion, cliente.tipo_cliente
            ))
            
            cliente_id = cursor.lastrowid
            conn.commit()
            
            # Registrar en MongoDB
            movimiento = Movimiento(
                tipo='creacion',
                entidad='cliente',
                entidad_id=cliente_id,
                usuario=usuario,
                datos_nuevos=cliente.to_dict()
            )
            
            mongo_db = self.mongo_db.get_database()
            mongo_db.movimientos.insert_one(movimiento.to_dict())
            
            print(f"Cliente '{cliente.nombre}' creado exitosamente")
            return cliente_id
            
        except Exception as e:
            conn.rollback()
            print(f"Error al crear cliente: {e}")
            return None
        finally:
            self.sqlite_db.disconnect()
    
    def crear_cliente_interactivo(self):
        """Crear cliente de forma interactiva"""
        print("\n--- CREAR NUEVO CLIENTE ---")
        
        rut = input("RUT: ")
        nombre = input("Nombre completo: ")
        telefono = input("Teléfono: ")
        email = input("Email: ")
        direccion = input("Dirección: ")
        
        print("\nTipo de cliente:")
        print("1. Normal")
        print("2. Preferencial")
        print("3. Mayorista")
        
        tipo_opcion = input("Seleccione tipo (1-3): ")
        tipos = {'1': 'normal', '2': 'preferencial', '3': 'mayorista'}
        tipo_cliente = tipos.get(tipo_opcion, 'normal')
        
        cliente_data = {
            'rut': rut,
            'nombre': nombre,
            'telefono': telefono,
            'email': email,
            'direccion': direccion,
            'tipo_cliente': tipo_cliente
        }
        
        cliente_id = self.crear_cliente(cliente_data, "sistema")
        if cliente_id:
            print(f"Cliente creado con ID: {cliente_id}")
            return cliente_id
        return None
    
    def listar_clientes(self):
        """Listar todos los clientes"""
        conn = self.sqlite_db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM clientes ORDER BY nombre')
            clientes = cursor.fetchall()
            
            if not clientes:
                print("\nNo hay clientes registrados")
                return
            
            print("\n--- LISTA DE CLIENTES ---")
            print(f"{'ID':<5} {'RUT':<12} {'Nombre':<25} {'Teléfono':<15} {'Tipo':<12}")
            print("-" * 70)
            
            for cliente in clientes:
                cliente_dict = dict(cliente)
                print(f"{cliente_dict['id']:<5} {cliente_dict['rut']:<12} "
                      f"{cliente_dict['nombre']:<25} {cliente_dict.get('telefono', ''):<15} "
                      f"{cliente_dict['tipo_cliente']:<12}")
                
        except Exception as e:
            print(f"Error al listar clientes: {e}")
        finally:
            self.sqlite_db.disconnect()
    
    def buscar_cliente_por_rut(self, rut):
        """Buscar cliente por RUT"""
        conn = self.sqlite_db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM clientes WHERE rut = ?', (rut,))
            cliente = cursor.fetchone()
            
            if cliente:
                return dict(cliente)
            return None
            
        except Exception as e:
            print(f"Error al buscar cliente: {e}")
            return None
        finally:
            self.sqlite_db.disconnect()