import tkinter as tk
from src.screen_capture import ScreenCapture
import sys
import os
from src.status_detector_config import StatusDetectorConfig
from src.status_detector_utilities import StatusDetectorUtilities
from src.alert_manager import AlertManager
import time
from datetime import datetime
import threading
from PIL import Image, ImageTk
from tkinter import scrolledtext
from src.global_console import GlobalConsole
from src.pushbullet_listener import PushbulletListener
from src.target_character import TargetCharacter
from typing import List
import base64
from io import BytesIO

class AppUI:
    def __init__(self, root, refresh_targets_view_fn=None):
        self.root = root
        self.refresh_targets_view_fn = refresh_targets_view_fn or self.show_target_characters
        if self.root is not None:
            self.root.title("M2 Monitor")
            self.root.geometry("400x450")
            self.root.resizable(False, False)
            self.root.attributes("-toolwindow", True)

            # Widgets
            label_frame = tk.Frame(self.root)
            label_frame.pack(pady=5)

            self.label = tk.Label(label_frame, text="Selecciona el área donde se encuentra la barra de vida")
            self.label.pack(side='left', padx=5)

            self.select_button = tk.Button(label_frame, text="Agregar", command=self.add_target_character)
            self.select_button.pack(side='left', padx=5)

            # Frame donde se mostrará la imagen
            self.setup_scrollable_frame()

            self.monitor_button = tk.Button(self.root, text="Iniciar monitoreo", command=self.toggle_monitoring)
            self.monitor_button.pack(pady=10)

            self.console = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=30, width=60, state="disabled", bg="gray20", fg="white")
            self.console.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)
            GlobalConsole.set_console(self.console)

        # Cargar recursos
        self.load_stored_recources()

        # Variable para controlar el monitoreo
        self.is_monitoring = False
        self.monitoring_thread = None
        self.target_characters: List[TargetCharacter] = []

        # Escuchar peticiones remotas
        remote_listener = PushbulletListener()
        remote_listener.start()

    def add_target_character(self):
        # Instancia de la clase
        capture_tool = ScreenCapture(self.root)

        # Capturar coordenadas
        self.target_characters.append(capture_tool.run())

        # Listar personajes monitoreados
        self.show_target_characters()

    def web_add_target_character(self, area):
        # Agregar área directamente (usado por WebApi)
        self.target_characters.append(area)

    @staticmethod
    def get_area_image_b64(area):
        try:
            status_detector_utilities = StatusDetectorUtilities()
            start_x, start_y, end_x, end_y = area
            screenshot_array = status_detector_utilities.get_screenshot_array(start_x, start_y, end_x, end_y)
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
            self.sound_path = os.path.join(sys._MEIPASS, 'store', 'alarm.mp3')
        else:
            # Ruta normal para desarrollo
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            self.pattern_path = os.path.join(parent_dir, 'store', 'pattern.png')
            self.sound_path = os.path.join(parent_dir, 'store', 'alarm.mp3')
        
        if not os.path.exists(self.sound_path):
            raise FileNotFoundError(f"No se encontró el archivo de sonido en: {self.sound_path}")
        if not os.path.exists(self.pattern_path):
            raise FileNotFoundError(f"No se encontró el archivo de patrón en: {self.pattern_path}")

    def show_target_characters(self):
        # Limpiar cualquier widget existente
        for widget in self.target_frame.winfo_children():
            widget.destroy()

        # Crear un frame para las imágenes capturadas
        for i, area in enumerate(self.target_characters):
            # Subframe para cada imagen
            image_frame = tk.Frame(self.target_frame)
            image_frame.pack(fill='x', pady=5)

            # Crear imagen
            status_detector_utilities = StatusDetectorUtilities()
            start_x, start_y, end_x, end_y = area
            screenshot_array = status_detector_utilities.get_screenshot_array(start_x, start_y, end_x, end_y)
            image = Image.fromarray(screenshot_array)
            tk_image = ImageTk.PhotoImage(image)

            # Label para la imagen
            image_label = tk.Label(image_frame, image=tk_image)
            image_label.image = tk_image
            image_label.pack(side='left', padx=5)

            # Botón para eliminar
            delete_button = tk.Button(
                image_frame, 
                text="Eliminar", 
                command=lambda idx=i: self.delete_target_character(idx)
            )
            delete_button.pack(side='left', padx=5)

    def delete_target_character(self, index):
        # Eliminar el área de la lista
        del self.target_characters[index]
        
        # Actualizar la vista
        self.show_target_characters()

    def monitoring_loop(self):
        status_detector_utilities = StatusDetectorUtilities()
        phone_alert = AlertManager()
        detector = StatusDetectorConfig(self.sound_path, self.pattern_path)

        while self.is_monitoring:
            try:
                screenshots = []
                alive_statuses = []

                for area in self.target_characters:
                    start_x, start_y, end_x, end_y = area
                    screenshot_array = status_detector_utilities.get_screenshot_array(start_x, start_y, end_x, end_y)
                    is_alive_pattern = status_detector_utilities.find_partial_pattern(screenshot_array, detector.pattern)
                    
                    screenshots.append(screenshot_array)
                    alive_statuses.append(is_alive_pattern)

                self.refresh_targets_view_fn()

                now = datetime.now()
                now_format = now.strftime("%Y-%m-%d %I:%M %p")

                if all(alive_statuses):
                    GlobalConsole.log(f"{now_format} ¡Personaje vivo! ✓")
                    detector.stop_alarm()
                else:
                    phone_alert.send_phone_alert("METIN2", "Personaje muerto!!!")
                    GlobalConsole.log(f"{now_format} ¡PERSONAJE MUERTO! ⚠")
                    detector.play_alarm()

                debounce_time = 30 if all(alive_statuses) else 5   
                time.sleep(debounce_time)
                    
            except Exception as e:
                print(f"Error en el monitoreo: {e}")
                time.sleep(5)  # Esperar antes de reintentar en caso de error

        detector.stop_alarm()  # Asegurarse de que la alarma se detenga al finalizar

    def toggle_monitoring(self):
        if not self.target_characters:
            GlobalConsole.log("Selecciona el área a monitorear")
            return

        if not self.is_monitoring:
            # Iniciar monitoreo
            self.is_monitoring = True
            self.set_monitor_button_text("Detener monitoreo")
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
            self.monitoring_thread.daemon = True  # El hilo se detendrá cuando se cierre la aplicación
            self.monitoring_thread.start()
        else:
            # Detener monitoreo
            self.is_monitoring = False
            self.set_monitor_button_text("Iniciar monitoreo")

    def set_monitor_button_text(self, text):
        if hasattr(self, 'monitor_button') and self.monitor_button is not None:
            self.monitor_button.config(text=text)

    def setup_scrollable_frame(self):
        # Frame contenedor principal
        container = tk.Frame(self.root, pady=10, padx=10)
        container.pack(pady=5, fill='x')

        # Canvas con scrollbar
        self.canvas = tk.Canvas(container, height=150, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(container, orient='vertical', command=self.canvas.yview)

        # Configuración del scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Posicionamiento de elementos
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        # Frame interno
        self.target_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.target_frame, anchor='nw')

        # Actualizar scrollregion cuando cambie el contenido
        def _configure_frame(event):
            size = (self.target_frame.winfo_reqwidth(), self.target_frame.winfo_reqheight())
            self.canvas.configure(scrollregion="0 0 %s %s" % size)
            if self.target_frame.winfo_reqwidth() != self.canvas.winfo_width():
                self.canvas.configure(width=self.target_frame.winfo_reqwidth())

        self.target_frame.bind("<Configure>", _configure_frame)