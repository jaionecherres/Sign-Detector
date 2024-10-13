from django.http import StreamingHttpResponse
import cv2
from django.shortcuts import render
from .recognition import inference_classifier2  # Import the combined inference logic
import os

# Generador para capturar los frames de la cámara y hacer predicciones
def gen(camera, tipo_modelo):
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break

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
                # Si se detecta una seña o número, mostrarla en el frame
                cv2.putText(frame, f"Seña: {predicted_sign}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            # Convertir el frame en formato JPEG
            _, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    finally:
        camera.release()  # Asegúrate de liberar la cámara cuando termines

# Vista para transmitir el video según el tipo de modelo (alfabeto o números)
def video_feed(request, tipo_modelo):
    camera = cv2.VideoCapture(0)  # Abre la cámara
    return StreamingHttpResponse(gen(camera, tipo_modelo), content_type='multipart/x-mixed-replace; boundary=frame')

# Vista para el alfabeto
def alfabeto(request):
    return render(request, 'alfabeto.html')

# Vista para los números
def numeros(request):
    return render(request, 'numeros.html')
