from django.http import StreamingHttpResponse, JsonResponse
from django.views.generic import DetailView
from django.shortcuts import redirect, render
import numpy as np
from .models import *
from django.utils.timezone import now
from app.security.models import Dashboard
from .recognition import inference_classifier2 
from django.shortcuts import get_object_or_404
from django.urls import reverse  # Importa reverse para construir URLs dinámicamente
import cv2
import time
import logging
import traceback

logger = logging.getLogger(__name__)

#*********************Configuración de la Cámara*********************

camera = None

#Función para abrir la cámara
def abrir_camara():
    global camera
    intentos = 0
    max_intentos = 3
    while intentos < max_intentos:
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0) 
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if camera.isOpened():
            logger.info("Cámara abierta correctamente.")
            return True  
        else:
            logger.error(f"Intento {intentos + 1} de abrir la cámara fallido.")
            intentos += 1
    logger.error("No se pudo abrir la cámara después de varios intentos.")
    return False

#Función para cerrar la cámara
def cerrar_camara():
    global camera
    if camera is not None:
        camera.release()
        camera = None
        logger.info("Cámara cerrada correctamente.")

#Función para obtener el último frame de la cámara
def obtener_frame():
    global camera
    if camera is not None and camera.isOpened():
        ret, frame = camera.read()
        if ret:
            return frame
        else:
            logger.error("No se pudo leer el frame de la cámara.")
            return None
    else:
        logger.error("La cámara no está disponible.")
        return None


