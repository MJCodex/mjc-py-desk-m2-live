import sys
import os
from src.status_detector_config import StatusDetectorConfig
from src.status_detector_utilities import StatusDetectorUtilities
from src.alert_manager import AlertManager
import time
from datetime import datetime
import threading
from PIL import Image
from src.global_console import GlobalConsole
from src.pushbullet_listener import PushbulletListener
from src.target_character import TargetCharacter
from typing import List
import base64
from io import BytesIO
from src.status_detector_config import SoundManager

class AppUI:
    def __init__(self, root, refresh_targets_view_fn=None):
        self.root = root
        self.refresh_targets_view_fn = refresh_targets_view_fn

        # Cargar recursos
        self.load_stored_recources()

        # Variable para controlar el monitoreo
        self.is_monitoring = False
        self.monitoring_thread = None
        self.target_characters: List[TargetCharacter] = []

        # Escuchar peticiones remotas
        remote_listener = PushbulletListener()
        remote_listener.start()

    def web_add_target_character(self, character: TargetCharacter):
        # Agregar área directamente (usado por WebApi)
        self.target_characters.append(character)

    @staticmethod
    def get_area_image_b64(area):
        try:
            status_detector_utilities = StatusDetectorUtilities()
            screenshot_array = status_detector_utilities.get_screenshot_array(area.start_x, area.start_y, area.end_x, area.end_y)
            image = Image.fromarray(screenshot_array)
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_b64 = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
            return img_b64
        except Exception:
            return None

    def load_stored_recources(self):
        if getattr(sys, 'frozen', False):
            # Usar sys._MEIPASS directamente para recursos
            self.pattern_path = os.path.join(sys._MEIPASS, 'store', 'pattern.png')
            self.is_online_pattern = os.path.join(sys._MEIPASS, 'store', 'online_pattern.png')
            self.sound_path = os.path.join(sys._MEIPASS, 'store', 'alarm.mp3')
        else:
            # Ruta normal para desarrollo
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            self.pattern_path = os.path.join(parent_dir, 'store', 'pattern.png')
            self.is_online_pattern = os.path.join(parent_dir, 'store', 'online_pattern.png')
            self.sound_path = os.path.join(parent_dir, 'store', 'alarm.mp3')
        
        if not os.path.exists(self.sound_path):
            raise FileNotFoundError(f"No se encontró el archivo de sonido en: {self.sound_path}")
        if not os.path.exists(self.pattern_path):
            raise FileNotFoundError(f"No se encontró el archivo de patrón en: {self.pattern_path}")
        if not os.path.exists(self.is_online_pattern):
            raise FileNotFoundError(f"No se encontró el archivo de patrón online en: {self.is_online_pattern}")

    def delete_target_character(self, index):
        # Eliminar el área de la lista
        del self.target_characters[index]
        
        # Actualizar la vista
        self.refresh_targets_view_fn()

    def monitoring_loop(self):
        status_detector_utilities = StatusDetectorUtilities()

        while self.is_monitoring:
            try:
                alarmed_characters = []
                phone_alert = AlertManager()

                for character in self.target_characters:
                    if (character.pattern_type == 'is_alive'):
                        self.is_alive_character(character, status_detector_utilities, alarmed_characters)

                self.send_all_alerts(alarmed_characters, phone_alert)
                debounce_time = 60 if all(alarmed_characters) else 30   
                time.sleep(debounce_time)
                    
            except Exception as e:
                print(f"Error en el monitoreo: {e}")
                time.sleep(5)  # Esperar antes de reintentar en caso de error

        # Asegurarse de que la alarma se detenga al finalizar
        sound_manager = SoundManager()
        sound_manager.stop()

    def send_all_alerts(self, alarmed_characters, phone_alert):
        all_text = ''
        for alarm_info in alarmed_characters:
            if alarm_info['alarmed']:
                all_text += f"{alarm_info['date']}: {alarm_info['message']}\n"
        phone_alert.send_phone_alert("METIN2", all_text)
        GlobalConsole.log(all_text)

    def is_alive_character(self, character, status_detector_utilities, alarmed_characters):
        detector = StatusDetectorConfig(self.sound_path, self.pattern_path)
        screenshot_array = status_detector_utilities.get_screenshot_array(character.start_x, character.start_y, character.end_x, character.end_y)
        is_pattern_detected = status_detector_utilities.find_partial_pattern(screenshot_array, detector.pattern)

        now = datetime.now()
        now_format = now.strftime("%Y-%m-%d %I:%M %p")
        message = "¡Personaje vivo! ✓" if is_pattern_detected else "¡PERSONAJE MUERTO! ⚠"

        alarmed_characters.append({
            'alarmed': not is_pattern_detected,
            'message': message,
            'date': now_format
        })

        self.refresh_targets_view_fn()

        if is_pattern_detected:
            GlobalConsole.log(f"{now_format} {message}")
            detector.stop_alarm()
        else:
            GlobalConsole.log(f"{now_format} {message}")
            detector.play_alarm()

    def toggle_monitoring(self):
        if not self.target_characters:
            GlobalConsole.log("Selecciona el área a monitorear")
            return

        if not self.is_monitoring:
            # Iniciar monitoreo
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
            self.monitoring_thread.daemon = True  # El hilo se detendrá cuando se cierre la aplicación
            self.monitoring_thread.start()
        else:
            # Detener monitoreo
            self.is_monitoring = False
            sound_manager = SoundManager()
            sound_manager.stop()