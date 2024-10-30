Bienvenido a Dullnane Sign Detector!!

Este proyecto tiene como objetivo capturar y reconocer señas a través de la inteligencia artificial con una conectividad de cámara al dispositivo del usuario. Está creado con el objetivo de ofrecer una experiencia interactiva que facilite el aprendizaje del lenguaje de señas a los usuarios.

## Descripción
Este sistema emplea OpenCV, scikit-learn y Django para capturar y procesar imágenes de señas en tiempo real, ofreciendo retroalimentación inmediata sobre la precisión de cada seña. Asimismo, permite a los usuarios avanzar a través de diferentes niveles (alfabeto, números, colores), brindándoles la oportunidad de mejorar gradualmente sus habilidades en el lenguaje de señas.

# Instalación
1.	Acceder al repositorio público de GitHub: https://github.com/jaionecherres/Sign-Detector.git
2.	Extraer los archivos en una carpeta nueva de su directorio.
3.	Abra una terminal de comandos en el directorio donde creó la carpeta, dentro de la carpeta se deben de visualizar los archivos del repositorio.

4.	Cree y active un entorno virtual con los siguientes comandos:
    `py -m venv ent_uni`
    `.\ent_uni\Scripts\activate`

5.	Instale las dependencias necesarias:
   
    `pip install -r requerimientos.txt`

# Configuración de variables de entorno
6.	En el directorio raíz del proyecto cree un archivo .env, comando:
    `touch .env`
7.	Abra el archivo .env y añada las siguientes variables con los valores correspondientes para la base de datos:
    Ejemplo:
  	
    `DB_ENGINE=django.db.backends.postgresql`
  	
    `DB_DATABASE=nombre_basedatos`
  	
    `DB_USERNAME=usuario`
  	
    `DB_PASSWORD=contraseña`
  	
    `DB_SOCKET=localhost`
  	
    `DB_PORT=5432`

# Aplicación de migraciones
8.	Revisar que el entorno virtual esté activo
9.	En la terminal ejecutar el siguiente comando para crear las migraciones en la base de datos:
    
    `py manage.py makemigrations`
  	
    `py manage.py migrate`

# Creación del superusuario
10.	En la terminal ejecute el siguiente comando:
    
    `py manage.py createsuperuser`
11.	Ingrese la información que se solicita
12.	Confirme la creación del superusuario

# Correr el servidor de desarrollo
13.	Para iniciar el servidor ingrese el siguiente comando:
    
    `py manage.py runserver`

# Uso
14.	Abra el navegador web y navegue a la dirección proporcionada http://127.0.0.1:8000/ 
15.	Para acceder al panel de administración añada lo siguiente: http://127.0.0.1:8000/admin, inicie sesión con el superusuario creado.

