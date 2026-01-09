from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.db.models import F, Q
from django.core.exceptions import ValidationError
from django.utils import timezone


class OrganizacionCentral(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    rif = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = 'Organización Central'
        verbose_name_plural = 'Organizaciones Centrales'
    def __str__(self):
        return f"{self.nombre}"

class Sucursal(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    organizacion_central = models.ForeignKey(
        OrganizacionCentral, on_delete=models.PROTECT, related_name='sucursales'
    )

    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'

    def __str__(self):
        return f"{self.nombre} ({self.organizacion_central.nombre})"


class Acueducto(models.Model):
    nombre = models.CharField(max_length=200)
    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE, related_name='acueductos'
    )

    class Meta:
        verbose_name = 'Acueducto'
        verbose_name_plural = 'Acueductos'
        unique_together = ('nombre', 'sucursal')

    def __str__(self):
        return f"{self.nombre} - {self.sucursal.nombre}"


class Categoria(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class ArticuloBase(models.Model):
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name='%(class)s_items'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.nombre


class Tuberia(ArticuloBase):
    MATERIAL_PVC = 'PVC'
    MATERIAL_HIERRO = 'HIERRO'
    MATERIAL_CEMENTO = 'CEMENTO'
    MATERIAL_OTRO = 'OTRO'

    MATERIAL_CHOICES = [
        (MATERIAL_PVC, 'PVC'),
        (MATERIAL_HIERRO, 'Hierro Dúctil'),
        (MATERIAL_CEMENTO, 'Cemento'),
        (MATERIAL_OTRO, 'Otro'),
    ]

    USO_POTABLE = 'POTABLE'
    USO_SERVIDAS = 'SERVIDAS'
    USO_RIEGO = 'RIEGO'

    USO_CHOICES = [
        (USO_POTABLE, 'Aguas Potables'),
        (USO_SERVIDAS, 'Aguas Servidas'),
        (USO_RIEGO, 'Riego'),
    ]

    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    tipo_uso = models.CharField(max_length=20, choices=USO_CHOICES)
    diametro_nominal_mm = models.IntegerField()
    longitud_m = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Tubería'
        verbose_name_plural = 'Tuberías'


class Equipo(ArticuloBase):
    marca = models.CharField(max_length=150, blank=True)
    modelo = models.CharField(max_length=150, blank=True)
    potencia_hp = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    numero_serie = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
class StockTuberia(models.Model):
    tuberia = models.ForeignKey(Tuberia, on_delete=models.CASCADE, related_name='stocks')
    acueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE, related_name='stocks_tuberia')
    cantidad = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock Tubería'
        verbose_name_plural = 'Stocks Tuberías'
        unique_together = ('tuberia', 'acueducto')
        # constraints commented out due to reported migration error in user environment
        # constraints = [
        #     models.CheckConstraint(check=Q(cantidad__gte=0), name='stock_tuberia_cantidad_gte_0'),
        # ]

    def __str__(self):
        return f"{self.tuberia} @ {self.acueducto}: {self.cantidad}"

    def save(self, *args, **kwargs):
        if self.cantidad < 0:
            raise ValidationError('La cantidad de stock no puede ser negativa')
        return super().save(*args, **kwargs)


class StockEquipo(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='stocks')
    acueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE, related_name='stocks_equipo')
    cantidad = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock Equipo'
        verbose_name_plural = 'Stocks Equipos'
        unique_together = ('equipo', 'acueducto')
        # constraints = [
        #     models.CheckConstraint(check=Q(cantidad__gte=0), name='stock_equipo_cantidad_gte_0'),
        # ]

    def __str__(self):
        return f"{self.equipo} @ {self.acueducto}: {self.cantidad}"

    def save(self, *args, **kwargs):
        if self.cantidad < 0:
            raise ValidationError('La cantidad de stock no puede ser negativa')
        return super().save(*args, **kwargs)


