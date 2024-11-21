from pushbullet import Pushbullet
import time
import os

class AlertManager:
    def __init__(self):
        self.last_push_notification = 0
        self.push_notification_delay = 20  # Segundos entre notificaciones
        self.API_KEY = os.getenv("PUSHBULLET_API_KEY")
        print(f"API_KEY cargado correctamente: {self.API_KEY}")
        self.config_connection()
        
    def should_send_push(self):
        current_time = time.time()
        if current_time - self.last_push_notification >= self.push_notification_delay:
            self.last_push_notification = current_time
            return True
        return False
    
    def config_connection(self):
        if not self.API_KEY:
            print("PUSHBULLET_API_KEY no está configurado en las variables de entorno.")
            self.pb = None
            return
        
        try:
            self.pb = Pushbullet(self.API_KEY)
            print("Conexión con Pushbullet establecida exitosamente!")
        except Exception as e:
            print(f"Error al inicializar Pushbullet: {str(e)}")
            self.pb = None

    def send_phone_alert(self,titulo, mensaje):
        # Verificar si podemos enviar la notificación
        if not self.should_send_push():
            print("Esperando tiempo de delay antes de enviar nueva notificación...")
            return
        
        # Verificar si tenemos una conexión válida con Pushbullet
        if self.pb is None:
            print("No hay conexión válida con Pushbullet")
            return
        
        try:
            self.pb.push_note(titulo, mensaje)
            print("Alerta enviada exitosamente!")
        except Exception as e:
            print(f"Error al enviar la alerta: {str(e)}")