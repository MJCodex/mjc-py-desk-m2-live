import time
from src.global_console import GlobalConsole
from src.pushbullet_base import PushbulletBase

class AlertManager(PushbulletBase):
    def __init__(self):
        super().__init__()
        self.last_push_notification = 0
        self.push_notification_delay = 30
    
    def should_send_push(self):
        current_time = time.time()
        if current_time - self.last_push_notification >= self.push_notification_delay:
            self.last_push_notification = current_time
            return True
        return False
    
    def send_phone_alert(self, titulo, mensaje):
        if not self.should_send_push():
            GlobalConsole.log("Esperando tiempo de delay antes de enviar nueva notificación...")
            return
        
        if self.pb is None:
            GlobalConsole.log("No hay conexión válida con Pushbullet")
            return
        
        try:
            self.pb.push_note(titulo, mensaje)
            GlobalConsole.log("Alerta enviada exitosamente!")
        except Exception as e:
            GlobalConsole.log(f"Error al enviar la alerta: {str(e)}")