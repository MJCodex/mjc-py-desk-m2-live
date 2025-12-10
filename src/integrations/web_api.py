from src.core.global_console import GlobalConsole
from src.app_ui import AppUI
import webview

class WebApi:
    def __init__(self, app_ui):
        self.app_ui = app_ui

    def add_target(self):
        result = self.app_ui.web_add_target_character(pattern_types=['is_alive'])
        return result

    def get_targets(self):
        result = []
        for area in self.app_ui.target_characters:
            img_b64 = AppUI.get_area_image_b64(area)
            result.append({
                'start_x': area.start_x,
                'start_y': area.start_y,
                'end_x': area.end_x,
                'end_y': area.end_y,
                'img_b64': img_b64,
                'pattern_types': area.pattern_types,
                'patterns_config': area.patterns_config,
                'name': area.name
            })
        return result
    
    def add_pattern_to_character(self, index, pattern_type, config=None):
        """Agrega un patrón a un character con configuración opcional"""
        try:
            if not self.app_ui.add_pattern_to_character(index, pattern_type):
                return False
            
            # Aplicar configuración personalizada si se proporciona
            if config:
                character = self.app_ui.target_characters[index]
                character.set_pattern_config(pattern_type, config)
                GlobalConsole.log(f"Configuración de '{pattern_type}' actualizada: {config}")
            
            return True
        except Exception as e:
            GlobalConsole.log(f"Error al agregar patrón: {e}")
            return False
    
    def remove_pattern_from_character(self, index, pattern_type):
        """Elimina un patrón de un character"""
        try:
            return self.app_ui.remove_pattern_from_character(index, pattern_type)
        except Exception as e:
            GlobalConsole.log(f"Error al eliminar patrón: {e}")
            return False
    
    def update_pattern_config(self, index, pattern_type, config_key, config_value):
        """Actualiza un valor de configuración de un patrón específico"""
        try:
            character = self.app_ui.target_characters[index]
            character.update_pattern_config_value(pattern_type, config_key, config_value)
            return True
        except Exception as e:
            GlobalConsole.log(f"Error al actualizar configuración del patrón: {e}")
            return False

    def update_target_name(self, index, new_name):
        try:
            old_name = self.app_ui.target_characters[index].name
            if old_name != new_name:
                self.app_ui.target_characters[index].name = new_name
                GlobalConsole.log(f"Nombre del objetivo {index} actualizado a {new_name}")
            return True
        except Exception:
            return False

    def toggle_monitoring(self):
        self.app_ui.toggle_monitoring()

    def delete_target(self, idx):
        try:
            self.last_target_character_will_be_deleted()
            self.app_ui.delete_target_character(idx)
            return True
        except Exception:
            return False
    
    def get_available_patterns(self):
        """Retorna todos los patrones disponibles del registro"""
        return self.app_ui.get_available_patterns()

    def last_target_character_will_be_deleted(self):
        if len(self.app_ui.target_characters) == 1 and self.app_ui.is_monitoring and webview.windows:
            GlobalConsole.log("No quedan áreas para monitorear. Deteniendo el monitoreo.")
            self.app_ui.toggle_monitoring()
            webview.windows[0].evaluate_js("monitoringStatusChanged(false)")

    def close_app(self):
        if webview.windows:
            webview.windows[0].destroy()
