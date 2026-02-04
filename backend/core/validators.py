import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_rif(value):
    """
    Validar formato de RIF venezolano    
    Formato: J-12345678-9 o V-12345678-9
    """
    rif_pattern = r'^[JGVEPCDN]-\d{8,9}-?\d?$'
    if not re.match(rif_pattern, value.upper()):
        raise ValidationError(
            _('%(value)s no es un RIF válido. Formato: J-12345678-9'),
            params={'value': value},
        )


def validate_cedula(value):
    """
    Validar formato de Cédula venezolana    
    Formato: V-12345678 o E-12345678
    """
    cedula_pattern = r'^[VE]-?\d{6,8}$'
    if not re.match(cedula_pattern, value.upper()):
        raise ValidationError(
            _('%(value)s no es una cédula válida. Formato: V-12345678'),
            params={'value': value},
        )


def validate_phone_ve(value):
    """
    Validar formato de teléfono venezolano    
    Formato: 0414-1234567 o 0212-1234567
    """
    phone_pattern = r'^0(2\d{2}|4\d{2})-?\d{7}$'
    if not re.match(phone_pattern, value):
        raise ValidationError(
            _('%(value)s no es un teléfono válido. Formato: 0414-1234567'),
            params={'value': value},
        )


def validate_positive(value):
    """Validar que un número sea positivo"""
    if value < 0:
        raise ValidationError(
            _('%(value)s debe ser un número positivo'),
            params={'value': value},
        )


def validate_not_empty(value):
    """Validar que un string no esté vacío"""
    if not value or not value.strip():
        raise ValidationError(_('Este campo no puede estar vacío'))