#*******************Generador para capturar frames de la cámara y hacer predicciones*******************
# Generador para capturar los frames y hacer predicciones
def gen(tipo_modelo):
    global camera
    if not abrir_camara(): 
        return  
    try:
        while True:
            frame = obtener_frame() 
            if frame is None:
                break  
            time.sleep(0.01)

            # Elegir el modelo y etiquetas según el tipo_modelo
            if tipo_modelo == 'alfabeto':
                model = inference_classifier2.model_alfabeto
                labels_dict = inference_classifier2.labels_dict_alfabeto
            elif tipo_modelo == 'numeros':
                model = inference_classifier2.model_numeros
                labels_dict = inference_classifier2.labels_dict_numeros
            elif tipo_modelo == 'colores':
                model = inference_classifier2.model_colores
                labels_dict = inference_classifier2.labels_dict_colores

            # Realizar predicción y dibujar el recuadro
            predicted_sign = inference_classifier2.predict_sign(frame, model, labels_dict, tipo_modelo)

            if predicted_sign:
                # Mostrar la señal predicha en el frame
                cv2.putText(frame, f"{predicted_sign}", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            # Convertir el frame a formato JPEG y enviarlo al navegador
            _, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    except Exception as e:
        logger.error(f"Error en el bucle de captura de frames: {e}")
    finally:
        cerrar_camara()

#**************Vista para transmitir el video según el tipo de modelo**************
def video_feed(request, tipo_modelo):
    response = StreamingHttpResponse(gen(tipo_modelo), content_type='multipart/x-mixed-replace; boundary=frame')
    response['Cache-Control'] = 'no-cache'
    return response

#*******Función para detectar una seña dependiendo del tipo de lección*******
def detectar_senal(request):
    tipo_leccion = request.POST.get('tipo_leccion')

    if not tipo_leccion:
        return JsonResponse({'status': 'error', 'mensaje': 'El tipo de lección no fue enviado.'})

    if tipo_leccion == 'alfabeto':
        model = inference_classifier2.model_alfabeto
        labels_dict = inference_classifier2.labels_dict_alfabeto
    elif tipo_leccion == 'numeros':
        model = inference_classifier2.model_numeros
        labels_dict = inference_classifier2.labels_dict_numeros
    elif tipo_leccion == 'colores':
        model = inference_classifier2.model_colores
        labels_dict = inference_classifier2.labels_dict_colores
    else:
        return JsonResponse({'status': 'error', 'mensaje': 'Tipo de lección no válido.'})

    frame = obtener_frame()

    if frame is None:
        return JsonResponse({'status': 'error', 'mensaje': 'No se pudo capturar la imagen'})

    # Realizar predicción
    predicted_sign = inference_classifier2.predict_sign(frame, model, labels_dict, tipo_leccion)

    # Asegurarse de que la predicción es del tipo correcto
    if isinstance(predicted_sign, np.ndarray):
        predicted_sign = predicted_sign.tolist()  # Convertir ndarray a lista si es necesario

    if isinstance(predicted_sign, str):
        return JsonResponse({'status': 'success', 'senal_detectada': predicted_sign})
    else:
        return JsonResponse({'status': 'error', 'mensaje': 'Predicción no válida.'}) 

#***************Vista para mostrar el detalle de una lección y su contenido***************

class LeccionDetailView(DetailView):
    model = Leccion
    context_object_name = 'leccion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title1"] = self.object.name
        tipo_leccion = self.object.nivel.name.lower()
        #print(f"Tipo de lección: {tipo_leccion}") 
        context["tipo_leccion"] = tipo_leccion
        return context

    #Define la plantilla según el tipo de lección
    def get_template_names(self):
        tipo_leccion = self.object.nivel.name.lower()  #Obtener el tipo de lección
        if tipo_leccion == 'alfabeto':
            return ['core/lecciones/alfabeto.html']  
        elif tipo_leccion == 'numeros':
            return ['core/lecciones/numeros.html'] 
        elif tipo_leccion == 'colores':
            return ['core/lecciones/colores.html'] 
        else:
            return ['core/lecciones/detail.html']  # Plantilla predeterminada 


def feedback_nivel(request, nivel_id):
    nivel = get_object_or_404(Nivel, id=nivel_id)
    usuario = request.user

    # Verificar si el nivel fue completado para permitir el acceso al feedback
    progreso = Progreso.objects.filter(usuario=usuario, nivel=nivel).first()

    if not progreso or not progreso.completado:
        # Si el nivel no está completado, bloquear el acceso al feedback
        return JsonResponse({'status': 'error', 'mensaje': 'Debes completar el nivel antes de acceder al feedback.'})

    # Obtener el feedback si existe
    feedback = Feedback.objects.filter(usuario=usuario, nivel=nivel).first()

    return render(request, 'core/lecciones/feedback.html', {'feedback': feedback, 'nivel': nivel})


#***********************Vista específica para manejar la lección de alfabeto***********************

def alfabeto(request):
    abecedario = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    letra_actual = request.session.get('letra_actual', 'A')

    alfabeto = Nivel.objects.get(orden=1)
    progreso, creado = Progreso.objects.get_or_create(usuario=request.user, nivel=alfabeto)

    # Verificar si el usuario ya completó el nivel
    if progreso.completado:
        # Redirigir al feedback si el nivel ya está completado
        return JsonResponse({
            'status': 'completado',
            'mensaje': 'Ya completaste el Nivel 1. Puedes dirigirte al feedback.',
            'redirigir': '/feedback/'
        })

    try:
        senal_inicial = Senal.objects.get(name=letra_actual)
        senal_detectada = senal_inicial.imagen.url
        logger.info(f"Imagen encontrada para la letra {letra_actual}: {senal_detectada}")
    except Senal.DoesNotExist:
        senal_detectada = None
        logger.error(f"No se encontró imagen para la letra {letra_actual}")

    if request.method == 'GET':
        return render(request, 'alfabeto.html', {'senal_detectada': senal_detectada, 'letra_actual': letra_actual, 'progreso': progreso})

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        senal_realizada = request.POST.get('senal_realizada')
        logger.info(f"Seña realizada: {senal_realizada}, letra actual: {letra_actual}")

        if senal_realizada == letra_actual:
            indice_actual = abecedario.index(letra_actual)

            if letra_actual == 'Z':
                # Marcar el progreso del nivel como completado
                progreso.completado = True
                progreso.fecha_completado = now()
                progreso.save()

                # Desbloquear el siguiente nivel
                try:
                    siguiente_nivel = Nivel.objects.get(orden=alfabeto.orden + 1)
                    primera_leccion_siguiente_nivel = Leccion.objects.filter(nivel=siguiente_nivel).first()
                    if not primera_leccion_siguiente_nivel:
                        return JsonResponse({
                            'status': 'error',
                            'mensaje': 'El siguiente nivel no tiene una lección asociada.'
                        })

                    Progreso.objects.get_or_create(
                        usuario=request.user,
                        nivel=siguiente_nivel,
                        defaults={'desbloqueado': True, 'leccion': primera_leccion_siguiente_nivel}
                    )
                except Nivel.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'mensaje': 'No se pudo encontrar el siguiente nivel.'
                    })

                # Actualizar el dashboard del usuario
                try:
                    dashboard, created = Dashboard.objects.get_or_create(usuario=request.user)
                    dashboard.nivel_actual = siguiente_nivel
                    dashboard.actualizar_dashboard()
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'mensaje': f'Error al actualizar el dashboard: {str(e)}'
                    })

                # Redirigir a la página de niveles donde se mostrará el feedback desbloqueado
                return JsonResponse({
                    'status': 'success',
                    'mensaje': '¡Felicidades! Ha completado el Nivel 1. ¡Prepárese para el siguiente nivel!',
                    'completado': True,
                    'redirigir': '/levels/'  # Redirigir al listado de niveles
                })

            if indice_actual < len(abecedario) - 1:
                letra_actual = abecedario[indice_actual + 1]
            request.session['letra_actual'] = letra_actual

            try:
                senal_inicial = Senal.objects.get(name=letra_actual)
                nueva_imagen = senal_inicial.imagen.url
                logger.info(f"Nueva imagen encontrada para la letra {letra_actual}: {nueva_imagen}")
            except Senal.DoesNotExist:
                nueva_imagen = None
                logger.error(f"No se encontró imagen para la letra {letra_actual}")

            return JsonResponse({
                'status': 'success',
                'nueva_letra': letra_actual,
                'nueva_imagen': nueva_imagen,
                'mensaje': '¡Seña correcta! Presiona el botón para continuar con la siguiente letra.',
                'completado': False 
            })

        return JsonResponse({'status': 'error', 'mensaje': 'Seña incorrecta, inténtalo de nuevo.'})

