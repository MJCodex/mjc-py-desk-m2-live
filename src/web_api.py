from src.global_console import GlobalConsole
import webview
from pathlib import Path
import tkinter as tk
from src.screen_capture import ScreenCapture
from src.app_ui import AppUI
import sys
from src.target_character import TargetCharacter

def web_refresh_targets_view():
    if webview.windows:
        webview.windows[0].evaluate_js("getTargets()")

app_ui = AppUI(None, refresh_targets_view_fn=web_refresh_targets_view)

def web_log_handler(msg):
    if webview.windows:
        webview.windows[0].evaluate_js(f"appendLog({repr(msg)})")

GlobalConsole.set_web_handler(web_log_handler)

class WebApi:
    def add_target(self):
        root = tk.Tk()
        root.withdraw()  # Oculta la ventana principal de Tkinter
        area = ScreenCapture(root).run()
        root.destroy()
        if area:
            start_x, start_y, end_x, end_y = area
            target = TargetCharacter(
                start_x = start_x,
                start_y = start_y,
                end_x = end_x,
                end_y = end_y,
                pattern_type = 'is_alive'
            )
            app_ui.web_add_target_character(target)
            return True
        return False
    
    def get_targets(self):
        # Devuelve la lista de áreas monitoreadas con imagen en base64
        result = []
        for area in app_ui.target_characters:
            img_b64 = AppUI.get_area_image_b64(area)
            result.append({
                'start_x': area.start_x,
                'start_y': area.start_y,
                'end_x': area.end_x,
                'end_y': area.end_y,
                'img_b64': img_b64,
                'pattern_type': area.pattern_type
            })
        return result

    def update_target_pattern(self, index, new_pattern):
        try:
            app_ui.target_characters[index].pattern_type = new_pattern
            GlobalConsole.log(f"Patrón del objetivo {index} actualizado a {new_pattern}")
            return True
        except Exception:
            return False

    def toggle_monitoring(self):
        app_ui.toggle_monitoring()

    def delete_target(self, idx):
        try:
            self.last_target_character_will_be_deleted()
            app_ui.delete_target_character(idx)
            return True
        except Exception:
            return False
    
    def last_target_character_will_be_deleted(self):
        if len(app_ui.target_characters) == 1 and app_ui.is_monitoring and webview.windows:
            GlobalConsole.log("No quedan áreas para monitorear. Deteniendo el monitoreo.")
            app_ui.toggle_monitoring()
            webview.windows[0].evaluate_js("monitoringStatusChanged(false)")

    def close_app(self):
        if webview.windows:
            webview.windows[0].destroy()

def launch_web_ui():
    """Lanza la interfaz HTML usando pywebview en una ventana nueva."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller: usar ruta temporal
        html_path = Path(sys._MEIPASS) / 'src' / 'ui' / 'index.html'
    else:
        html_path = Path(__file__).parent / 'ui' / 'index.html'
    webview.create_window('M2 Monitor',
                          html_path.resolve().as_uri(),
                          frameless=True,
                          width=500,
                          height=650,
                          js_api=WebApi())
    webview.start()

if __name__ == "__main__":
    launch_web_ui()