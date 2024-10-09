from django.http import StreamingHttpResponse
import cv2
import mediapipe as mp
import numpy as np
import pickle
from django.conf import settings
import os

# Obtener la ruta absoluta del modelo
model_path = os.path.join(settings.BASE_DIR, 'app', 'core', 'recognition', 'model.p')
    
# Cargar el modelo
model = None
try:
    model_dict = pickle.load(open(model_path, 'rb'))
    model = model_dict['model']
    print("Modelo cargado correctamente")
except FileNotFoundError:
    print(f"Error: El archivo del modelo no se encuentra en {model_path}")
except Exception as e:
    print(f"Error al cargar el modelo: {str(e)}")

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Ajustar MediaPipe con un umbral más bajo y desactivar el modo de imagen estática
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.2, min_tracking_confidence=0.2)

# Etiquetas para las predicciones del modelo (puedes ajustar estas etiquetas según tu modelo)
labels_dict = {0: 'A', 1: 'B', 2: 'C'}  # Asume que el modelo predice letras A, B, C

# Función para procesar los frames y hacer predicciones
def predict_sign(frame):
    global model

    if model is None:
        print("El modelo no está cargado. No se puede hacer la predicción.")
        return None

    # Convertir el frame a RGB para usar con MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Verificar si se detectan manos
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extraer coordenadas clave para el modelo
            data_aux = []
            x_ = []
            y_ = []

            # Recolectar coordenadas
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                x_.append(x)
                y_.append(y)

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

            # Hacer la predicción con el modelo cargado
            try:
                prediction = model.predict([np.asarray(data_aux)])
                predicted_character = labels_dict[int(prediction[0])]
                return predicted_character
            except Exception as e:
                print(f"Error en la predicción: {str(e)}")
                return None

    return None  # Si no se detecta nada, retornar None

# Generador para capturar los frames de la cámara y hacer predicciones
def gen(camera):
    global model
    print("Iniciando la captura de video y reconocimiento")
    while True:
        ret, frame = camera.read()
        if not ret:
            print("No se pudo leer el frame de la cámara.")
            break

        # Predecir la seña en el frame capturado
        predicted_sign = predict_sign(frame)

        if predicted_sign:
            # Si se detecta una seña, mostrarla en el frame
            cv2.putText(frame, f"Seña: {predicted_sign}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            print(f"Seña detectada: {predicted_sign}")

        # Convertir el frame en formato JPEG para mostrar en el navegador
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Vista para transmitir el video
def video_feed(request):
    camera = cv2.VideoCapture(0)  # Abre la cámara
    try:
        return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')
    finally:
        camera.release()  # Asegurarse de liberar la cámara cuando se termina el streaming
        print("Cámara liberada correctamente.")
