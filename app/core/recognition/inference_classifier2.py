from django.http import StreamingHttpResponse
import cv2
import mediapipe as mp
import numpy as np
import pickle
from django.conf import settings
import os
from django.shortcuts import render
from collections import deque
import time 

# Cargar los tres modelos (alfabeto, números y colores)
model_alfabeto_path = os.path.join(settings.BASE_DIR, 'app', 'core', 'recognition', 'random_forest_landmarks_model.pkl')
model_numeros_path = os.path.join(settings.BASE_DIR, 'app', 'core', 'recognition', 'numeros_model.pkl')
model_colores_path = os.path.join(settings.BASE_DIR, 'app', 'core', 'recognition', 'colores_model.pkl')

model_alfabeto = None
model_numeros = None
model_colores = None

try:
    # Cargar modelo de alfabeto
    with open(model_alfabeto_path, 'rb') as model_file_alf:
        model_alfabeto = pickle.load(model_file_alf)
    print("Modelo de alfabeto cargado correctamente")

    # Cargar modelo de números
    with open(model_numeros_path, 'rb') as model_file_num:
        model_numeros = pickle.load(model_file_num)
    print("Modelo de números cargado correctamente")

    # Cargar modelo de colores
    with open(model_colores_path, 'rb') as model_file_colores:
        model_colores = pickle.load(model_file_colores)
    print("Modelo de colores cargado correctamente")

except FileNotFoundError as e:
    print(f"Error: {str(e)}")
except Exception as e:
    print(f"Error al cargar los modelos: {str(e)}")

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Ajustar MediaPipe con un umbral más bajo y desactivar el modo de imagen estática
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.2, min_tracking_confidence=0.2)

# Etiquetas para las predicciones de los modelos
labels_dict_alfabeto = {i: chr(65 + i) for i in range(26)}  # A-Z
labels_dict_numeros = {i: str(i) for i in range(10)}  # 0-9
labels_dict_colores = {0: 'Rojo', 1: 'Verde', 2: 'Azul', 3: 'Amarillo', 4: 'Naranja', 
                       5: 'Morado', 6: 'Negro', 7: 'Blanco', 8: 'Rosa', 9: 'Cafe'}  # Colores

frame_window = deque(maxlen=5)  # Almacenar hasta 5 frames

def predict_sign(frame, model, labels_dict, tipo_leccion):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Verificar si se detectan manos
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            data_aux = []
            x_ = []
            y_ = []

            # Recolectar coordenadas de los landmarks
            for landmark in hand_landmarks.landmark:
                x_.append(landmark.x)
                y_.append(landmark.y)

            # Calcular las coordenadas del recuadro alrededor de la mano
            x_min, x_max = int(min(x_) * frame.shape[1]), int(max(x_) * frame.shape[1])
            y_min, y_max = int(min(y_) * frame.shape[0]), int(max(y_) * frame.shape[0])

            # Inicializar el color del recuadro como rojo (incorrecto)
            color_recuadro = (0, 0, 255)  # Rojo por defecto (BGR)

            # Recolectar los landmarks para la predicción
            for landmark in hand_landmarks.landmark:
                data_aux.append(landmark.x - min(x_))
                data_aux.append(landmark.y - min(y_))

            # Lógica separada para colores
            if tipo_leccion == 'colores':
                frame_window.append(data_aux)

                # Verificar si ya tenemos 5 fotogramas para hacer la predicción
                if len(frame_window) == 5:
                    input_data = np.array(frame_window).flatten()

                    # Hacer la predicción con el modelo de colores
                    try:
                        prediction = model.predict([input_data])
                        pred_value = prediction[0]

                        # Obtener el valor predicho del diccionario de etiquetas
                        predicted_character = labels_dict.get(pred_value, str(pred_value))

                        # Si la predicción es correcta, cambiar el color del recuadro a verde
                        color_recuadro = (0, 255, 0)  # Verde si es correcto

                        # Dibujar el recuadro alrededor de la mano con el color correcto
                        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color_recuadro, 2)

                        return predicted_character
                    except Exception as e:
                        print(f"Error en la predicción: {str(e)}")
                        return None
            else:
                # Lógica para alfabeto y números (un solo fotograma)
                try:
                    prediction = model.predict([np.asarray(data_aux)])
                    pred_value = prediction[0]

                    # Obtener el valor predicho del diccionario de etiquetas
                    predicted_character = labels_dict.get(pred_value, str(pred_value))

                    # Si la predicción es correcta, cambiar el color del recuadro a verde
                    color_recuadro = (0, 255, 0)  # Verde si es correcto

                    # Dibujar el recuadro alrededor de la mano con el color correcto
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color_recuadro, 2)

                    return predicted_character
                except Exception as e:
                    print(f"Error en la predicción: {str(e)}")
                    return None

            # Dibujar el recuadro alrededor de la mano si no es correcto
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color_recuadro, 2)

    return None

# Generador para capturar los frames y hacer predicciones
def gen(camera, model, labels_dict):
    print("Iniciando la captura de video y reconocimiento")
    while True:
        ret, frame = camera.read()
        if not ret:
            print("No se pudo leer el frame de la cámara.")
            break

        # Predecir la seña en el frame capturado
        predicted_sign = predict_sign(frame, model, labels_dict)

        if predicted_sign:
            # Si se detecta una seña, mostrarla en el frame
            cv2.putText(frame, f"Predicción: {predicted_sign}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            print(f"Predicción detectada: {predicted_sign}")

        # Convertir el frame en formato JPEG para mostrar en el navegador
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Vista para transmitir el video y seleccionar el modelo (alfabeto, números o colores)
def video_feed(request, tipo_modelo):
    tipo_modelo = tipo_modelo.lower()
    print(f"Valor de tipo_modelo recibido: {tipo_modelo}")
    camera = cv2.VideoCapture(0)
    try:
        if tipo_modelo == 'alfabeto':
            return StreamingHttpResponse(gen(camera, model_alfabeto, labels_dict_alfabeto),
                                         content_type='multipart/x-mixed-replace; boundary=frame')
        elif tipo_modelo == 'numeros':
            return StreamingHttpResponse(gen(camera, model_numeros, labels_dict_numeros),
                                         content_type='multipart/x-mixed-replace; boundary=frame')
        elif tipo_modelo == 'colores':
            return StreamingHttpResponse(gen(camera, model_colores, labels_dict_colores),
                                         content_type='multipart/x-mixed-replace; boundary=frame')
        else:
            print(f"Tipo de modelo no válido: {tipo_modelo}")
    finally:
        camera.release()
        print("Cámara liberada correctamente.")


