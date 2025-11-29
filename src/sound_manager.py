from threading import Lock
import logging
import sys
from pygame import mixer

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