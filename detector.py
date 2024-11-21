import numpy as np
import pyautogui
import time
from PIL import ImageGrab
import cv2
import keyboard
import logging
import sys
import traceback
from pygame import mixer
import os
from datetime import datetime
from src.status_detector_config import StatusDetectorConfig
from src.status_detector_utilities import StatusDetectorUtilities
from src.alert_manager import AlertManager

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('detector_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    try:
        # Pedir la ruta del archivo de sonido
        sound_path = r"D:\HostLocal\MJCodex\mjc-py-m2-live\store\alarm.mp3"
        pattern_path = r"D:\HostLocal\MJCodex\mjc-py-m2-live\store\pattern.png"
        status_detector_utilities = StatusDetectorUtilities()
        phone_alert = AlertManager()
        
        if not os.path.exists(sound_path):
            raise Exception(f"No se encontró el archivo de sonido en: {sound_path}")
        if not os.path.exists(pattern_path):
            raise Exception(f"No se encontró el archivo de patrón en: {pattern_path}")
        
        detector = StatusDetectorConfig(sound_path, pattern_path)
        
        logging.info("Programa iniciado")
        print("\n=== Detector de barra de vida con alarma ===")
        print("Programa iniciado. Presiona 'q' para salir.")
        print("\nPrimero, necesitamos configurar el área a monitorear...")
        
        # Espera inicial para preparación
        print("\nPreparando captura en 3 segundos...")
        time.sleep(3)
        
        # Captura primera posición
        print("Posiciona el cursor en la primera esquina y espera 3 segundos...")
        time.sleep(3)
        x1, y1 = status_detector_utilities.get_screen_position()
        if x1 is None:
            raise Exception("No se pudo capturar la primera posición")
        print(f"Posición 1 capturada: {x1}, {y1}")
        
        # Captura segunda posición
        print("\nAhora posiciona el cursor en la esquina opuesta y espera 3 segundos...")
        time.sleep(3)
        x2, y2 = status_detector_utilities.get_screen_position()
        if x2 is None:
            raise Exception("No se pudo capturar la segunda posición")
        print(f"Posición 2 capturada: {x2}, {y2}")
        
        print("\n¡Monitoreo iniciado! Presiona 'q' para detener.")
        logging.info("Iniciando bucle de monitoreo")
        
        while True:
            screenshot_array = status_detector_utilities.get_screenshot_array(x1, y1, x2, y2)
            is_alive_pattern = status_detector_utilities.find_partial_pattern(screenshot_array, detector.pattern)


            # Guardar imágenes para depuración
            cv2.imwrite("last_screenshot.png", screenshot_array)
            cv2.imwrite("pattern.png", detector.pattern_original)

            # Obtén la fecha y hora actual
            now = datetime.now()

            # Formatea la fecha y hora
            now_format = now.strftime("%Y-%m-%d %I:%M %p")

            if is_alive_pattern:
                print(f"{now_format} ¡Personaje vivo! ✓")
                detector.stop_alarm()
            else:
                phone_alert.send_phone_alert("METIN2", "Personaje muerto!!!")
                print(f"{now_format} ¡PERSONAJE MUERTO! ⚠")
                detector.play_alarm()
            
            # Verifica si se presionó 'q'
            if keyboard.is_pressed('q'):
                print("\nPrograma terminado por el usuario")
                logging.info("Programa terminado por el usuario")
                break
            debounce_time = 30 if is_alive_pattern else 5   
            time.sleep(debounce_time)  # Espera entre escaneos
            
    except Exception as e:
        error_msg = f"Error en la ejecución: {str(e)}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        print(f"\nERROR: {error_msg}")
        print("Consulta el archivo 'detector_debug.log' para más detalles")
        input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()