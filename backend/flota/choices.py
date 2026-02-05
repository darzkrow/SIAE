"""
Opciones para modelos de la aplicación flota.
"""
from django.db import models

class TipoVehiculoChoices(models.TextChoices):
        MOTO = 'MOTO', 'Motocicleta'
        LIVIANO = 'LIVIANO', 'Vehículo Liviano'
        PESADO = 'PESADO', 'Vehículo Pesado'
        TRANSPORTE = 'TRANSPORTE', 'Transporte de Personal'
        EMBARCACION = 'EMBARCACION', 'Embarcación'
        MAQUINARIA = 'MAQUINARIA', 'Maquinaria Pesada'
        ESPECIAL = 'ESPECIAL', 'Vehículo Especial'

class EstadoVehiculo(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        EN_USO = 'EN_USO', 'En Uso'
        ASIGNADO = 'ASIGNADO', 'Asignado Permanente'
        MANTENIMIENTO = 'MANTENIMIENTO', 'En Mantenimiento'
        REPARACION = 'REPARACION', 'En Reparación'
        RESERVADO = 'RESERVADO', 'Reservado'
        FUERA_SERVICIO = 'FUERA_SERVICIO', 'Fuera de Servicio'
        SINIESTRADO = 'SINIESTRADO', 'Siniestrado'
        BAJA = 'BAJA', 'Dado de Baja'

class TipoDocumentoVehiculo(models.TextChoices):
        REGISTRO = 'REGISTRO', 'Certificado de Registro'
        SEGURO = 'SEGURO', 'Póliza de Seguro'
        REVISION = 'REVISION', 'Revisión Técnica'
        PERMISO_CIRCULACION = 'PERMISO_CIRCULACION', 'Permiso de Circulación'
        LICENCIA_OPERACION = 'LICENCIA_OPERACION', 'Licencia de Operación'
        MATRICULA = 'MATRICULA', 'Certificado de Matrícula'
        INSPECCION = 'INSPECCION', 'Certificado de Inspección'
        FUMIGACION = 'FUMIGACION', 'Certificado de Fumigación'
        GARANTIA = 'GARANTIA', 'Certificado de Garantía'
        OTRO = 'OTRO', 'Otro Documento'
