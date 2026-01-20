from django.urls import path
from . import views

urlpatterns = [
    # --- VISTAS HTML ---
    path('', views.index, name='index'),
    path('pantalla/', views.pantalla, name='pantalla'),
    path('ventanillas/', views.ventanillas, name='ventanillas'),
    path('operador/<int:numero_ventanilla>/', views.vista_operador, name='vista_operador'),

    # --- API ENDPOINTS (LÓGICA) ---
    path('api/turnos/crear/', views.api_crear_turno, name='api_crear_turno'),
    path('api/turnos/activos/', views.api_turnos_activos, name='api_turnos_activos'),
    
    # Aquí estaba el error de nombre (api_llamar_turno -> api_llamar_siguiente)
    path('api/turnos/llamar/', views.api_llamar_siguiente, name='api_llamar'), 
    
    path('api/turnos/rellamar/', views.api_rellamar, name='api_rellamar'),
    path('api/turnos/atencion/', views.api_iniciar_atencion, name='api_atencion'),
    path('api/turnos/finalizar/', views.api_finalizar_turno, name='api_finalizar'),
]