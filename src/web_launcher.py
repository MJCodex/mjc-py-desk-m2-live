from pathlib import Path
import webview
import sys
from src.web_api import WebApi
from src.app_ui import AppUI
from src.global_console import GlobalConsole

def web_refresh_targets_view():
    if webview.windows:
        webview.windows[0].evaluate_js("getTargets()")

def web_log_handler(msg):
    if webview.windows:
        webview.windows[0].evaluate_js(f"appendLog({repr(msg)})")

def launch_web_ui():
    """Lanza la interfaz HTML usando pywebview."""
    app_ui = AppUI(None, refresh_targets_view_fn=web_refresh_targets_view)
    GlobalConsole.set_web_handler(web_log_handler)
    web_api = WebApi(app_ui)

    if hasattr(sys, '_MEIPASS'):
        html_path = Path(sys._MEIPASS) / 'src' / 'ui' / 'index.html'
    else:
        html_path = Path(__file__).parent / 'ui' / 'index.html'

    webview.create_window(
        title='M2 Monitor',
        url=html_path.resolve().as_uri(),
        frameless=True,
        width=500,
        height=650,
        js_api=web_api
    )
    webview.start()
