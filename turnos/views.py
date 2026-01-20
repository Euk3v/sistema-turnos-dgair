from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .models import Turno, TipoTramite

# --- VISTAS (Páginas HTML) ---

def index(request):
    """Kiosco: Muestra los trámites reales activos"""
    tramites = TipoTramite.objects.filter(activo=True).order_by('prioridad')
    return render(request, 'turnos/index.html', {'tramites': tramites})

def pantalla(request):
    """TV Sala de Espera"""
    return render(request, 'turnos/pantalla.html')

def ventanillas(request):
    """Menú de Selección de Ventanilla"""
    return render(request, 'turnos/ventanillas.html')

def vista_operador(request, numero_ventanilla):
    """Panel de Control del Operador"""
    return render(request, 'turnos/operador_panel.html', {
        'numero_ventanilla': numero_ventanilla
    })

# --- API ENDPOINTS (Lógica del Sistema) ---

@csrf_exempt
def api_crear_turno(request):
    """Kiosco: Genera un turno nuevo"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            prefijo_tramite = data.get('tipo_tramite') 

            # 1. Buscar trámite
            tramite_obj = TipoTramite.objects.filter(prefijo=prefijo_tramite).first()
            if not tramite_obj:
                return JsonResponse({'success': False, 'error': 'Trámite no encontrado'})

            # 2. Calcular consecutivo del día
            hoy = timezone.now().date()
            ultimo_turno = Turno.objects.filter(
                fecha=hoy, 
                tipo_tramite=tramite_obj
            ).count()
            nuevo_consecutivo = ultimo_turno + 1
            
            # 3. Generar Código (Ej: REV-005)
            codigo = f"{tramite_obj.prefijo}-{nuevo_consecutivo:03d}"

            # 4. Guardar
            nuevo_turno = Turno.objects.create(
                numero_consecutivo=nuevo_consecutivo,
                codigo_completo=codigo,
                tipo_tramite=tramite_obj,
                nombre_ciudadano=nombre,
                estado='ESPERA'
            )

            return JsonResponse({
                'success': True,
                'turno': {
                    'numero': nuevo_turno.codigo_completo,
                    'nombre': nuevo_turno.nombre_ciudadano
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def api_turnos_activos(request):
    """Para la TV: Devuelve llamados, en atención y espera"""
    
    # 1. LLAMANDO (Zona Roja)
    llamando = Turno.objects.filter(estado='LLAMADO').order_by('-hora_llamado')
    
    # 2. EN ATENCIÓN (Zona Derecha) <--- ESTO ES LO QUE TE FALTABA
    en_atencion = Turno.objects.filter(estado='EN_ATENCION').order_by('-hora_inicio_atencion')
    
    # 3. ESPERA (Próximos)
    espera = Turno.objects.filter(estado='ESPERA').order_by('id')[:5]

    return JsonResponse({
        'turnos_llamando': [{
            'numero': t.codigo_completo,
            'nombre': t.nombre_ciudadano,
            'ventanilla': t.ventanilla,
            'intentos': t.intentos_llamada
        } for t in llamando],
        
        # AGREGAR ESTA SECCIÓN:
        'turnos_en_atencion': [{
            'numero': t.codigo_completo,
            'nombre': t.nombre_ciudadano,
            'ventanilla': t.ventanilla
        } for t in en_atencion],
        
        'turnos_espera': [{
            'numero': t.codigo_completo,
            'nombre': t.nombre_ciudadano
        } for t in espera]
    })


@csrf_exempt
def api_llamar_siguiente(request):
    """Operador: Botón 'Llamar Siguiente'"""
    if request.method == 'POST':
        data = json.loads(request.body)
        ventanilla = data.get('ventanilla') 
        nombre_ventanilla = f"Ventanilla {ventanilla}"

        # Buscar el siguiente en ESPERA (FIFO)
        siguiente = Turno.objects.filter(estado='ESPERA').order_by('id').first()

        if siguiente:
            siguiente.estado = 'LLAMADO'
            siguiente.ventanilla = nombre_ventanilla
            siguiente.intentos_llamada = 1 
            siguiente.hora_llamado = timezone.now()
            siguiente.save()
            
            return JsonResponse({'success': True, 'turno': {
                'id': siguiente.id,
                'numero': siguiente.codigo_completo,
                'nombre': siguiente.nombre_ciudadano,
                'intentos': 1
            }})
        else:
            return JsonResponse({'success': False, 'message': 'No hay turnos en espera'})


@csrf_exempt
def api_rellamar(request):
    """Operador: Botón 'Volver a llamar'"""
    if request.method == 'POST':
        data = json.loads(request.body)
        turno_id = data.get('turno_id')
        
        turno = get_object_or_404(Turno, id=turno_id)
        
        turno.intentos_llamada += 1
        turno.hora_llamado = timezone.now() # Actualiza hora para que suene en TV
        turno.save()
        
        return JsonResponse({'success': True, 'intentos': turno.intentos_llamada})


@csrf_exempt
def api_iniciar_atencion(request):
    """Operador: Botón 'Ciudadano Llegó'"""
    if request.method == 'POST':
        data = json.loads(request.body)
        turno_id = data.get('turno_id')
        
        turno = get_object_or_404(Turno, id=turno_id)
        turno.estado = 'EN_ATENCION' # Pasa a la lista derecha
        turno.hora_inicio_atencion = timezone.now()
        turno.save()
        
        return JsonResponse({'success': True})


@csrf_exempt
def api_finalizar_turno(request):
    """Operador: Botón 'Finalizar' o 'No Show'"""
    if request.method == 'POST':
        data = json.loads(request.body)
        turno_id = data.get('turno_id')
        tipo_fin = data.get('tipo') # 'FINALIZADO' o 'NO_SHOW'
        
        turno = get_object_or_404(Turno, id=turno_id)
        turno.estado = tipo_fin # Desaparece de TV
        turno.hora_fin_atencion = timezone.now()
        turno.save()
        
        return JsonResponse({'success': True})