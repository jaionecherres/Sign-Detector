from django.http import StreamingHttpResponse
import cv2
from django.shortcuts import render
from .recognition.inference_classifier import predict_sign  # Importar la inferencia

# Generador para capturar los frames de la cámara
def gen(camera):
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break

            # Predecir la seña en el frame capturado
            predicted_sign = predict_sign(frame)
            
            if predicted_sign:
                # Si se detecta una seña, mostrarla en el frame
                cv2.putText(frame, f"Seña: {predicted_sign}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            # Convertir el frame en formato JPEG
            _, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    finally:
        camera.release()  # Asegúrate de liberar la cámara cuando termines

# Vista para transmitir el video
def video_feed(request):
    camera = cv2.VideoCapture(0)  # Abre la cámara
    return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')

def home(request):
    return render(request, 'alfabeto.html')
