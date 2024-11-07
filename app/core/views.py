from django.http import StreamingHttpResponse, JsonResponse
from django.views.generic import DetailView
from django.shortcuts import redirect, render
import numpy as np
from .models import *
from django.utils.timezone import now
from app.security.models import Dashboard
from .recognition import inference_classifier2 
from django.shortcuts import get_object_or_404
import cv2, time, logging

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
        if not ret or frame is None:
            logger.error("No se pudo leer el frame de la cámara o el frame es None. Intentando reiniciar la cámara.")
            reiniciar_camara()  # Reinicia la cámara en caso de error
            return None
        return frame
    else:
        logger.error("La cámara no está disponible o no se abrió correctamente. Intentando reiniciar la cámara.")
        reiniciar_camara()
        return None

# Función para reiniciar la cámara
def reiniciar_camara():
    global camera
    if camera is not None:
        camera.release()
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if camera.isOpened():
        logger.info("Cámara reiniciada correctamente.")
    else:
        logger.error("No se pudo reiniciar la cámara.")

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

            if tipo_modelo == 'alfabeto':
                model = inference_classifier2.model_alfabeto
                labels_dict = inference_classifier2.labels_dict_alfabeto
            elif tipo_modelo == 'numeros':
                model = inference_classifier2.model_numeros
                labels_dict = inference_classifier2.labels_dict_numeros
            elif tipo_modelo == 'colores':
                model = inference_classifier2.model_colores
                labels_dict = inference_classifier2.labels_dict_colores
            elif tipo_modelo == 'evaluación_final':
                model = inference_classifier2.model_senas
                labels_dict = inference_classifier2.labels_dict_senas

            #Realizar predicción y dibujar el recuadro
            predicted_sign = inference_classifier2.predict_sign(frame, model, labels_dict, tipo_modelo)

            if predicted_sign:
                #Mostrar la señal predicha en el frame
                cv2.putText(frame, f"{predicted_sign}", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            #Convertir el frame a formato JPEG y enviarlo al navegador
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
    elif tipo_leccion == 'evaluacion_final': 
        model = inference_classifier2.model_senas
        labels_dict = inference_classifier2.labels_dict_senas
    else:
        return JsonResponse({'status': 'error', 'mensaje': 'Tipo de lección no válido.'})

    frame = obtener_frame()

    if frame is None:
        return JsonResponse({'status': 'error', 'mensaje': 'No se pudo capturar la imagen'})

    predicted_sign = inference_classifier2.predict_sign(frame, model, labels_dict, tipo_leccion)

    # Asegurarse de que la predicción es del tipo correcto
    if isinstance(predicted_sign, np.ndarray):
        predicted_sign = predicted_sign.tolist()  #Convertir ndarray a lista si es necesario

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
        context["tipo_leccion"] = tipo_leccion
        if tipo_leccion != 'evaluación_final':
            context["nivel"] = self.object.nivel
        
        return context

    #Define la plantilla según el tipo de lección
    def get_template_names(self):
        tipo_leccion = self.object.nivel.name.lower() 
        if tipo_leccion == 'alfabeto':
            return ['core/lecciones/alfabeto.html']  
        elif tipo_leccion == 'numeros':
            return ['core/lecciones/numeros.html'] 
        elif tipo_leccion == 'colores':
            return ['core/lecciones/colores.html'] 
        elif tipo_leccion == 'evaluación_final': 
            return ['core/lecciones/evaluacion_final.html']
        else:
            return ['core/lecciones/evaluacion_final.html']  #Plantilla predeterminada 

def feedback_nivel(request, nivel_id):
    nivel = get_object_or_404(Nivel, id=nivel_id)
    usuario = request.user

    # Verificar si el nivel fue completado para permitir el acceso al feedback
    progreso = Progreso.objects.filter(usuario=usuario, nivel=nivel).first()
    if not progreso or not progreso.completado:
        return JsonResponse({'status': 'error', 'mensaje': 'Debes completar el nivel antes de acceder al feedback.'})

    # Determinar el tipo de feedback basado en el nivel
    if nivel.orden == 1:
        tipo_feedback = 'alfabeto'
        template_name = 'core/lecciones/feedback.html'
    elif nivel.orden == 2:
        tipo_feedback = 'numeros'
        template_name = 'core/lecciones/feedback_num.html'
    elif nivel.orden == 3:
        tipo_feedback = 'colores'
        template_name = 'core/lecciones/feedback_colores.html'
    else:
        return JsonResponse({'status': 'error', 'mensaje': 'Nivel de feedback no reconocido.'})
    
    request.session['tipo_feedback'] = tipo_feedback

    # Configuración inicial para cada tipo de feedback
    alfabeto = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    numeros = list(range(0, 11))  # Del 0 al 10
    COLORES_CALIDOS = ['Rojo', 'Naranja', 'Amarillo', 'Rosa', 'Cafe']
    COLORES_FRIOS = ['Verde', 'Azul', 'Morado', 'Negro', 'Blanco']

    if tipo_feedback == 'alfabeto':
        letra_actual = request.session.get('letra_actual_feedback', alfabeto[0])
        try:
            senal = Senal.objects.get(name=letra_actual)
            senal_detectada = senal.video.url if senal.video else senal.imagen.url
            es_video = bool(senal.video)
        except Senal.DoesNotExist:
            senal_detectada = None
            es_video = False
    elif tipo_feedback == 'numeros':
        numero_actual = request.session.get('numero_actual_feedback', numeros[0])
        try:
            senal = Senal.objects.get(name=str(numero_actual))
            senal_detectada = senal.video.url if senal.video else senal.imagen.url
            es_video = bool(senal.video)
        except Senal.DoesNotExist:
            senal_detectada = None
            es_video = False
    elif tipo_feedback == 'colores':
        color_actual = request.session.get('color_actual_feedback', COLORES_CALIDOS[0])
        categoria_colores = COLORES_CALIDOS if color_actual in COLORES_CALIDOS else COLORES_FRIOS
        try:
            senal = Senal.objects.get(name=color_actual)
            senal_detectada = senal.video.url if senal.video else senal.imagen.url
            es_video = bool(senal.video)
        except Senal.DoesNotExist:
            senal_detectada = None
            es_video = False

    if request.method == 'GET':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if tipo_feedback == 'alfabeto':
                request.session['letra_actual_feedback'] = alfabeto[0]
                return JsonResponse({
                    'status': 'success',
                    'letra_actual': letra_actual,
                    'senal_detectada': senal_detectada,
                    'tipo_feedback': 'alfabeto'
                })
            elif tipo_feedback == 'numeros':
                request.session['numero_actual_feedback'] = numeros[0]
                return JsonResponse({
                    'status': 'success',
                    'numero_actual': numero_actual,
                    'senal_detectada': senal_detectada,
                    'tipo_feedback': 'numeros'
                })
            elif tipo_feedback == 'colores':
                request.session['color_actual_feedback'] = COLORES_CALIDOS[0]
                return JsonResponse({
                    'status': 'success',
                    'color_actual': color_actual,
                    'senal_detectada': senal_detectada,
                    'tipo_feedback': 'colores'
                })
        else:
            # Renderizar el HTML adecuado según el tipo de feedback
            request.session['letra_actual_feedback'] = alfabeto[0]
            request.session['numero_actual_feedback'] = numeros[0]
            request.session['color_actual_feedback'] = COLORES_CALIDOS[0]
            return render(request, template_name, {
                'senal_detectada': senal_detectada,
                'letra_actual': letra_actual if tipo_feedback == 'alfabeto' else None,
                'numero_actual': numero_actual if tipo_feedback == 'numeros' else None,
                'color_actual': color_actual.capitalize() if tipo_feedback == 'colores' else None,
                'nivel': nivel,
                'tipo_feedback': tipo_feedback
            })

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        senal_realizada = request.POST.get('senal_realizada', '').strip().lower()

        if tipo_feedback == 'alfabeto':
            if senal_realizada == letra_actual.lower():
                indice_letra = alfabeto.index(letra_actual)
                if indice_letra == len(alfabeto) - 1:
                    request.session['letra_actual_feedback'] = alfabeto[0]
                    return JsonResponse({
                        'status': 'success',
                        'mensaje': '¡Has completado el feedback del alfabeto!',
                        'completado': True,
                        'redirigir': '/levels/'
                    })
                else:
                    letra_actual = alfabeto[indice_letra + 1]
                    request.session['letra_actual_feedback'] = letra_actual
                    try:
                        nueva_imagen = Senal.objects.get(name=letra_actual).imagen.url
                    except Senal.DoesNotExist:
                        nueva_imagen = None
                    return JsonResponse({
                        'status': 'success',
                        'nueva_letra': letra_actual,
                        'nueva_imagen': nueva_imagen,
                        'mensaje': '¡Seña correcta! Continúa con la siguiente letra.',
                        'tipo_feedback': 'alfabeto'
                    })

        elif tipo_feedback == 'numeros':
            if senal_realizada.isdigit() and int(senal_realizada) == numero_actual:
                indice_numero = numeros.index(numero_actual)
                if indice_numero == len(numeros) - 1:
                    request.session['numero_actual_feedback'] = numeros[0]
                    return JsonResponse({
                        'status': 'success',
                        'mensaje': '¡Has completado el feedback de los números!',
                        'completado': True,
                        'redirigir': '/levels/'
                    })
                else:
                    numero_actual = numeros[indice_numero + 1]
                    request.session['numero_actual_feedback'] = numero_actual
                    try:
                        nueva_imagen = Senal.objects.get(name=str(numero_actual)).imagen.url
                    except Senal.DoesNotExist:
                        nueva_imagen = None
                    return JsonResponse({
                        'status': 'success',
                        'nuevo_numero': numero_actual,
                        'nueva_imagen': nueva_imagen,
                        'mensaje': '¡Número correcto! Continúa con el siguiente número.',
                        'tipo_feedback': 'numeros'
                    })

        elif tipo_feedback == 'colores':
            if senal_realizada == color_actual.lower():
                indice_color = categoria_colores.index(color_actual)
                
                if indice_color == len(categoria_colores) - 1:
                    # Si es el último color cálido, pasar a los fríos
                    if categoria_colores == COLORES_CALIDOS:
                        request.session['color_actual_feedback'] = COLORES_FRIOS[0]
                        request.session['categoria_colores'] = 'fríos'
                        return JsonResponse({
                            'status': 'transition',
                            'mensaje': '¡Colores cálidos completados! Ahora, continúa con los colores fríos.',
                            'nuevo_color': COLORES_FRIOS[0].capitalize(),
                            'nueva_imagen': Senal.objects.get(name=COLORES_FRIOS[0]).imagen.url
                        })
                    # Si es el último color frío, finalizar feedback
                    else:
                        return JsonResponse({
                            'status': 'success',
                            'mensaje': '¡Has completado el feedback de los colores!',
                            'completado': True,
                            'redirigir': '/levels/'
                        })
                else:
                    color_actual = categoria_colores[indice_color + 1]
                    request.session['color_actual_feedback'] = color_actual
                try:
                    nueva_imagen = Senal.objects.get(name=color_actual).imagen.url
                except Senal.DoesNotExist:
                    nueva_imagen = None
                return JsonResponse({
                    'status': 'success',
                    'nuevo_color': color_actual.capitalize(),
                    'nueva_imagen': nueva_imagen,
                    'mensaje': '¡Color correcto! Continúa con el siguiente color.',
                    'tipo_feedback': 'colores'
                })

        return JsonResponse({'status': 'error', 'mensaje': 'Seña incorrecta, inténtalo de nuevo.'})

#***********************Vista específica para manejar la lección de alfabeto***********************

def alfabeto(request):
    # Listas de vocales y consonantes
    vocales = list('AEIOU')
    consonantes = list('BCDFGHJKLMNPQRSTVWXYZ')
    
    # Determinar si está en la fase de vocales o consonantes
    fase_actual = request.session.get('fase_actual', 'vocales')
    letra_actual = request.session.get('letra_actual', vocales[0] if fase_actual == 'vocales' else consonantes[0])

    # Obtener el nivel y progreso del usuario
    alfabeto = Nivel.objects.get(orden=1)
    progreso, _ = Progreso.objects.get_or_create(usuario=request.user, nivel=alfabeto)

    # Verificar si el nivel está completo
    if progreso.completado:
        return JsonResponse({
            'status': 'completado',
            'mensaje': 'Ya completaste el Nivel 1! Puedes dirigirte a tu feedback.',
            'redirigir': '/levels/'
        })

    # Intentar obtener la señal de la letra actual
    try:
        senal_inicial = Senal.objects.get(name=letra_actual)
        senal_detectada = senal_inicial.imagen.url
        logger.info(f"Imagen encontrada para la letra {letra_actual}: {senal_detectada}")
    except Senal.DoesNotExist:
        senal_detectada = "media/senales/Captura_de_pantalla_2024-10-23_153532.png"
        logger.error(f"No se encontró imagen para la letra {letra_actual}")

    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'letra_actual': letra_actual,
            'senal_detectada': senal_detectada,
            'fase_actual': fase_actual,
        })
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        senal_realizada = request.POST.get('senal_realizada')
        logger.info(f"Seña realizada: {senal_realizada}, letra actual: {letra_actual}, fase actual: {fase_actual}")

        # Verificar si la seña realizada es correcta
        if senal_realizada == letra_actual:
            if fase_actual == 'vocales':
                # Si es la última vocal, pasar a consonantes y mostrar mensaje de transición
                if letra_actual == vocales[-1]:
                    fase_actual = 'consonantes'
                    letra_actual = consonantes[0]
                    request.session['fase_actual'] = fase_actual
                    request.session['letra_actual'] = letra_actual

                    try:
                        senal_inicial = Senal.objects.get(name=letra_actual)
                        nueva_imagen = senal_inicial.imagen.url
                    except Senal.DoesNotExist:
                        nueva_imagen = None

                    return JsonResponse({
                        'status': 'transition',
                        'mensaje': '¡Has completado las vocales! Ahora pasará a las consonantes.',
                        'nueva_fase': fase_actual,
                        'nueva_letra': letra_actual,
                        'nueva_imagen': nueva_imagen
                    })
                else:
                    # Ir a la siguiente vocal
                    letra_actual = vocales[vocales.index(letra_actual) + 1]
            elif fase_actual == 'consonantes':
                # Si es la última consonante, marcar el nivel como completado y desbloquear el siguiente
                if letra_actual == consonantes[-1]:
                    progreso.completado = True
                    progreso.fecha_completado = now()
                    progreso.save()

                    # Intentar desbloquear el siguiente nivel
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
                        dashboard, _ = Dashboard.objects.get_or_create(usuario=request.user)
                        dashboard.nivel_actual = siguiente_nivel
                        dashboard.actualizar_dashboard()
                    except Exception as e:
                        return JsonResponse({
                            'status': 'error',
                            'mensaje': f'Error al actualizar el dashboard: {str(e)}'
                        })

                    return JsonResponse({
                        'status': 'success',
                        'mensaje': '¡Felicidades! Has completado el Nivel 1. ¡Prepárate para el siguiente nivel!',
                        'completado': True,
                        'redirigir': '/levels/'
                    })
                else:
                    # Ir a la siguiente consonante
                    letra_actual = consonantes[consonantes.index(letra_actual) + 1]

            # Guardar la fase y letra actual en la sesión
            request.session['fase_actual'] = fase_actual
            request.session['letra_actual'] = letra_actual

            # Intentar cargar la imagen de la nueva letra
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
    # Listas de números pares e impares
    pares = [0, 2, 4, 6, 8, 10]
    impares = [1, 3, 5, 7, 9]
    
    # Determinar si está en la fase de pares o impares
    fase_actual = request.session.get('fase_actual', 'pares')
    numero_actual = request.session.get('numero_actual', pares[0] if fase_actual == 'pares' else impares[0])

    # Obtener el nivel y progreso del usuario
    numeros = Nivel.objects.get(orden=2)
    progreso, _ = Progreso.objects.get_or_create(usuario=request.user, nivel=numeros)

    # Verificar si el nivel está completo
    if progreso.completado:
        return JsonResponse({
            'status': 'completado',
            'mensaje': 'Ya completaste el Nivel 2! Puedes dirigirte a tu feedback.',
            'redirigir': '/levels/'
        })

    # Intentar obtener la señal del número actual
    try:
        senal_inicial = Senal.objects.get(name=str(numero_actual))
        senal_detectada = senal_inicial.imagen.url
        logger.info(f"Imagen encontrada para el número {numero_actual}")
    except Senal.DoesNotExist:
        senal_detectada = None
        logger.error(f"No se encontró imagen para el número {numero_actual}")

    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'numero_actual': numero_actual,
            'senal_detectada': senal_detectada,
            'fase_actual': fase_actual,
        })
    
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        senal_realizada = request.POST.get('senal_realizada')
        logger.info(f"Seña realizada: {senal_realizada}, número actual: {numero_actual}, fase actual: {fase_actual}")

        # Verificar si la seña realizada es correcta
        if str(senal_realizada).strip() == str(numero_actual):
            if fase_actual == 'pares':
                # Si es el último par (10), pasar a los impares y mostrar mensaje de transición
                if numero_actual == pares[-1]:  # Aquí el último número es 10
                    fase_actual = 'impares'
                    numero_actual = impares[0]
                    request.session['fase_actual'] = fase_actual
                    request.session['numero_actual'] = numero_actual

                    try:
                        senal_inicial = Senal.objects.get(name=str(numero_actual))
                        nueva_imagen = senal_inicial.imagen.url
                    except Senal.DoesNotExist:
                        nueva_imagen = None

                    return JsonResponse({
                        'status': 'transition',
                        'mensaje': '¡Has completado los números pares! Ahora pasarás a los impares.',
                        'nueva_fase': fase_actual,
                        'nuevo_numero': numero_actual,
                        'nueva_imagen': nueva_imagen
                    })
                else:
                    # Ir al siguiente número par
                    numero_actual = pares[pares.index(numero_actual) + 1]
            elif fase_actual == 'impares':
                # Si es el último impar (9), marcar el nivel como completado y desbloquear el siguiente
                if numero_actual == impares[-1]:
                    progreso.completado = True
                    progreso.fecha_completado = now()
                    progreso.save()

                    # Intentar desbloquear el siguiente nivel
                    try:
                        siguiente_nivel = Nivel.objects.get(orden=numeros.orden + 1)
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
                        dashboard, _ = Dashboard.objects.get_or_create(usuario=request.user)
                        dashboard.nivel_actual = siguiente_nivel
                        dashboard.actualizar_dashboard()
                    except Exception as e:
                        return JsonResponse({
                            'status': 'error',
                            'mensaje': f'Error al actualizar el dashboard: {str(e)}'
                        })

                    return JsonResponse({
                        'status': 'success',
                        'mensaje': '¡Felicidades! Has completado el Nivel 2. ¡Prepárate para el siguiente nivel!',
                        'completado': True,
                        'redirigir': '/levels/'
                    })
                else:
                    # Ir al siguiente número impar
                    numero_actual = impares[impares.index(numero_actual) + 1]

            # Guardar la fase y número actual en la sesión
            request.session['fase_actual'] = fase_actual
            request.session['numero_actual'] = numero_actual

            # Intentar cargar la imagen del nuevo número
            try:
                senal_inicial = Senal.objects.get(name=str(numero_actual))
                nueva_imagen = senal_inicial.imagen.url
                logger.info(f"Nueva imagen encontrada para el número {numero_actual}: {nueva_imagen}")
            except Senal.DoesNotExist:
                nueva_imagen = None
                logger.error(f"No se encontró imagen para el número {numero_actual}")

            return JsonResponse({
                'status': 'success',
                'nuevo_numero': numero_actual,
                'nueva_imagen': nueva_imagen,
                'mensaje': '¡Número correcto! Presiona el botón para continuar con el siguiente número.',
                'completado': False
            })

        return JsonResponse({'status': 'error', 'mensaje': 'Número incorrecto, inténtalo de nuevo.'})

