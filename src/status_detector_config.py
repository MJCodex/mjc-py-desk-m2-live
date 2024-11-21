import logging
from pygame import mixer
import sys
import cv2

class StatusDetectorConfig:
    def __init__(self, sound_path, pattern_path):
        self.sound_path = sound_path
        self.pattern_path = pattern_path
        self.setup_sound()
        self.setup_pattern()
        
    def setup_sound(self):
        #Inicializa el sistema de sonido
        try:
            mixer.init()
            self.alarm_sound = mixer.Sound(self.sound_path)
            logging.info("Sistema de sonido inicializado correctamente")
        except Exception as e:
            logging.error(f"Error al inicializar el sonido: {str(e)}")
            print("Error al cargar el sonido. Verificar archivo de audio.")
            sys.exit(1)

    def setup_pattern(self):
        #Carga el patrón para matching
        try:
            # Cargar imagen en color
            self.pattern_original = cv2.imread(self.pattern_path)

            self.pattern = cv2.cvtColor(self.pattern_original, cv2.COLOR_BGR2GRAY)
            if self.pattern is None:
                raise Exception("No se pudo cargar el patrón")
            logging.info("Patrón cargado correctamente")
        except Exception as e:
            logging.error(f"Error al cargar el patrón: {str(e)}")
            print("Error al cargar el patrón de imagen. Verificar archivo.")
            sys.exit(1)

    def play_alarm(self):
        #Reproduce el sonido de alarma
        try:
            self.alarm_sound.stop()
            self.alarm_sound.play()
        except Exception as e:
            logging.error(f"Error al reproducir el sonido: {str(e)}")

    def stop_alarm(self):
        #Reproduce el sonido de alarma
        try:
            self.alarm_sound.stop()
        except Exception as e:
            logging.error(f"Error al terminar el sonido: {str(e)}")
