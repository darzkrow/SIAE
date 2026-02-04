from decimal import Decimal
from datetime import datetime, date
from django.utils import timezone
import random
import string

def format_currency(amount, currency='Bs.'):
    """
    Formatear cantidad como moneda    
    Ejemplo: 1234.56 -> "Bs. 1.234,56"
    """
    if amount is None:
        return f"{currency} 0,00"
    amount = Decimal(str(amount))
    formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"{currency} {formatted}"


def format_rif(rif):
    """
    Formatear RIF con guiones    
    Ejemplo: J123456789 -> J-12345678-9
    """
    rif = rif.upper().replace('-', '')
    if len(rif) >= 9:
        return f"{rif[0]}-{rif[1:9]}-{rif[9:]}" if len(rif) > 9 else f"{rif[0]}-{rif[1:]}"
    return rif


def format_phone(phone):
    """
    Formatear teléfono con guión
    Ejemplo: 04141234567 -> 0414-1234567
    """
    phone = phone.replace('-', '').replace(' ', '')
    if len(phone) == 11:
        return f"{phone[:4]}-{phone[4:]}"
    elif len(phone) == 10:
        return f"{phone[:3]}-{phone[3:]}"
    return phone


def get_current_datetime():
    """Obtener fecha y hora actual con timezone"""
    return timezone.now()


def get_current_date():
    """Obtener solo la fecha actual"""
    return timezone.now().date()


def parse_date(date_string, format='%Y-%m-%d'):
    """
    Convertir string a fecha    
    Ejemplo: "2026-02-04" -> date(2026, 2, 4)
    """
    try:
        return datetime.strptime(date_string, format).date()
    except (ValueError, TypeError):
        return None


def calculate_percentage(part, total):
    """
    Calcular porcentaje    
    Ejemplo: calculate_percentage(25, 100) -> 25.0
    """
    if total == 0:
        return Decimal('0')
    return (Decimal(str(part)) / Decimal(str(total))) * 100


def truncate_string(text, max_length=50, suffix='...'):
    """
    Truncar texto largo    
    Ejemplo: truncate_string("Texto muy largo", 10) -> "Texto m..."
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_string(text):
    """Limpiar string: quitar espacios extras y convertir a minúsculas"""
    if not text:
        return ''
    return ' '.join(text.strip().lower().split())


def generate_code(prefix='', length=8):
    """
    Generar código único    
    Ejemplo: generate_code('INV', 6) -> "INV-123456"
    """

    code = ''.join(random.choices(string.digits, k=length))
    return f"{prefix}-{code}" if prefix else code