class InventoryAudit(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_SUCCESS = 'SUCCESS'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_SUCCESS, 'Exitoso'),
        (STATUS_FAILED, 'Fallido'),
    ]

    movimiento = models.ForeignKey('MovimientoInventario', on_delete=models.SET_NULL, null=True, blank=True, related_name='audits')
    articulo_tipo = models.CharField(max_length=20, choices=[('TUBERIA', 'Tubería'), ('EQUIPO', 'Equipo')], blank=True)
    articulo_nombre = models.CharField(max_length=250, blank=True)
    tipo_movimiento = models.CharField(max_length=20, blank=True)
    cantidad = models.IntegerField(null=True, blank=True)
    acueducto_origen = models.ForeignKey(Acueducto, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    acueducto_destino = models.ForeignKey(Acueducto, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    mensaje = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Auditoría de Inventario'
        verbose_name_plural = 'Auditorías de Inventario'

    def __str__(self):
        return f"[{self.status}] {self.tipo_movimiento} {self.articulo_nombre or ''} ({self.fecha})"


class AlertaStock(models.Model):
    """Define un umbral para un artículo en un acueducto concreto.
    Exactly one of `tuberia` or `equipo` must be set.
    """
    tuberia = models.ForeignKey(Tuberia, on_delete=models.CASCADE, null=True, blank=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=True, blank=True)
    acueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE, related_name='alertas')
    umbral_minimo = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Alerta de Stock'
        verbose_name_plural = 'Alertas de Stock'

    def clean(self):
        if bool(self.tuberia) == bool(self.equipo):
            raise ValidationError('Debe especificar exactamente un artículo: tuberia o equipo en la alerta')

    def __str__(self):
        nombre = str(self.tuberia) if self.tuberia else str(self.equipo)
        return f"Alerta {nombre} @ {self.acueducto} <= {self.umbral_minimo}"


class Notification(models.Model):
    alerta = models.ForeignKey(AlertaStock, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    mensaje = models.TextField()
    creada_en = models.DateTimeField(auto_now_add=True)
    enviada = models.BooleanField(default=False)
    enviada_en = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def mark_sent(self):
        self.enviada = True
        self.enviada_en = timezone.now()
        self.save()



class MovimientoInventario(models.Model):
    T_ENTRADA = 'ENTRADA'
    T_SALIDA = 'SALIDA'
    T_TRANSFER = 'TRANSFERENCIA'
    T_AJUSTE = 'AJUSTE'

    TIPO_CHOICES = [
        (T_ENTRADA, 'Entrada'),
        (T_SALIDA, 'Salida'),
        (T_TRANSFER, 'Transferencia'),
        (T_AJUSTE, 'Ajuste'),
    ]

    tuberia = models.ForeignKey(Tuberia, on_delete=models.SET_NULL, null=True, blank=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, blank=True)

    acueducto_origen = models.ForeignKey(
        Acueducto, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_salida'
    )
    acueducto_destino = models.ForeignKey(
        Acueducto, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_entrada'
    )

    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    razon = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'

    def __str__(self):
        articulo = self.get_articulo_display_name()
        return f"{self.tipo_movimiento} {self.cantidad} of {articulo} on {self.fecha_movimiento.date()}"

    def get_articulo(self):
        return self.tuberia or self.equipo

    def get_articulo_display_name(self):
        a = self.get_articulo()
        return str(a) if a else '—'

    def _process_movement(self, StockModel, item_field, item):
        """
        Maneja la lógica de actualización de stock de forma agnóstica al tipo de artículo.
        
        Para TRANSFERENCIA:
        - Si es entre diferentes sucursales: Disminuye origen, aumenta destino
        - Si es dentro de la misma sucursal (diferente acueducto): Solo cambia ubicación, mantiene total
        """
        def get_stock(acueducto, create=False):
            if create:
                obj, _ = StockModel.objects.get_or_create(
                    acueducto=acueducto,
                    **{item_field: item},
                    defaults={'cantidad': 0}
                )
                # Retornamos el objeto bloqueado para lectura/escritura si es necesario
                return StockModel.objects.select_for_update().get(pk=obj.pk)
            else:
                return StockModel.objects.select_for_update().get(
                    acueducto=acueducto,
                    **{item_field: item}
                )

        if self.tipo_movimiento == self.T_ENTRADA:
            if not self.acueducto_destino:
                raise ValidationError('acueducto_destino requerido para ENTRADA')
            
            stock = get_stock(self.acueducto_destino, create=True)
            StockModel.objects.filter(pk=stock.pk).update(cantidad=F('cantidad') + self.cantidad)

        elif self.tipo_movimiento == self.T_SALIDA:
            if not self.acueducto_origen:
                raise ValidationError('acueducto_origen requerido para SALIDA')
            
            try:
                stock = get_stock(self.acueducto_origen)
            except StockModel.DoesNotExist:
                raise ValidationError(f'Stock inexistente en origen para {item}')
            
            if stock.cantidad < self.cantidad:
                raise ValidationError('Stock insuficiente en origen para realizar la salida')
            
            StockModel.objects.filter(pk=stock.pk).update(cantidad=F('cantidad') - self.cantidad)

        elif self.tipo_movimiento == self.T_TRANSFER:
            if not self.acueducto_origen or not self.acueducto_destino:
                raise ValidationError('acueducto_origen y acueducto_destino son requeridos para TRANSFER')

            # Check if transfer is within same sucursal or between different sucursales
            same_sucursal = self.acueducto_origen.sucursal_id == self.acueducto_destino.sucursal_id

            if same_sucursal:
                # Transferencia dentro de la misma sucursal: solo cambiar ubicación, mantener total
                # Origen: disminuir
                try:
                    stock_orig = get_stock(self.acueducto_origen)
                except StockModel.DoesNotExist:
                    raise ValidationError('Stock inexistente en origen para transferencia')
                
                if stock_orig.cantidad < self.cantidad:
                    raise ValidationError('Stock insuficiente en origen para la transferencia')
                
                StockModel.objects.filter(pk=stock_orig.pk).update(cantidad=F('cantidad') - self.cantidad)

                # Destino: aumentar (mismo total, solo cambio de ubicación)
                stock_dest = get_stock(self.acueducto_destino, create=True)
                StockModel.objects.filter(pk=stock_dest.pk).update(cantidad=F('cantidad') + self.cantidad)
            else:
                # Transferencia entre sucursales: disminuir origen, aumentar destino (comportamiento normal)
                # Origen
                try:
                    stock_orig = get_stock(self.acueducto_origen)
                except StockModel.DoesNotExist:
                    raise ValidationError('Stock inexistente en origen para transferencia')
                
                if stock_orig.cantidad < self.cantidad:
                    raise ValidationError('Stock insuficiente en origen para la transferencia')
                
                StockModel.objects.filter(pk=stock_orig.pk).update(cantidad=F('cantidad') - self.cantidad)

                # Destino
                stock_dest = get_stock(self.acueducto_destino, create=True)
                StockModel.objects.filter(pk=stock_dest.pk).update(cantidad=F('cantidad') + self.cantidad)

        elif self.tipo_movimiento == self.T_AJUSTE:
            # Nota: AJUSTE actualmente solo suma stock (comportamiento original).
            if self.acueducto_destino:
                stock = get_stock(self.acueducto_destino, create=True)
                StockModel.objects.filter(pk=stock.pk).update(cantidad=F('cantidad') + self.cantidad)
            elif self.acueducto_origen:
                stock = get_stock(self.acueducto_origen, create=True)
                StockModel.objects.filter(pk=stock.pk).update(cantidad=F('cantidad') + self.cantidad)

    def save(self, *args, **kwargs):
        # Validate: exactly one of tuberia/equipo should be set
        if bool(self.tuberia) == bool(self.equipo):
            # Create audit record for failure (without movimiento FK)
            InventoryAudit.objects.create(
                articulo_tipo='TUBERIA' if self.tuberia else ('EQUIPO' if self.equipo else ''),
                articulo_nombre=(str(self.tuberia) if self.tuberia else (str(self.equipo) if self.equipo else '')),
                tipo_movimiento=self.tipo_movimiento or '',
                cantidad=self.cantidad,
                acueducto_origen=self.acueducto_origen,
                acueducto_destino=self.acueducto_destino,
                status=InventoryAudit.STATUS_FAILED,
                mensaje='Debe especificar exactamente un artículo: tuberia o equipo'
            )
            raise ValidationError('Debe especificar exactamente un artículo: tuberia o equipo')

        # Configuración dinámica según el tipo de artículo
        if self.tuberia:
            item = self.tuberia
            StockModel = StockTuberia
            item_field = 'tuberia'
            audit_type = 'TUBERIA'
        else:
            item = self.equipo
            StockModel = StockEquipo
            item_field = 'equipo'
            audit_type = 'EQUIPO'

        with transaction.atomic():
            super().save(*args, **kwargs)

            # create pending audit linked to this movimiento
            audit = InventoryAudit.objects.create(
                movimiento=self,
                articulo_tipo=audit_type,
                articulo_nombre=str(item),
                tipo_movimiento=self.tipo_movimiento,
                cantidad=self.cantidad,
                acueducto_origen=self.acueducto_origen,
                acueducto_destino=self.acueducto_destino,
                status=InventoryAudit.STATUS_PENDING,
            )

            try:
                self._process_movement(StockModel, item_field, item)
                audit.status = InventoryAudit.STATUS_SUCCESS
                audit.save()
            except ValidationError as e:
                audit.status = InventoryAudit.STATUS_FAILED
                audit.mensaje = str(e.message) if hasattr(e, 'message') else str(e)
                audit.save()
                raise e
