import os
from src.global_console import GlobalConsole
from pushbullet import Pushbullet

class PushbulletBase:
    def __init__(self):
        self.API_KEY = os.getenv("PUSHBULLET_API_KEY")
        self.config_connection()
    
    def config_connection(self):
        if not self.API_KEY:
            GlobalConsole.log("PUSHBULLET_API_KEY no está configurado en las variables de entorno.")
            self.pb = None
            return
        
        try:
            self.pb = Pushbullet(self.API_KEY)
            GlobalConsole.log("Conexión con Pushbullet establecida exitosamente!")
        except Exception as e:
            GlobalConsole.log(f"Error al inicializar Pushbullet: {str(e)}")
            self.pb = None