from sqlite_db.database import SQLiteDatabase
from sqlite_db.models import Producto
from mongodb_db.database import MongoDBDatabase
from mongodb_db.models import Movimiento
from datetime import datetime

class ProductoService:
    def __init__(self):
        self.sqlite_db = SQLiteDatabase()
        self.mongo_db = MongoDBDatabase()
    
    def crear_producto(self, producto_data, usuario="admin"):
        """Crear un nuevo producto en ambas bases de datos"""
        conn = self.sqlite_db.connect()
        cursor = conn.cursor()
        
        try:
            # Crear producto en SQLite
            producto = Producto(**producto_data)
            
            cursor.execute('''
                INSERT INTO productos 
                (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, 
                 stock, stock_minimo, proveedor, fecha_ingreso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                producto.codigo, producto.nombre, producto.descripcion, 
                producto.categoria, producto.precio_compra, producto.precio_venta,
                producto.stock, producto.stock_minimo, producto.proveedor,
                producto.fecha_ingreso
            ))
            
            producto_id = cursor.lastrowid
            conn.commit()
            
            # Registrar movimiento en MongoDB
            movimiento = Movimiento(
                tipo='creacion',
                entidad='producto',
                entidad_id=producto_id,
                usuario=usuario,
                datos_nuevos=producto.to_dict()
            )
            
            mongo_db = self.mongo_db.get_database()
            mongo_db.movimientos.insert_one(movimiento.to_dict())
            
            print(f"Producto '{producto.nombre}' creado exitosamente (ID: {producto_id})")
            return producto_id
            
        except Exception as e:
            conn.rollback()
            print(f"Error al crear producto: {e}")
            return None
        finally:
            self.sqlite_db.disconnect()
    
    def obtener_productos(self, categoria=None):
        """Obtener productos desde SQLite"""
        conn = self.sqlite_db.connect()
        cursor = conn.cursor()
        
        try:
            if categoria:
                cursor.execute('SELECT * FROM productos WHERE categoria = ?', (categoria,))
            else:
                cursor.execute('SELECT * FROM productos')
            
            productos = cursor.fetchall()
            return [dict(producto) for producto in productos]
            
        except Exception as e:
            print(f"Error al obtener productos: {e}")
            return []
        finally:
            self.sqlite_db.disconnect()
    
    def actualizar_stock(self, producto_id, cantidad, operacion='venta', usuario="admin"):
        """Actualizar stock de un producto"""
        conn = self.sqlite_db.connect()
        cursor = conn.cursor()
        
        try:
            # Obtener producto actual
            cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
            producto_actual = cursor.fetchone()
            
            if not producto_actual:
                print(f"Producto con ID {producto_id} no encontrado")
                return False
            
            producto_actual = dict(producto_actual)
            stock_actual = producto_actual['stock']
            
            # Calcular nuevo stock
            if operacion == 'venta':
                nuevo_stock = stock_actual - cantidad
                if nuevo_stock < 0:
                    print("Stock insuficiente")
                    return False
            elif operacion == 'compra':
                nuevo_stock = stock_actual + cantidad
            else:
                print(f"Operación no válida: {operacion}")
                return False
            
            # Actualizar en SQLite
            cursor.execute('UPDATE productos SET stock = ? WHERE id = ?', 
                          (nuevo_stock, producto_id))
            
            conn.commit()
            
            # Registrar movimiento en MongoDB
            movimiento = Movimiento(
                tipo='actualizacion',
                entidad='producto',
                entidad_id=producto_id,
                usuario=usuario,
                datos_anteriores={'stock': stock_actual},
                datos_nuevos={'stock': nuevo_stock},
                detalles=f"{operacion} de {cantidad} unidades"
            )
            
            mongo_db = self.mongo_db.get_database()
            mongo_db.movimientos.insert_one(movimiento.to_dict())
            
            print(f"Stock actualizado: {stock_actual} -> {nuevo_stock}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error al actualizar stock: {e}")
            return False
        finally:
            self.sqlite_db.disconnect()
    
    def productos_bajo_stock_minimo(self):
        """Obtener productos con stock por debajo del mínimo"""
        conn = self.sqlite_db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM productos 
                WHERE stock <= stock_minimo 
                ORDER BY stock ASC
            ''')
            
            productos = cursor.fetchall()
            return [dict(producto) for producto in productos]
            
        except Exception as e:
            print(f"Error al obtener productos bajo stock: {e}")
            return []
        finally:
            self.sqlite_db.disconnect()