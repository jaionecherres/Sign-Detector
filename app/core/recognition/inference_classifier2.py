from django.http import StreamingHttpResponse
import cv2
import mediapipe as mp
import numpy as np
import pickle
from django.conf import settings
import os
from django.shortcuts import render

#Cargar ambos modelos
model_alfabeto_path = os.path.join(settings.BASE_DIR, 'app', 'core', 'recognition', 'model.p')
model_numeros_path = os.path.join(settings.BASE_DIR, 'app', 'core', 'recognition', 'model2.p')

model_alfabeto = None
model_numeros = None

try:
    with open(model_alfabeto_path, 'rb') as model_file_alf:
        model_dict_alfabeto = pickle.load(model_file_alf)
        model_alfabeto = model_dict_alfabeto['model']
    print("Modelo de alfabeto cargado correctamente")

    with open(model_numeros_path, 'rb') as model_file_num:
        model_dict_numeros = pickle.load(model_file_num)
        model_numeros = model_dict_numeros['model']
    print("Modelo de números cargado correctamente")
except FileNotFoundError as e:
    print(f"Error: {str(e)}")
except Exception as e:
    print(f"Error al cargar los modelos: {str(e)}")

#Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

#Ajustar MediaPipe con un umbral más bajo y desactivar el modo de imagen estática
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.2, min_tracking_confidence=0.2)

#Etiquetas para las predicciones del modelo
labels_dict_alfabeto = {i: chr(65 + i) for i in range(26)}  # A-Z
labels_dict_numeros = {i: str(i) for i in range(10)}  # 0-9

#Función para predecir usando el modelo seleccionado
def predict_sign(frame, model, labels_dict):
    #Convertir el frame a RGB para usar con MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    #Verificar si se detectan manos
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            #Extraer coordenadas clave para el modelo
            data_aux = []
            x_ = []
            y_ = []

            #Recolectar coordenadas
            for landmark in hand_landmarks.landmark:
                x_.append(landmark.x)
                y_.append(landmark.y)

            for landmark in hand_landmarks.landmark:
                data_aux.append(landmark.x - min(x_))
                data_aux.append(landmark.y - min(y_))

            #Hacer la predicción con el modelo seleccionado
            try:
                prediction = model.predict([np.asarray(data_aux)])
                pred_value = prediction[0]  # Obtener la predicción

                #Si el valor predicho es un número o letra, usar labels_dict
                if isinstance(pred_value, (int, np.integer)):
                    predicted_character = labels_dict[pred_value]
                else:
                    predicted_character = str(pred_value)

                return predicted_character
            except Exception as e:
                print(f"Error en la predicción: {str(e)}")
                return None

    return None  

#Generador para capturar los frames y hacer predicciones
def gen(camera, model, labels_dict):
    print("Iniciando la captura de video y reconocimiento")
    while True:
        ret, frame = camera.read()
        if not ret:
            print("No se pudo leer el frame de la cámara.")
            break

        #Predecir la seña en el frame capturado
        predicted_sign = predict_sign(frame, model, labels_dict)

        if predicted_sign:
            #Si se detecta una seña, mostrarla en el frame
            cv2.putText(frame, f"Predicción: {predicted_sign}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            print(f"Predicción detectada: {predicted_sign}")

        #Convertir el frame en formato JPEG para mostrar en el navegador
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#Vista para transmitir el video y seleccionar el modelo (alfabeto o números)
def video_feed(request, tipo_modelo):
    camera = cv2.VideoCapture(0) 
    try:
        if tipo_modelo == 'alfabeto':
            return StreamingHttpResponse(gen(camera, model_alfabeto, labels_dict_alfabeto),
                                         content_type='multipart/x-mixed-replace; boundary=frame')
        elif tipo_modelo == 'numeros':
            return StreamingHttpResponse(gen(camera, model_numeros, labels_dict_numeros),
                                         content_type='multipart/x-mixed-replace; boundary=frame')
        else:
            print("Tipo de modelo no válido.")
    finally:
        camera.release() 
        print("Cámara liberada correctamente.")
