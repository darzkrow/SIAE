"""
Opciones para modelos de la aplicación institución.
"""
from django.db import models

class VicepresidenciaTypes(models.TextChoices):
    COMERCIALIZACION = 'COMERCIALIZACION', 'Vicepresidencia de Comercialización'
    OPERACIONES_HIDRICAS = 'OPERACIONES_HIDRICAS', 'Vicepresidencia de Operaciones Hídricas'
    ADMINISTRATIVA = 'ADMINISTRATIVA', 'Vicepresidencia Administrativa'

class TipoUnidadChoices(models.TextChoices):
        GERENCIA = 'GERENCIA', 'Gerencia'
        COORDINACION = 'COORDINACION', 'Coordinación'
        DEPARTAMENTO = 'DEPARTAMENTO', 'Departamento'
        DIVISION = 'DIVISION', 'División'
        SECCION = 'SECCION', 'Sección'
        OFICINA = 'OFICINA', 'Oficina'
        ALMACEN = 'ALMACEN', 'Almacén'
        PLANTA = 'PLANTA', 'Planta de Tratamiento'
        ESTACION = 'ESTACION', 'Estación de Bombeo'

class AlmacenPrefijos(models.TextChoices):
        ZULIA = 'ZUL', 'Zulia'
        CARABOBO = 'CAR', 'Carabobo'
        MIRANDA = 'MIR', 'Miranda'
        ARAGUA = 'ARA', 'Aragua'
        LARA = 'LAR', 'Lara'
        TACHIRA = 'TAC', 'Táchira'
        BOLIVAR = 'BOL', 'Bolívar'
        ANZOATEGUI = 'ANZ', 'Anzoátegui'
        NUEVA_ESPARTA = 'NVA', 'Nueva Esparta'
