from pushbullet import Pushbullet
import time
import os
from src.global_console import GlobalConsole

class AlertManager:
    def __init__(self):
        self.last_push_notification = 0
        self.push_notification_delay = 20  # Segundos entre notificaciones
        self.API_KEY = os.getenv("PUSHBULLET_API_KEY")
        GlobalConsole.log("API_KEY cargado correctamente")
        self.config_connection()
        
    def should_send_push(self):
        current_time = time.time()
        if current_time - self.last_push_notification >= self.push_notification_delay:
            self.last_push_notification = current_time
            return True
        return False
    
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

    def send_phone_alert(self,titulo, mensaje):
        # Verificar si podemos enviar la notificación
        if not self.should_send_push():
            GlobalConsole.log("Esperando tiempo de delay antes de enviar nueva notificación...")
            return
        
        # Verificar si tenemos una conexión válida con Pushbullet
        if self.pb is None:
            GlobalConsole.log("No hay conexión válida con Pushbullet")
            return
        
        try:
            self.pb.push_note(titulo, mensaje)
            GlobalConsole.log("Alerta enviada exitosamente!")
        except Exception as e:
            GlobalConsole.log(f"Error al enviar la alerta: {str(e)}")