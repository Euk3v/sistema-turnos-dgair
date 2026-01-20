from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# 1. ENTIDAD: MODULO (Ventanilla)
class Modulo(models.Model):
    nombre = models.CharField(max_length=50, help_text="Ej: Ventanilla 1")
    siglas = models.CharField(max_length=10, unique=True, help_text="Ej: V-01")
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.siglas})"

    class Meta:
        verbose_name = "Módulo / Ventanilla"
        verbose_name_plural = "Módulos y Ventanillas"

# 2. ENTIDAD: USUARIO (Extendido)
class Usuario(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('OPERADOR', 'Operador de Ventanilla'),
        ('SUPERVISOR', 'Supervisor'),
        ('PANTALLA', 'Pantalla de Turnos'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='OPERADOR')
    modulo_default = models.ForeignKey(
        Modulo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='operadores_asignados'
    )

    class Meta:
        verbose_name = "Usuario del Sistema"
        verbose_name_plural = "Usuarios"

# 3. ENTIDAD: TIPO DE TRAMITE
class TipoTramite(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Revalidación")
    prefijo = models.CharField(max_length=5, unique=True, help_text="Ej: REV")
    prioridad = models.IntegerField(default=1)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} [{self.prefijo}]"

    class Meta:
        verbose_name = "Tipo de Trámite"
        verbose_name_plural = "Catálogo de Trámites"

# 4. ENTIDAD: TURNO
class Turno(models.Model):
    # Opciones de Estado Actualizadas según tu lógica
    ESTADOS = [
        ('ESPERA', 'En Espera'),
        ('LLAMADO', 'Llamando por Altavoz'),
        ('EN_ATENCION', 'En Atención en Ventanilla'), # Antes "Historial"
        ('FINALIZADO', 'Finalizado'),
        ('NO_SHOW', 'No se presentó'),
    ]

    fecha = models.DateField(default=timezone.now, db_index=True)
    numero_consecutivo = models.IntegerField()
    codigo_completo = models.CharField(max_length=20, db_index=True)
    tipo_tramite = models.ForeignKey(TipoTramite, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ESPERA', db_index=True)
    usuario_operador = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True)
    modulo_atencion = models.ForeignKey(Modulo, on_delete=models.PROTECT, null=True, blank=True)
    nombre_ciudadano = models.CharField(max_length=150, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ESPERA')
    ventanilla = models.CharField(max_length=50, blank=True, null=True) # Ej: "Ventanilla 1"
    
    # Timestamps
    hora_creacion = models.DateTimeField(auto_now_add=True)
    hora_llamado = models.DateTimeField(null=True, blank=True)
    hora_inicio_atencion = models.DateTimeField(null=True, blank=True)
    hora_fin = models.DateTimeField(null=True, blank=True)
    intentos_llamada = models.IntegerField(default=0) # Para contar las 3 veces
    hora_inicio_atencion = models.DateTimeField(null=True, blank=True)
    hora_fin_atencion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.codigo_completo} - {self.get_estado_display()}"

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Gestión de Turnos"

# 5. ENTIDAD: CONFIGURACION
class Configuracion(models.Model):
    clave = models.CharField(max_length=50, unique=True)
    valor = models.CharField(max_length=255)
    tipo_dato = models.CharField(max_length=20, default='TEXTO')
    
    def __str__(self):
        return f"{self.clave}: {self.valor}"

    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuraciones"

