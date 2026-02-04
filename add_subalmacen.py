"""
Script para agregar modelo Subalmacén y campos QR a institucion/models.py
"""

import re

# Leer el archivo models.py
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Agregar import de geography models después de los imports existentes
geography_import = "from geography.models import State, Municipality, Parish\n"

# Buscar la línea "User = get_user_model()"
if "from geography.models import State" not in content:
    content = content.replace(
        "from core.models import TimeStampedModel\n",
        "from core.models import TimeStampedModel\n" + geography_import
    )

# 2. Agregar modelo Subalmacén antes del modelo Acueducto
subalmacen_model = '''

# ============================================================================
# SUBALMACÉN MODEL (Nuevo - Reemplaza Acueducto)
# ============================================================================

class Subalmacen(TimeStampedModel):
    """
    Subalmacén con ubicación geográfica.
    Reemplaza el modelo Acueducto con capacidades geográficas mejoradas.
    """
    nombre = models.CharField(max_length=200, help_text='Nombre del subalmacén')
    codigo = models.CharField(max_length=20, unique=True, help_text='Código único (ej: SUB-ZUL-001)')
    
    sucursal = models.ForeignKey(
        'Sucursal',
        on_delete=models.CASCADE,
        related_name='subalmacenes',
        help_text='Sucursal a la que pertenece'
    )
    
    # Ubicación geográfica
    estado = models.ForeignKey(State, on_delete=models.PROTECT, related_name='subalmacenes')
    municipio = models.ForeignKey(Municipality, on_delete=models.PROTECT, related_name='subalmacenes', null=True, blank=True)
    parroquia = models.ForeignKey(Parish, on_delete=models.PROTECT, related_name='subalmacenes', null=True, blank=True)
    
    direccion = models.TextField(blank=True, help_text='Dirección completa')
    coordenadas_gps = models.CharField(max_length=100, blank=True, help_text='Coordenadas GPS (lat,lng)')
    
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subalmacenes_responsable')
    capacidad = models.IntegerField(null=True, blank=True, help_text='Capacidad de almacenamiento')
    activo = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Subalmacén'
        verbose_name_plural = 'Subalmacenes'
        unique_together = ('nombre', 'sucursal')
        ordering = ['estado__name', 'sucursal__nombre', 'nombre']
        indexes = [
            models.Index(fields=['estado', 'activo']),
            models.Index(fields=['sucursal', 'activo']),
            models.Index(fields=['codigo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.estado.name})"
    
    def get_ubicacion_completa(self):
        partes = [self.estado.name]
        if self.municipio:
            partes.append(self.municipio.name)
        if self.parroquia:
            partes.append(self.parroquia.name)
        return ", ".join(partes)
    
    def es_responsable(self, user):
        return self.responsable == user or user.is_staff


# ============================================================================
# LEGACY MODELS (Backward Compatibility)
# ============================================================================

'''

# Insertar antes de "class Acueducto(models.Model):"
if "class Subalmacen(TimeStampedModel):" not in content:
    content = content.replace(
        "class Acueducto(models.Model):",
        subalmacen_model + "class Acueducto(models.Model):"
    )

# 3. Agregar campos QR a SolicitudTraslado
# Buscar el final de los campos de SolicitudTraslado (antes de class Meta)
qr_fields = '''
    
    # 🆕 Campos para QR Code
    qr_code = models.ImageField(
        upload_to='qr_codes/traslados/',
        blank=True,
        null=True,
        help_text='Código QR para aprobación rápida'
    )
    qr_url = models.URLField(
        blank=True,
        help_text='URL de aprobación contenida en el QR'
    )
    qr_generado_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de generación del QR'
    )
'''

# Buscar la clase SolicitudTraslado y agregar campos antes de class Meta
if "qr_code = models.ImageField" not in content:
    # Buscar el patrón de observaciones en SolicitudTraslado
    pattern = r"(class SolicitudTraslado\(models\.Model\):.*?observaciones = models\.TextField\([^)]+\))"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content.replace(
            match.group(0),
            match.group(0) + qr_fields
        )

# Guardar el archivo modificado
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Modelo Subalmacén agregado exitosamente")
print("✅ Campos QR agregados a SolicitudTraslado")
print("✅ Import de geography models agregado")
