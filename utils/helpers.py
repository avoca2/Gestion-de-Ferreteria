from datetime import datetime

def formatear_moneda(valor):
    """Formatear valor como moneda"""
    return f"${valor:,.2f}"

def formatear_fecha(fecha):
    """Formatear fecha para mostrar"""
    if isinstance(fecha, str):
        return fecha
    elif isinstance(fecha, datetime):
        return fecha.strftime("%d/%m/%Y %H:%M:%S")
    return str(fecha)

def calcular_iva(subtotal, porcentaje_iva=0.19):
    """Calcular IVA de un subtotal"""
    return subtotal * porcentaje_iva

def validar_rut(rut):
    """Validar formato de RUT chileno (simple)"""
    rut = rut.replace(".", "").replace("-", "").upper()
    if len(rut) < 2:
        return False
    
    cuerpo = rut[:-1]
    dv = rut[-1]
    
    try:
        int(cuerpo)
    except ValueError:
        return False
    
    return True

def generar_codigo_producto(nombre, categoria):
    """Generar código de producto automático"""
    iniciales_categoria = categoria[:3].upper()
    iniciales_nombre = ''.join([palabra[0] for palabra in nombre.split()[:3]]).upper()
    timestamp = datetime.now().strftime("%m%d")
    
    return f"{iniciales_categoria}-{iniciales_nombre}-{timestamp}"