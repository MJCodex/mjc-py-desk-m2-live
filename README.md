# mjc-py-desk-m2-live

### Descripción de la aplicación
Este es un Detector de Estado de Personaje diseñado para monitorear la barra de vida de un personaje en un juego, detectar su estado (vivo o muerto) y alertar al usuario en caso de que el personaje esté muerto. La aplicación captura y procesa la pantalla para buscar un patrón específico que representa la barra de vida del personaje y, si detecta que el personaje está muerto, se emite una alerta sonora y se envía una notificación a un teléfono móvil. Además, la aplicación permite la configuración del área de captura y proporciona una interfaz simple para iniciar y detener el monitoreo.

### Características
- **Monitoreo de barra de vida:** La aplicación captura áreas específicas de la pantalla para detectar el estado del personaje en base a un patrón visual (la barra de vida).
- **Alerta sonora:** Si el personaje muere, se reproduce una alarma sonora.
- **Notificación móvil:** En caso de que el personaje muera, se envía una alerta a un teléfono móvil usando la clase AlertManager.
- **Interfaz interactiva:** Permite al usuario configurar el área de monitoreo posicionando el cursor en dos puntos de la pantalla.
- **Depuración:** Se guarda la captura de pantalla y el patrón de búsqueda para facilitar la depuración del proceso de detección.

### Requisitos
- **Python 3.x:** Se necesita tener Python instalado para ejecutar la aplicación.
- **Dependencias:** Las dependencias necesarias están listadas en el archivo requirements.txt y deben instalarse mediante pip.
    - Librerías adicionales:
    - numpy
    - pyautogui
    - PIL (Pillow)
    - opencv-python
    - keyboard
    - pygame
    - logging

## Entorno de desarrollo

- Clonar repositorio
- Tener python instalado
- Crear entorno virtual `python -m venv venv`
- Activar entorno virtual `source venv/bin/activate`
- Instalar dependencias `pip install -r requirements.txt`
- Iniciar instancia `python detector.py`
- Generar instalador `pyinstaller --onefile detector.py`

## Uso Makefile
- Instalar choco desde powershell con permisos de administrador `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`
- Instalar make `choco install make`
- Usar comandos de Makefile ejemplo: `make run`

## Configuración notificación móvil
- Crear una cuenta en `https://www.pushbullet.com/`
- Generar un `Access Tokens`
- Agregar variable de entorno en el SO `PUSHBULLET_API_KEY` con el valor del `Access Tokens`
- Instalar `Pushbullet Android app` desde la Play Store
- Loguear la cuenta anteriormente creada