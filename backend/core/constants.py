
# Estados Comunes
ESTADO_ACTIVO = 'activo'
ESTADO_INACTIVO = 'inactivo'
ESTADO_PENDIENTE = 'pendiente'
ESTADO_APROBADO = 'aprobado'
ESTADO_RECHAZADO = 'rechazado'
ESTADO_CANCELADO = 'cancelado'

ESTADOS_CHOICES = [
    (ESTADO_ACTIVO, 'Activo'),
    (ESTADO_INACTIVO, 'Inactivo'),
    (ESTADO_PENDIENTE, 'Pendiente'),
    (ESTADO_APROBADO, 'Aprobado'),
    (ESTADO_RECHAZADO, 'Rechazado'),
    (ESTADO_CANCELADO, 'Cancelado'),
]

# Tipos de Documentos
TIPO_DOC_RIF = 'RIF'
TIPO_DOC_CEDULA = 'CEDULA'
TIPO_DOC_PASAPORTE = 'PASAPORTE'

TIPOS_DOCUMENTO_CHOICES = [
    (TIPO_DOC_RIF, 'RIF'),
    (TIPO_DOC_CEDULA, 'Cédula'),
    (TIPO_DOC_PASAPORTE, 'Pasaporte'),
]

# Monedas
MONEDA_BS = 'BS'
MONEDA_USD = 'USD'
MONEDA_EUR = 'EUR'

MONEDAS_CHOICES = [
    (MONEDA_BS, 'Bolívares'),
    (MONEDA_USD, 'Dólares'),
    (MONEDA_EUR, 'Euros'),
]

# Configuración de Paginación
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Formatos de Fecha
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT = '%H:%M:%S'

# Niveles de Riesgo (Auditoría)
RIESGO_BAJO = 'bajo'
RIESGO_MEDIO = 'medio'
RIESGO_ALTO = 'alto'
RIESGO_CRITICO = 'critico'

NIVELES_RIESGO_CHOICES = [
    (RIESGO_BAJO, 'Bajo'),
    (RIESGO_MEDIO, 'Medio'),
    (RIESGO_ALTO, 'Alto'),
    (RIESGO_CRITICO, 'Crítico'),
]

# Acciones de Auditoría
ACCION_CREAR = 'crear'
ACCION_ACTUALIZAR = 'actualizar'
ACCION_ELIMINAR = 'eliminar'
ACCION_LEER = 'leer'

ACCIONES_AUDITORIA_CHOICES = [
    (ACCION_CREAR, 'Crear'),
    (ACCION_ACTUALIZAR, 'Actualizar'),
    (ACCION_ELIMINAR, 'Eliminar'),
    (ACCION_LEER, 'Leer'),
]
