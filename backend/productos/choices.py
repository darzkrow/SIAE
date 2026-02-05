"""
Opciones para modelos de la aplicación productos.
"""
from django.db import models

class TipoUnidad(models.TextChoices):
        LONGITUD = 'LONGITUD', 'Longitud'
        VOLUMEN = 'VOLUMEN', 'Volumen'
        PESO = 'PESO', 'Peso'
        UNIDAD = 'UNIDAD', 'Unidad'
        AREA = 'AREA', 'Área'

class TipoInventario(models.TextChoices):
        ESTRATEGICO = 'ESTRATEGICO', 'Estratégico Hídrico'
        OPERACIONAL = 'OPERACIONAL', 'Operacional'
        CONSUMIBLE = 'CONSUMIBLE', 'Consumible'
        ACTIVO_FIJO = 'ACTIVO_FIJO', 'Activo Fijo'

class NivelCriticidad(models.TextChoices):
        BAJO = 'BAJO', 'Bajo'
        MEDIO = 'MEDIO', 'Medio'
        ALTO = 'ALTO', 'Alto'
        CRITICO = 'CRITICO', 'Crítico'

class NivelPeligrosidad(models.TextChoices):
        BAJO = 'BAJO', 'Bajo'
        MEDIO = 'MEDIO', 'Medio'
        ALTO = 'ALTO', 'Alto'
        MUY_ALTO = 'MUY_ALTO', 'Muy Alto'
    
class TipoPresentacion(models.TextChoices):
        SACO = 'SACO', 'Saco'
        TAMBOR = 'TAMBOR', 'Tambor/Bidón'
        GRANEL = 'GRANEL', 'Granel'
        GALON = 'GALON', 'Galón'
        CILINDRO = 'CILINDRO', 'Cilindro'
        OTRO = 'OTRO', 'Otro'

class MaterialTuberia(models.TextChoices):
        PVC = 'PVC', 'PVC'
        PEAD = 'PEAD', 'PEAD'
        ACERO = 'ACERO', 'Acero'
        HIERRO = 'HIERRO_DUCTIL', 'Hierro Dúctil'

class TipoEquipo(models.TextChoices):
        BOMBA = 'BOMBA', 'Bomba'
        MOTOR = 'MOTOR', 'Motor'
