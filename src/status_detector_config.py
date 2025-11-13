import logging
from pygame import mixer
import sys
import cv2
from threading import Lock

class SoundManager:
    """Gestor global de sonido (Singleton)"""
    _instance = None
    _lock = Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not SoundManager._initialized:
            try:
                mixer.init()
                self.current_sound = None
                SoundManager._initialized = True
                logging.info("Sistema de sonido inicializado correctamente")
            except Exception as e:
                logging.error(f"Error al inicializar el sonido: {str(e)}")
                print("Error al inicializar el sistema de audio.")
                sys.exit(1)
    
    def play(self, sound):
        """Reproduce un sonido, deteniendo cualquier otro"""
        try:
            if self.current_sound:
                self.current_sound.stop()
            sound.play()
            self.current_sound = sound
        except Exception as e:
            logging.error(f"Error al reproducir el sonido: {str(e)}")
    
    def stop(self):
        """Detiene cualquier sonido en reproducción"""
        try:
            if self.current_sound:
                self.current_sound.stop()
                self.current_sound = None
        except Exception as e:
            logging.error(f"Error al detener el sonido: {str(e)}")
    
    @classmethod
    def get_instance(cls):
        """Obtiene la instancia del SoundManager desde cualquier lugar"""
        return cls()


class StatusDetectorConfig:
    # Gestor de sonido compartido entre todas las instancias
    sound_manager = SoundManager()
    
    def __init__(self, sound_path, pattern_path):
        self.sound_path = sound_path
        self.pattern_path = pattern_path
        self.setup_sound()
        self.setup_pattern()
        
    def setup_sound(self):
        """Carga el archivo de sonido específico de esta instancia"""
        try:
            self.alarm_sound = mixer.Sound(self.sound_path)
            logging.info(f"Sonido cargado: {self.sound_path}")
        except Exception as e:
            logging.error(f"Error al cargar el sonido {self.sound_path}: {str(e)}")
            print(f"Error al cargar el sonido. Verificar archivo: {self.sound_path}")
            sys.exit(1)

    def setup_pattern(self):
        """Carga el patrón para matching"""
        try:
            self.pattern_original = cv2.imread(self.pattern_path)
            self.pattern = cv2.cvtColor(self.pattern_original, cv2.COLOR_BGR2GRAY)
            if self.pattern is None:
                raise FileNotFoundError("No se pudo cargar el patrón")
            logging.info(f"Patrón cargado: {self.pattern_path}")
        except Exception as e:
            logging.error(f"Error al cargar el patrón: {str(e)}")
            print(f"Error al cargar el patrón. Verificar archivo: {self.pattern_path}")
            sys.exit(1)

    def play_alarm(self):
        """Reproduce el sonido de alarma de esta instancia"""
        self.sound_manager.play(self.alarm_sound)

    def stop_alarm(self):
        """Detiene cualquier alarma en reproducción"""
        self.sound_manager.stop()