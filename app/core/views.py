from django.http import StreamingHttpResponse, JsonResponse
import cv2
from django.shortcuts import render
from .recognition import inference_classifier2  # Import the combined inference logic
from .models import Senal
import time
import logging

logger = logging.getLogger(__name__)

# Variable global para la cámara
camera = None

# Función para abrir la cámara
def abrir_camara():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Función para cerrar la cámara
def cerrar_camara():
    global camera
    if camera is not None:
        camera.release()
        camera = None

# Generador para capturar los frames de la cámara y hacer predicciones
def gen(tipo_modelo):
    global camera
    abrir_camara()
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            time.sleep(0.05)

            # Elegir el modelo y etiquetas según el tipo_modelo
            if tipo_modelo == 'alfabeto':
                model = inference_classifier2.model_alfabeto
                labels_dict = inference_classifier2.labels_dict_alfabeto
            elif tipo_modelo == 'numeros':
                model = inference_classifier2.model_numeros
                labels_dict = inference_classifier2.labels_dict_numeros
            else:
                model = None
                labels_dict = None

            # Realizar predicción si el modelo es válido
            if model is not None:
                predicted_sign = inference_classifier2.predict_sign(frame, model, labels_dict)
            else:
                predicted_sign = None

            if predicted_sign:
                # Mostrar la seña en el frame
                cv2.putText(frame, f"Seña: {predicted_sign}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            # Convertir el frame a formato JPEG
            _, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    finally:
        cerrar_camara()  # Cerrar la cámara cuando termina el generador

# Vista para transmitir el video según el tipo de modelo (alfabeto o números)
def video_feed(request, tipo_modelo):
    abrir_camara()  # Asegurar que la cámara esté abierta antes de iniciar la transmisión
    return StreamingHttpResponse(gen(tipo_modelo), content_type='multipart/x-mixed-replace; boundary=frame')

# Función para obtener el último frame de la cámara
def obtener_frame():
    global camera
    if camera is not None and camera.isOpened():
        ret, frame = camera.read()
        if ret:
            return frame
    return None

# Vista para detectar la seña usando el último frame capturado
def detectar_senal(request):
    # No necesitas abrir la cámara aquí, porque ya está abierta en video_feed
    # Cargar modelo y etiquetas
    model = inference_classifier2.model_alfabeto
    labels_dict = inference_classifier2.labels_dict_alfabeto

    # Obtener el último frame de la cámara
    frame = obtener_frame()

    if frame is None:
        return JsonResponse({'status': 'error', 'mensaje': 'No se pudo capturar la imagen'})

    # Procesar el frame para detectar la seña
    predicted_sign = inference_classifier2.predict_sign(frame, model, labels_dict)

    if predicted_sign:
        return JsonResponse({'status': 'success', 'senal_detectada': predicted_sign})
    else:
        return JsonResponse({'status': 'error', 'mensaje': 'No se detectó ninguna seña'})

def alfabeto(request):
    abecedario = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    letra_actual = request.session.get('letra_actual', 'A')

    try:
        senal_inicial = Senal.objects.get(name=letra_actual)  
        senal_detectada = senal_inicial.imagen.url
    except Senal.DoesNotExist:
        senal_detectada = None

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        senal_realizada = request.POST.get('senal_realizada')

        logger.info(f"Seña realizada: {senal_realizada}, letra actual: {letra_actual}")
        logger.info("Vista alfabeto cargada correctamente.")

        if senal_realizada == letra_actual:
            indice_actual = abecedario.index(letra_actual)
            if indice_actual < len(abecedario) - 1:
                letra_actual = abecedario[indice_actual + 1]
            else:
                letra_actual = 'A'

            request.session['letra_actual'] = letra_actual

            try:
                senal_inicial = Senal.objects.get(name=letra_actual)
                nueva_imagen = senal_inicial.imagen.url
            except Senal.DoesNotExist:
                nueva_imagen = None

            return JsonResponse({
                'status': 'success',
                'nueva_letra': letra_actual,
                'nueva_imagen': nueva_imagen
            })

        return JsonResponse({'status': 'error', 'mensaje': 'Seña incorrecta'})

    return render(request, 'alfabeto.html', {'senal_detectada': senal_detectada, 'letra_actual': letra_actual})

def numeros(request):
    return render(request, 'numeros.html')
