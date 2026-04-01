from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import Config

class MongoDBDatabase:
    def __init__(self):
        self.client = None
        self.db = None
        
    def connect(self):
        """Conectar a MongoDB"""
        try:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client[Config.MONGO_DB_NAME]
            print(f"Conectado a MongoDB: {Config.MONGO_DB_NAME}")
            return self.db
        except ConnectionFailure as e:
            print(f"Error de conexión a MongoDB: {e}")
            return None
    
    def disconnect(self):
        """Desconectar de MongoDB"""
        if self.client:
            self.client.close()
            print("Desconectado de MongoDB")
    
    def create_collections(self):
        """Crear colecciones iniciales en MongoDB"""
        if not self.db:
            self.connect()
        
        # Colección para historial de movimientos (datos semi-estructurados)
        if 'movimientos' not in self.db.list_collection_names():
            self.db.create_collection('movimientos')
        
        # Colección para logs del sistema
        if 'logs_sistema' not in self.db.list_collection_names():
            self.db.create_collection('logs_sistema')
        
        # Colección para estadísticas y reportes
        if 'estadisticas' not in self.db.list_collection_names():
            self.db.create_collection('estadisticas')
        
        # Colección para configuraciones del sistema
        if 'configuraciones' not in self.db.list_collection_names():
            self.db.create_collection('configuraciones')
            # Insertar configuración inicial
            self.db.configuraciones.insert_one({
                'empresa': Config.EMPRESA_NOMBRE,
                'iva_porcentaje': Config.IVA_PORCENTAJE,
                'moneda': 'CLP',
                'configurado': False
            })
        
        print("Colecciones MongoDB creadas exitosamente")
    
    def get_database(self):
        """Obtener instancia de la base de datos"""
        if not self.db:
            self.connect()
        return self.db