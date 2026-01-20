from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Modulo, Usuario, TipoTramite, Turno, Configuracion

# 1. Configuración para el USUARIO (Para que maneje passwords seguros)
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Agregamos los campos de la DGAIR al formulario de usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Datos DGAIR', {'fields': ('rol', 'modulo_default')}),
    )
    list_display = ('username', 'first_name', 'rol', 'modulo_default', 'is_active')
    list_filter = ('rol', 'is_active')

# 2. Configuración para MÓDULOS
@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'siglas', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'siglas')

# 3. Configuración para TRÁMITES
@admin.register(TipoTramite)
class TipoTramiteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'prefijo', 'prioridad', 'activo')
    list_editable = ('prioridad', 'activo')  # ¡Permite editar directo en la lista!
    ordering = ('-prioridad',)

# 4. Configuración para TURNOS
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('codigo_completo', 'estado', 'tipo_tramite', 'modulo_atencion', 'hora_creacion')
    list_filter = ('estado', 'tipo_tramite', 'fecha', 'modulo_atencion')
    search_fields = ('codigo_completo', 'nombre_ciudadano')
    readonly_fields = ('hora_creacion', 'hora_llamado', 'hora_inicio_atencion', 'hora_fin')

# 5. Configuración para CONFIGURACIÓN
@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ('clave', 'valor', 'tipo_dato')
    search_fields = ('clave',)