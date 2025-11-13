import threading
import websocket
import json
import os
import time
import requests
from src.global_console import GlobalConsole
from src.screenshot_manager import ScreenshotManager
from src.constants import command_actions

class PushbulletListener:
    def __init__(self):
        self.api_key = os.getenv("PUSHBULLET_API_KEY")
        if not self.api_key:
            raise ValueError("PUSHBULLET_API_KEY no está configurada en las variables de entorno")
        
        self.last_timestamp = None
        self.running = False
        self.websocket_url = f"wss://stream.pushbullet.com/websocket/{self.api_key}"
        self.api_url = "https://api.pushbullet.com/v2"
        self.ws = None
        self.reconnect_delay = 5
        self.thread = None

    def get_latest_push(self):
        """Obtiene solo el push más reciente via API REST."""
        headers = {
            'Access-Token': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            # Pedimos solo 1 push ordenado por modified descendente
            params = {
                'limit': 1,
                'modified_after': self.last_timestamp if self.last_timestamp else 0
            }

            response = requests.get(
                f"{self.api_url}/pushes",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            pushes = response.json()
            
            if pushes.get('pushes') and len(pushes['pushes']) > 0:
                latest_push = pushes['pushes'][0]
                self.last_timestamp = latest_push.get('modified', self.last_timestamp)
                return latest_push
                
        except Exception as e:
            GlobalConsole.log(f"Error obteniendo último push: {str(e)}")
        return None

    def process_command(self, command):
        """Procesa un comando recibido desde Pushbullet."""
        command = command.strip().lower()
        try:
            if command == command_actions.take_screenshot.command:
                GlobalConsole.log(f"Procesando comando: {command_actions.take_screenshot.command}")
                alert_manager = ScreenshotManager()
                alert_manager.capture_and_send()
        except Exception as e:
            GlobalConsole.log(f"Error procesando comando: {str(e)}")

    def _create_websocket(self):
        """Crea y configura una nueva instancia de WebSocket."""
        websocket.enableTrace(True)
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                # Si es un tickle de tipo push, buscamos el último push
                if data.get('type') == 'tickle' and data.get('subtype') == 'push':
                    latest_push = self.get_latest_push()
                    
                    if latest_push:
                        
                        # Procesar solo si está activo y tiene body
                        if not latest_push.get('dismissed') and latest_push.get('body'):
                            command = latest_push['body']                            
                            self.process_command(command)
                    else:
                        GlobalConsole.log("No se encontraron nuevos pushes")
                
                # Si es un push directo (menos común)
                elif data.get('type') == 'push' and data.get('push'):
                    push = data['push']
                    GlobalConsole.log(f"Push directo recibido: {json.dumps(push, indent=2)}")
                    
                    if push.get('body'):
                        self.process_command(push['body'])

            except json.JSONDecodeError as e:
                GlobalConsole.log(f"Error decodificando mensaje: {str(e)}")
            except Exception as e:
                GlobalConsole.log(f"Error en on_message: {str(e)}")

        def on_error(ws, error):
            GlobalConsole.log(f"Error en WebSocket: {str(error)}")

        def on_close(ws, close_status_code, close_msg):
            GlobalConsole.log(f"Conexión WebSocket cerrada: {close_status_code} - {close_msg}")
            if self.running:
                GlobalConsole.log(f"Intentando reconexión en {self.reconnect_delay} segundos...")
                time.sleep(self.reconnect_delay)
                self.reconnect()

        def on_open(ws):
            GlobalConsole.log("Conexión WebSocket abierta")

        return websocket.WebSocketApp(
            self.websocket_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

    def listen_via_websocket(self):
        """Escucha comandos usando WebSocket para notificaciones en tiempo real."""
        while self.running:
            try:
                self.ws = self._create_websocket()
                self.ws.run_forever()
                if not self.running:
                    break
                GlobalConsole.log("Conexión perdida, reconectando...")
                time.sleep(self.reconnect_delay)
            except Exception as e:
                GlobalConsole.log(f"Error en listen_via_websocket: {str(e)}")
                if self.running:
                    time.sleep(self.reconnect_delay)

    def reconnect(self):
        """Intenta reconectar el WebSocket."""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.ws = None
        if self.running:
            self.listen_via_websocket()

    def start(self):
        """Inicia el escuchador en un hilo separado."""
        if self.thread and self.thread.is_alive():
            GlobalConsole.log("El escuchador ya está corriendo")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self.listen_via_websocket, daemon=True)
        self.thread.start()
        GlobalConsole.log("Escuchador iniciado")

    def stop(self):
        """Detiene el escuchador."""
        self.running = False
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.ws = None
        if self.thread:
            self.thread.join(timeout=5)
        GlobalConsole.log("Escuchador detenido")

    def is_running(self):
        """Verifica si el escuchador está activo."""
        return self.running and self.thread and self.thread.is_alive()