#*************************Vista específica para manejar la lección de colores*************************
def colores(request):
    lista_colores = ['Rojo', 'Verde', 'Azul', 'Amarillo', 'Naranja', 'Morado', 'Negro', 'Blanco', 'Rosa', 'Cafe']
    color_actual = request.session.get('color_actual', 'Rojo')

    colores = Nivel.objects.get(orden=3) 
    progreso, creado = Progreso.objects.get_or_create(usuario=request.user, nivel=colores)

    if progreso.completado:
        return JsonResponse({
            'status': 'completado',
            'mensaje': 'Ya completaste el Nivel 3! Puedes dirigirse al feedback.',
            'redirigir': '/levels/'
        })

    try:
        senal_inicial = Senal.objects.get(name=color_actual)
        senal_detectada = senal_inicial.imagen.url
        logger.info(f"Imagen encontrada para el color {color_actual}: {senal_detectada}")
    except Senal.DoesNotExist:
        senal_detectada = None
        logger.error(f"No se encontró imagen para el color {color_actual}")

    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'letra_actual': color_actual,
            'senal_detectada': senal_detectada,
        })
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        color_realizado = request.POST.get('color_realizado')
        logger.info(f"Color realizado: {color_realizado}, color actual: {color_actual}")

        if color_realizado == color_actual:
            indice_actual = lista_colores.index(color_actual)

            if color_actual == 'Cafe':
                #Marcar el progreso del nivel como completado
                progreso.completado = True
                progreso.fecha_completado = now()
                progreso.save()

                #Desbloquear el siguiente nivel
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

                #Actualizar el dashboard del usuario
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