#*************************Vista específica para manejar la lección de números*************************
def numeros(request):
    lista_numeros = list(range(10))
    numero_actual = request.session.get('numero_actual', 8)
    
    numeros = Nivel.objects.get(orden=2)
    progreso = Progreso.objects.filter(usuario=request.user, nivel=numeros).first()

    try:
        senal_inicial = Senal.objects.get(name=str(numero_actual))
        senal_detectada = senal_inicial.imagen.url
        logger.info(f"Imagen encontrada para el número {numero_actual}")
    except Senal.DoesNotExist:
        senal_detectada = None
        logger.error(f"No se encontró la imagen para el número: {numero_actual}")

    if request.method == 'GET':
        return render(request, 'numeros.html', {'senal_detectada': senal_detectada, 'numero_actual': numero_actual})
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        senal_realizada = request.POST.get('senal_realizada')
        logger.info(f"Seña realizada: {senal_realizada} (tipo: {type(senal_realizada)}), número actual: {numero_actual} (str: {str(numero_actual)}, tipo: {type(numero_actual)})")

        if str(senal_realizada).strip() == str(numero_actual).strip():
            
            if numero_actual == 9:
                progreso, creado = Progreso.objects.get_or_create(usuario=request.user, nivel=numeros)
                progreso.completado = True
                progreso.fecha_completado = now()
                progreso.save()

                # Desbloquear el siguiente nivel
                try:
                    siguiente_nivel = Nivel.objects.get(orden=numeros.orden + 1)
                    segunda_leccion_siguiente_nivel = Leccion.objects.filter(nivel=siguiente_nivel).first()
                    if not segunda_leccion_siguiente_nivel:
                        return JsonResponse({
                            'status': 'error',
                            'mensaje': 'El siguiente nivel no tiene una lección asociada.'
                        })

                    Progreso.objects.get_or_create(
                        usuario=request.user,
                        nivel=siguiente_nivel,
                        defaults={'desbloqueado': True, 'leccion': segunda_leccion_siguiente_nivel}
                    )
                except Nivel.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'mensaje': 'No se pudo encontrar el siguiente nivel.'
                    })

                # Actualizar el dashboard del usuario
                try:
                    dashboard, created = Dashboard.objects.get_or_create(usuario=request.user)
                    dashboard.nivel_actual = siguiente_nivel
                    dashboard.actualizar_dashboard()
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'mensaje': f'Error al actualizar el dashboard: {str(e)}'
                    })

                return JsonResponse({
                    'status': 'success',
                    'mensaje': '¡Felicidades! Ha completado el Nivel 2. ¡Prepárese para el siguiente nivel!',
                    'completado': True,
                    'redirigir': '/levels/'
                })
                
            try:
                indice_actual = lista_numeros.index(int(numero_actual))
                if indice_actual < len(lista_numeros) - 1:
                    numero_actual = lista_numeros[indice_actual + 1]
                    logger.info(f"Avanzando al siguiente número: {numero_actual}")
                else:
                    numero_actual = 0  # Reiniciar a 0 si se completa toda la lista de números
                    logger.info("Reiniciando al número 0")

                request.session['numero_actual'] = numero_actual

                try:
                    senal_inicial = Senal.objects.get(name=str(numero_actual))
                    nueva_imagen = senal_inicial.imagen.url
                    logger.info(f"Nueva imagen cargada para el número: {numero_actual}")
                except Senal.DoesNotExist:
                    nueva_imagen = None
                    logger.error(f"No se encontró la imagen para el siguiente número: {numero_actual}")

                return JsonResponse({
                    'status': 'success',
                    'nuevo_numero': str(numero_actual),
                    'nueva_imagen': nueva_imagen, 
                    'mensaje': '¡Número correcto! Presiona el botón para continuar con el siguiente número.'
                })

            except ValueError:
                logger.error(f"El número actual {numero_actual} no se encontró en la lista de números.")
                return JsonResponse({'status': 'error', 'mensaje': 'Hubo un problema con la secuencia de números.'})

        logger.info(f"Número incorrecto. Seña realizada: {senal_realizada}, número actual esperado: {str(numero_actual)}")
        return JsonResponse({'status': 'error', 'mensaje': 'Número incorrecto, inténtalo de nuevo.'})


