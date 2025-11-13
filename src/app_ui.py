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
from src.screen_capture import ScreenCapture
import tkinter as tk

class AppUI:
    def __init__(self, root, refresh_targets_view_fn=None):
        self.root = root
        self.refresh_targets_view_fn = refresh_targets_view_fn

        # Cargar recursos
        self.detector_alive = None
        self.detector_online = None
        self.load_stored_recources()

        # Variable para controlar el monitoreo
        self.is_monitoring = False
        self.monitoring_thread = None
        self.target_characters: List[TargetCharacter] = []

        # Escuchar peticiones remotas
        remote_listener = PushbulletListener()
        remote_listener.start()

    def web_add_target_character(self):
        capture_tool = ScreenCapture()
        area = capture_tool.run()
        if area:
            start_x, start_y, end_x, end_y = area
            target = TargetCharacter(
                start_x = start_x,
                start_y = start_y,
                end_x = end_x,
                end_y = end_y,
                pattern_type = 'is_alive'
            )
            self.target_characters.append(target)
            return True
        return False

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

        self.detector_alive = StatusDetectorConfig(self.sound_path, self.pattern_path)
        self.detector_online = StatusDetectorConfig(self.sound_path, self.is_online_pattern)
        
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
        phone_alert = AlertManager()

        while self.is_monitoring:
            try:
                alarmed_characters = []

                for character in self.target_characters:
                    if (character.pattern_type == 'is_alive'):
                        self.is_alive_character(character, status_detector_utilities, alarmed_characters)
                    
                    elif (character.pattern_type == 'is_online'):
                        self.is_online_character(character, status_detector_utilities, alarmed_characters)

                self.send_all_alerts(alarmed_characters, phone_alert)
                any_alarm = any(char['alarmed'] for char in alarmed_characters)
                debounce_time = 30 if any_alarm else 60

                self.wait_with_monitoring_check(debounce_time)
                    
            except Exception as e:
                print(f"Error en el monitoreo: {e}")
                time.sleep(5)  # Esperar antes de reintentar en caso de error

        # Asegurarse de que la alarma se detenga al finalizar
        sound_manager = SoundManager()
        sound_manager.stop()

    def wait_with_monitoring_check(self, seconds):
        """Espera una cantidad de segundos, verificando si debe continuar monitoreando"""
        for _ in range(seconds):
            if not self.is_monitoring:
                break
            time.sleep(1)


    def send_all_alerts(self, alarmed_characters, phone_alert):
        all_text = ''
        for alarm_info in alarmed_characters:
            if alarm_info['alarmed'] == True:
                all_text += f"{alarm_info['date']}: {alarm_info['message']}\n"

        if all_text:
            phone_alert.send_phone_alert("METIN2", all_text)
            GlobalConsole.log(f"{all_text}")
            self.detector_online.play_alarm()
        else:
            GlobalConsole.log("Todos los personajes ok ✓")
            self.detector_online.stop_alarm()

    def is_online_character(self, character, status_detector_utilities, alarmed_characters):
        screenshot_array = status_detector_utilities.get_screenshot_array(character.start_x, character.start_y, character.end_x, character.end_y)
        is_pattern_detected = status_detector_utilities.find_partial_pattern(screenshot_array, self.detector_online.pattern)

        now = datetime.now()
        now_format = now.strftime("%Y-%m-%d %I:%M %p")
        message = "¡Personaje conectado! ✓" if is_pattern_detected else f"¡PERSONAJE {character.name} DESCONECTADO! ⚠"

        alarmed_characters.append({
            'alarmed': not is_pattern_detected,
            'message': message,
            'name': character.name,
            'date': now_format
        })

        self.refresh_targets_view_fn()

    def is_alive_character(self, character, status_detector_utilities, alarmed_characters):
        screenshot_array = status_detector_utilities.get_screenshot_array(character.start_x, character.start_y, character.end_x, character.end_y)
        is_pattern_detected = status_detector_utilities.find_partial_pattern(screenshot_array, self.detector_alive.pattern)

        now = datetime.now()
        now_format = now.strftime("%Y-%m-%d %I:%M %p")
        message = "¡Personaje vivo! ✓" if is_pattern_detected else f"¡PERSONAJE {character.name} MUERTO! ⚠"

        alarmed_characters.append({
            'alarmed': not is_pattern_detected,
            'message': message,
            'name': character.name,
            'date': now_format
        })

        self.refresh_targets_view_fn()

    def toggle_monitoring(self):
        if not self.target_characters:
            GlobalConsole.log("Selecciona el área a monitorear")
            return

        if not self.is_monitoring:
            # Iniciar monitoreo SOLO si no hay un hilo activo
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                GlobalConsole.log("Esperando a que termine el monitoreo anterior...")
                return

            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
            self.monitoring_thread.daemon = True  # El hilo se detendrá cuando se cierre la aplicación
            self.monitoring_thread.start()
        else:
            # Detener monitoreo
            self.is_monitoring = False
            sound_manager = SoundManager()
            sound_manager.stop()
            GlobalConsole.log("Monitoreo detenido.")