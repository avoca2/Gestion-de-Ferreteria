from datetime import datetime
from bson import ObjectId

class Movimiento:
    def __init__(self, tipo, entidad, entidad_id, usuario, **kwargs):
        self.tipo = tipo  # 'creacion', 'actualizacion', 'eliminacion', 'venta', 'compra'
        self.entidad = entidad  # 'producto', 'cliente', 'venta', etc.
        self.entidad_id = entidad_id
        self.usuario = usuario
        self.datos_anteriores = kwargs.get('datos_anteriores', {})
        self.datos_nuevos = kwargs.get('datos_nuevos', {})
        self.fecha = kwargs.get('fecha', datetime.now())
        self.detalles = kwargs.get('detalles', '')
    
    def to_dict(self):
        return {
            'tipo': self.tipo,
            'entidad': self.entidad,
            'entidad_id': self.entidad_id,
            'usuario': self.usuario,
            'datos_anteriores': self.datos_anteriores,
            'datos_nuevos': self.datos_nuevos,
            'fecha': self.fecha,
            'detalles': self.detalles
        }

class LogSistema:
    def __init__(self, nivel, mensaje, modulo, **kwargs):
        self.nivel = nivel  # 'INFO', 'ERROR', 'WARNING', 'DEBUG'
        self.mensaje = mensaje
        self.modulo = modulo
        self.fecha = kwargs.get('fecha', datetime.now())
        self.usuario = kwargs.get('usuario', 'sistema')
        self.ip = kwargs.get('ip', '')
    
    def to_dict(self):
        return {
            'nivel': self.nivel,
            'mensaje': self.mensaje,
            'modulo': self.modulo,
            'fecha': self.fecha,
            'usuario': self.usuario,
            'ip': self.ip
        }