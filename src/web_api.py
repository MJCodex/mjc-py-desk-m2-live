from src.global_console import GlobalConsole
from src.app_ui import AppUI
import webview

class WebApi:
    def __init__(self, app_ui):
        self.app_ui = app_ui

    def add_target(self):
        result = self.app_ui.web_add_target_character()
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
                'pattern_type': area.pattern_type,
                'name': area.name
            })
        return result

    def update_target_pattern(self, index, new_pattern):
        try:
            self.app_ui.target_characters[index].pattern_type = new_pattern
            GlobalConsole.log(f"Patrón del objetivo {index} actualizado a {new_pattern}")
            return True
        except Exception:
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

    def last_target_character_will_be_deleted(self):
        if len(self.app_ui.target_characters) == 1 and self.app_ui.is_monitoring and webview.windows:
            GlobalConsole.log("No quedan áreas para monitorear. Deteniendo el monitoreo.")
            self.app_ui.toggle_monitoring()
            webview.windows[0].evaluate_js("monitoringStatusChanged(false)")

    def close_app(self):
        if webview.windows:
            webview.windows[0].destroy()
