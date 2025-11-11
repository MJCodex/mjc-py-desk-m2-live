from src.global_console import GlobalConsole
import webview
from pathlib import Path
import tkinter as tk
from src.screen_capture import ScreenCapture
from src.app_ui import AppUI

app_ui = AppUI(None)
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
            app_ui.web_add_target_character(area)
            return True
        return False
    
    def get_targets(self):
        # Devuelve la lista de áreas monitoreadas con imagen en base64
        result = []
        for area in app_ui.target_characters:
            start_x, start_y, end_x, end_y = area
            img_b64 = AppUI.get_area_image_b64(area)
            result.append({
                'start_x': start_x,
                'start_y': start_y,
                'end_x': end_x,
                'end_y': end_y,
                'img_b64': img_b64
            })
        return result

    def toggle_monitoring(self):
        app_ui.toggle_monitoring()

def launch_web_ui():
    """Lanza la interfaz HTML usando pywebview en una ventana nueva."""
    html_path = Path(__file__).parent / 'ui' / 'index.html'
    webview.create_window('M2 Monitor', html_path.resolve().as_uri(), js_api=WebApi())
    webview.start()

if __name__ == "__main__":
    launch_web_ui()