def evaluacion_final(request):
    # Lista de señas específicas a completar en orden
    lista_senas = ['A', 'B', 'C', '1', '2', '3', 'Rojo', 'Verde', 'Cafe']
    senal_actual = request.session.get('senal_actual', lista_senas[0])

    # Obtener el nivel y progreso del usuario
    nivel_evaluacion_final = Nivel.objects.get(name='evaluacion_final')
    progreso, _ = Progreso.objects.get_or_create(usuario=request.user, nivel=nivel_evaluacion_final)

    # Verificar si el nivel está completo
    if progreso.completado:
        return JsonResponse({
            'status': 'completado',
            'mensaje': 'Ya completaste la Evaluación Final! Puedes dirigirte al menú de niveles.',
            'redirigir': '/levels/'
        })

    # Intentar obtener la señal actual
    try:
        senal_inicial = Senal.objects.get(name=senal_actual)
        senal_detectada = senal_inicial.imagen.url
    except Senal.DoesNotExist:
        senal_detectada = None

    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'senal_actual': senal_actual,
            'senal_detectada': senal_detectada,
        })

    # Procesar la seña realizada por el usuario (si la solicitud es POST)
    if request.method == 'POST':
        senal_realizada = request.POST.get('senal_realizada')
        if senal_realizada == senal_actual:
            # Avanzar a la siguiente seña
            indice_actual = lista_senas.index(senal_actual)
            if indice_actual == len(lista_senas) - 1:
                # Si es la última seña, marcar como completado
                progreso.completado = True
                progreso.fecha_completado = now()
                progreso.save()

                # Actualizar el dashboard del usuario
                try:
                    dashboard, _ = Dashboard.objects.get_or_create(usuario=request.user)
                    dashboard.nivel_actual = None  # No hay más niveles después de la evaluación final
                    dashboard.actualizar_dashboard()
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'mensaje': f'Error al actualizar el dashboard: {str(e)}'
                    })

                return JsonResponse({
                    'status': 'success',
                    'mensaje': '¡Felicidades! Has completado la Evaluación Final.',
                    'completado': True,
                    'redirigir': '/levels/'
                })
            else:
                # Avanzar a la siguiente seña en la evaluación final
                senal_actual = lista_senas[indice_actual + 1]
                request.session['senal_actual'] = senal_actual

                nueva_imagen = Senal.objects.get(name=senal_actual).imagen.url if Senal.objects.filter(name=senal_actual).exists() else None
                return JsonResponse({
                    'status': 'success',
                    'nueva_senal': senal_actual,
                    'nueva_imagen': nueva_imagen,
                    'mensaje': '¡Seña correcta! Continúa con la siguiente seña.',
                })

        return JsonResponse({'status': 'error', 'mensaje': 'Seña incorrecta, inténtalo de nuevo.'})