#*************************Vista específica para manejar la lección de colores*************************
def colores(request):
    lista_colores = ['Rojo', 'Verde', 'Azul', 'Amarillo', 'Naranja', 'Morado', 'Negro', 'Blanco', 'Rosa', 'Cafe']
    color_actual = request.session.get('color_actual', 'Rojo')

    colores = Nivel.objects.get(orden=3)  # Suponiendo que los colores están en el Nivel 2
    progreso, creado = Progreso.objects.get_or_create(usuario=request.user, nivel=colores)

    # Verificar si el usuario ya completó el nivel
    if progreso.completado:
        return JsonResponse({
            'status': 'completado',
            'mensaje': 'Ya completaste el Nivel de Colores. Puedes dirigirte al feedback.',
            'redirigir': '/feedback/'
        })

    try:
        senal_inicial = Senal.objects.get(name=color_actual)
        senal_detectada = senal_inicial.imagen.url
        logger.info(f"Imagen encontrada para el color {color_actual}: {senal_detectada}")
    except Senal.DoesNotExist:
        senal_detectada = None
        logger.error(f"No se encontró imagen para el color {color_actual}")

    if request.method == 'GET':
        return render(request, 'colores.html', {'senal_detectada': senal_detectada, 'color_actual': color_actual, 'progreso': progreso})

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        color_realizado = request.POST.get('color_realizado')
        logger.info(f"Color realizado: {color_realizado}, color actual: {color_actual}")

        if color_realizado == color_actual:
            indice_actual = lista_colores.index(color_actual)

            if color_actual == 'Cafe':
                # Marcar el progreso del nivel como completado
                progreso.completado = True
                progreso.fecha_completado = now()
                progreso.save()

                # Desbloquear el siguiente nivel
                try:
                    siguiente_nivel = Nivel.objects.get(orden=colores.orden + 1)
                    primera_leccion_siguiente_nivel = Leccion.objects.filter(nivel=siguiente_nivel).first()
                    if not primera_leccion_siguiente_nivel:
                        return JsonResponse({
                            'status': 'error',
                            'mensaje': 'El siguiente nivel no tiene una lección asociada.'
                        })

                    Progreso.objects.get_or_create(
                        usuario=request.user,
                        nivel=siguiente_nivel,
                        defaults={'desbloqueado': True, 'leccion': primera_leccion_siguiente_nivel}
                    )
                except Nivel.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'mensaje': 'No se pudo encontrar el siguiente nivel.'
                    })

                # Actualizar el dashboard del usuario
                try:
                    dashboard, created = Dashboard.objects.get_or_create(usuario=request.user)
                    dashboard.nivel_actual = siguiente_nivel
                    dashboard.actualizar_dashboard()
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'mensaje': f'Error al actualizar el dashboard: {str(e)}'
                    })

                # Redirigir a la página de niveles donde se mostrará el feedback desbloqueado
                return JsonResponse({
                    'status': 'success',
                    'mensaje': '¡Felicidades! Has completado el Nivel de Colores. ¡Prepárate para el siguiente nivel!',
                    'completado': True,
                    'redirigir': '/levels/'  # Redirigir al listado de niveles
                })

            if indice_actual < len(lista_colores) - 1:
                color_actual = lista_colores[indice_actual + 1]
            request.session['color_actual'] = color_actual

            try:
                senal_inicial = Senal.objects.get(name=color_actual)
                nueva_imagen = senal_inicial.imagen.url
                logger.info(f"Nueva imagen encontrada para el color {color_actual}: {nueva_imagen}")
            except Senal.DoesNotExist:
                nueva_imagen = None
                logger.error(f"No se encontró imagen para el color {color_actual}")

            return JsonResponse({
                'status': 'success',
                'nuevo_color': color_actual,
                'nueva_imagen': nueva_imagen,
                'mensaje': '¡Seña de color correcta! Presiona el botón para continuar con el siguiente color.',
                'completado': False 
            })

        return JsonResponse({'status': 'error', 'mensaje': 'Seña de color incorrecta, inténtalo de nuevo.'})
