import time
import threading
from PIL import Image
from typing import List
import base64
from io import BytesIO

from src.pattern_registry import PatternRegistry
from src.pattern_detector import PatternDetector
from src.status_detector_utilities import StatusDetectorUtilities
from src.alert_manager import AlertManager
from src.global_console import GlobalConsole
from src.pushbullet_listener import PushbulletListener
from src.target_character import TargetCharacter
from src.sound_manager import SoundManager
from src.screen_capture import ScreenCapture

class AppUI:
    def __init__(self, root, refresh_targets_view_fn=None):
        self.root = root
        self.refresh_targets_view_fn = refresh_targets_view_fn
        SoundManager.get_instance()

        # Inicializar sistema de patrones
        self.pattern_registry = PatternRegistry.get_instance()
        self.pattern_detector = PatternDetector()
        
        # Variable para controlar el monitoreo
        self.is_monitoring = False
        self.monitoring_thread = None
        self.target_characters: List[TargetCharacter] = []

        # Escuchar peticiones remotas
        remote_listener = PushbulletListener()
        remote_listener.start()
        
        GlobalConsole.log(f"✓ Sistema iniciado. Patrones disponibles: {self.pattern_registry.get_all_pattern_types()}")

    def web_add_target_character(self, pattern_types: List[str] = None):
        """
        Agrega un nuevo personaje objetivo con captura de área.
        
        Args:
            pattern_types: Lista de patrones a monitorear (por defecto: ['is_alive'])
        """
        if pattern_types is None:
            pattern_types = ['is_alive']  # Patrón por defecto
        
        capture_tool = ScreenCapture()
        area = capture_tool.run()
        
        if area:
            start_x, start_y, end_x, end_y = area
            
            # Validar que los patrones existen
            for pattern_type in pattern_types:
                if not self.pattern_registry.pattern_exists(pattern_type):
                    GlobalConsole.log(f"⚠ Patrón desconocido: '{pattern_type}'")
                    return False
            
            target = TargetCharacter(
                start_x=start_x,
                start_y=start_y,
                end_x=end_x,
                end_y=end_y,
                pattern_types=pattern_types,
                name=f"Personaje {len(self.target_characters) + 1}"
            )
            
            self.target_characters.append(target)
            GlobalConsole.log(f"✓ Personaje agregado con patrones: {pattern_types}")
            return True
        
        return False

    @staticmethod
    def get_area_image_b64(area):
        """Obtiene imagen base64 del área de un personaje"""
        try:
            status_detector_utilities = StatusDetectorUtilities()
            screenshot_array = status_detector_utilities.get_screenshot_array(
                area.start_x, area.start_y, area.end_x, area.end_y
            )
            image = Image.fromarray(screenshot_array)
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_b64 = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
            return img_b64
        except Exception:
            return None

    def delete_target_character(self, index):
        """Elimina un personaje de la lista"""
        if 0 <= index < len(self.target_characters):
            deleted = self.target_characters.pop(index)
            GlobalConsole.log(f"✓ Personaje eliminado: {deleted.name}")
            self.refresh_targets_view_fn()
        else:
            GlobalConsole.log(f"⚠ Índice inválido: {index}")

    def monitoring_loop(self):
        """
        Bucle principal de monitoreo.
        Ahora es genérico y funciona con cualquier cantidad de patrones.
        """
        phone_alert = AlertManager()
        sound_manager = SoundManager.get_instance()

        while self.is_monitoring:
            try:
                # Detectar todos los patrones de todos los personajes
                all_results = self.pattern_detector.detect_multiple_characters(
                    self.target_characters
                )
                
                # Enviar alertas si hay problemas
                self._process_detection_results(all_results, phone_alert, sound_manager)
                
                # Determinar tiempo de espera
                any_alarm = any(result['alarmed'] for result in all_results)
                debounce_time = 30 if any_alarm else 60
                
                self.wait_with_monitoring_check(debounce_time)
                    
            except Exception as e:
                GlobalConsole.log(f"❌ Error en el monitoreo: {e}")
                time.sleep(5)

        # Detener alarma al finalizar
        sound_manager.stop()

    def _process_detection_results(self, results, phone_alert, sound_manager):
        """
        Procesa los resultados de detección y envía alertas si es necesario.
        """
        # Filtrar solo las alarmas activas
        alarmed_results = [r for r in results if r['alarmed']]
        
        if alarmed_results:
            # Construir mensaje de alerta
            alert_text = '\n'.join([
                f"{r['date']}: {r['message']}" 
                for r in alarmed_results
            ])
            
            # Enviar alerta telefónica
            phone_alert.send_phone_alert("METIN2", alert_text)
            GlobalConsole.log(f"🚨 ALERTAS:\n{alert_text}")
            
            # Reproducir alarma (usa el sonido del primer patrón alarmado)
            first_pattern = alarmed_results[0]['pattern_type']
            pattern_config = self.pattern_registry.get_pattern(first_pattern)
            sound_manager.play(pattern_config['sound'])
        else:
            # Todo OK
            GlobalConsole.log("✓ Todos los personajes OK")
            sound_manager.stop()
        
        # Refrescar vista
        if self.refresh_targets_view_fn:
            self.refresh_targets_view_fn()

    def wait_with_monitoring_check(self, seconds):
        """Espera verificando periódicamente si debe continuar"""
        for _ in range(seconds):
            if not self.is_monitoring:
                break
            time.sleep(1)

    def toggle_monitoring(self):
        """Inicia o detiene el monitoreo"""
        if not self.target_characters:
            GlobalConsole.log("⚠ No hay personajes para monitorear")
            return

        if not self.is_monitoring:
            # Iniciar monitoreo
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                GlobalConsole.log("⏳ Esperando a que termine el monitoreo anterior...")
                return

            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            GlobalConsole.log("▶ Monitoreo iniciado")
        else:
            # Detener monitoreo
            self.is_monitoring = False
            sound_manager = SoundManager.get_instance()
            sound_manager.stop()
            GlobalConsole.log("⏸ Monitoreo detenido")
    
    # ========== MÉTODOS DE UTILIDAD ==========
    
    def get_available_patterns(self):
        """Retorna lista de patrones disponibles (útil para UI)"""
        return self.pattern_registry.get_all_pattern_types()
    
    def add_pattern_to_character(self, character_index: int, pattern_type: str):
        """Agrega un patrón a un personaje existente"""
        if 0 <= character_index < len(self.target_characters):
            character = self.target_characters[character_index]
            if self.pattern_registry.pattern_exists(pattern_type):
                character.add_pattern(pattern_type)
                GlobalConsole.log(f"✓ Patrón '{pattern_type}' agregado a {character.name}")
                return True
            else:
                GlobalConsole.log(f"⚠ Patrón desconocido: '{pattern_type}'")
        return False
    
    def remove_pattern_from_character(self, character_index: int, pattern_type: str):
        """Elimina un patrón de un personaje"""
        if 0 <= character_index < len(self.target_characters):
            character = self.target_characters[character_index]
            character.remove_pattern(pattern_type)
            GlobalConsole.log(f"✓ Patrón '{pattern_type}' eliminado de {character.name}")
            return True
        return False