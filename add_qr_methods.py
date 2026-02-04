"""
Script para agregar métodos de generación de QR a SolicitudTraslado
"""

import re

# Leer el archivo models.py
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Agregar imports necesarios para QR
qr_imports = """import qrcode
from io import BytesIO
from django.core.files import File
from django.urls import reverse
"""

# Agregar imports después de los imports existentes
if "import qrcode" not in content:
    # Buscar la última línea de import
    content = content.replace(
        "from geography.models import State, Municipality, Parish\n",
        "from geography.models import State, Municipality, Parish\n" + qr_imports
    )

# Métodos para generar QR
qr_methods = '''
    
    def generar_qr_code(self, request=None):
        """
        Genera código QR con URL de aprobación.
        """
        from django.contrib.sites.models import Site
        
        # Construir URL de aprobación
        if request:
            domain = request.get_host()
            protocol = 'https' if request.is_secure() else 'http'
        else:
            try:
                site = Site.objects.get_current()
                domain = site.domain
                protocol = 'https'
            except:
                domain = 'localhost:8000'
                protocol = 'http'
        
        # URL de aprobación
        approval_path = f'/api/institucion/solicitudes-traslado/{self.pk}/aprobar/'
        self.qr_url = f"{protocol}://{domain}{approval_path}"
        
        # Generar QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qr_url)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar en campo ImageField
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'solicitud_{self.numero_solicitud}_qr.png'
        self.qr_code.save(filename, File(buffer), save=False)
        
        # Actualizar fecha de generación
        from django.utils import timezone
        self.qr_generado_en = timezone.now()
        
        self.save()
        return self.qr_code
'''

# Buscar el método __str__ de SolicitudTraslado y agregar después
if "def generar_qr_code(self, request=None):" not in content:
    # Buscar la clase SolicitudTraslado y su método __str__
    pattern = r"(class SolicitudTraslado\(models\.Model\):.*?def __str__\(self\):.*?return f.*?\n)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content.replace(
            match.group(0),
            match.group(0) + qr_methods
        )

# Guardar el archivo modificado
with open(r'c:\Users\gfranco\Desktop\SIAE\backend\institucion\models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Imports de QR agregados")
print("✅ Método generar_qr_code() agregado a SolicitudTraslado")
