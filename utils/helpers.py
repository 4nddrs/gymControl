"""
Utilidades generales
"""
from datetime import datetime

def format_date(date, formato='%d/%m/%Y'):
    """Formatear fecha"""
    if isinstance(date, str):
        return date
    if isinstance(date, datetime):
        return date.strftime(formato)
    return ''

def format_datetime(dt, formato='%d/%m/%Y %H:%M'):
    """Formatear fecha y hora"""
    if isinstance(dt, datetime):
        return dt.strftime(formato)
    return ''

def format_currency(amount):
    """Formatear cantidad como moneda"""
    return f"${amount:,.2f}"

def calcular_edad(fecha_nacimiento):
    """Calcular edad a partir de fecha de nacimiento"""
    if not fecha_nacimiento:
        return None
    
    hoy = datetime.now()
    edad = hoy.year - fecha_nacimiento.year
    
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    
    return edad

def paginar(items, page, per_page):
    """Paginar una lista de items"""
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': items[start:end],
        'total': len(items),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(items) + per_page - 1) // per_page
    }
