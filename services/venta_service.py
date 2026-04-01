from sqlite_db.database import SQLiteDatabase
from sqlite_db.models import Venta
from mongodb_db.database import MongoDBDatabase
from mongodb_db.models import Movimiento
from datetime import datetime
import uuid
from config import Config

class VentaService:
    def __init__(self):
        self.sqlite_db = SQLiteDatabase()
        self.mongo_db = MongoDBDatabase()
    
    def generar_folio(self):
        """Generar un número de folio único para la venta"""
        fecha_actual = datetime.now().strftime("%Y%m%d")
        consecutivo = str(uuid.uuid4().int)[:6]
        return f"VTA-{fecha_actual}-{consecutivo}"
    
    def crear_venta(self, datos_venta, items_venta, usuario="cajero"):
        """Crear una nueva venta"""
        conn = self.sqlite_db.connect()
        cursor = conn.cursor()
        
        try:
            # Generar folio único
            folio = self.generar_folio()
            
            # Calcular totales
            subtotal = sum(item['precio_unitario'] * item['cantidad'] 
                          for item in items_venta)
            iva = subtotal * Config.IVA_PORCENTAJE
            total = subtotal + iva
            
            # Crear venta en SQLite
            venta = Venta(
                numero_folio=folio,
                cliente_id=datos_venta.get('cliente_id'),
                subtotal=subtotal,
                iva=iva,
                total=total,
                metodo_pago=datos_venta.get('metodo_pago', 'efectivo')
            )
            
            cursor.execute('''
                INSERT INTO ventas 
                (numero_folio, cliente_id, subtotal, iva, total, metodo_pago)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                venta.numero_folio, venta.cliente_id, venta.subtotal,
                venta.iva, venta.total, venta.metodo_pago
            ))
            
            venta_id = cursor.lastrowid
            
            # Insertar items de la venta
            for item in items_venta:
                cursor.execute('''
                    INSERT INTO detalle_ventas 
                    (venta_id, producto_id, cantidad, precio_unitario, total_linea)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    venta_id, item['producto_id'], item['cantidad'],
                    item['precio_unitario'], item['precio_unitario'] * item['cantidad']
                ))
                
                # Actualizar stock del producto
                producto_service = ProductoService()
                producto_service.actualizar_stock(
                    item['producto_id'], 
                    item['cantidad'], 
                    'venta',
                    usuario
                )
            
            conn.commit()
            
            # Registrar movimiento en MongoDB
            movimiento = Movimiento(
                tipo='venta',
                entidad='venta',
                entidad_id=venta_id,
                usuario=usuario,
                datos_nuevos={
                    'folio': folio,
                    'cliente_id': venta.cliente_id,
                    'total': venta.total,
                    'items': items_venta
                },
                detalles=f"Venta realizada con {len(items_venta)} productos"
            )
            
            mongo_db = self.mongo_db.get_database()
            mongo_db.movimientos.insert_one(movimiento.to_dict())
            
            # Actualizar estadísticas en MongoDB
            self._actualizar_estadisticas_venta(venta, items_venta)
            
            print(f"Venta {folio} creada exitosamente")
            return {'venta_id': venta_id, 'folio': folio, 'total': total}
            
        except Exception as e:
            conn.rollback()
            print(f"Error al crear venta: {e}")
            return None
        finally:
            self.sqlite_db.disconnect()
    
    def _actualizar_estadisticas_venta(self, venta, items_venta):
        """Actualizar estadísticas de ventas en MongoDB"""
        mongo_db = self.mongo_db.get_database()
        
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        mes_actual = datetime.now().strftime("%Y-%m")
        
        # Actualizar estadísticas diarias
        mongo_db.estadisticas.update_one(
            {'tipo': 'ventas_diarias', 'fecha': fecha_hoy},
            {
                '$inc': {
                    'total_ventas': 1,
                    'total_ingresos': venta.total,
                    'cantidad_productos': sum(item['cantidad'] for item in items_venta)
                },
                '$push': {
                    'ventas': {
                        'venta_id': venta.numero_folio,
                        'total': venta.total,
                        'metodo_pago': venta.metodo_pago
                    }
                }
            },
            upsert=True
        )
        
        # Actualizar estadísticas mensuales
        mongo_db.estadisticas.update_one(
            {'tipo': 'ventas_mensuales', 'mes': mes_actual},
            {
                '$inc': {
                    'total_ventas': 1,
                    'total_ingresos': venta.total
                }
            },
            upsert=True
        )
    
    def obtener_ventas_dia(self):
        """Obtener ventas del día actual"""
        conn = self.sqlite_db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT v.*, c.nombre as cliente_nombre 
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                WHERE DATE(v.fecha_venta) = DATE('now')
                ORDER BY v.fecha_venta DESC
            ''')
            
            ventas = cursor.fetchall()
            return [dict(venta) for venta in ventas]
            
        except Exception as e:
            print(f"Error al obtener ventas del día: {e}")
            return []
        finally:
            self.sqlite_db.disconnect()