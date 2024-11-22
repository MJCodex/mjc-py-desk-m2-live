import tkinter as tk
from src.screen_capture import ScreenCapture
import sys
import os
from src.status_detector_config import StatusDetectorConfig
from src.status_detector_utilities import StatusDetectorUtilities
from src.alert_manager import AlertManager
import cv2
import time
from datetime import datetime
import threading
from PIL import Image, ImageTk
from tkinter import scrolledtext
from src.global_console import GlobalConsole

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("M2 Monitor")
        self.root.geometry("400x450")
        self.root.resizable(False, False)
        self.root.attributes("-toolwindow", True)

        # Variable para controlar el monitoreo
        self.is_monitoring = False
        self.monitoring_thread = None
        self.selected_area = None

        # Widgets
        self.label = tk.Label(self.root, text="Selecciona el área donde se encuentra la barra de vida")
        self.label.pack(pady=10)

        self.select_button  = tk.Button(self.root, text="Seleccionar", command=self.capture_coordinates)
        self.select_button .pack(pady=10)

        # Frame donde se mostrará la imagen
        self.target_area = tk.Label(self.root, text="Área monitoreada")
        self.target_area.pack(pady=10)

        self.monitor_button = tk.Button(self.root, text="Iniciar monitoreo", command=self.toggle_monitoring)
        self.monitor_button.pack(pady=10)

        self.console = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=30, width=60, state="disabled", bg="gray20", fg="white")
        self.console.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)
        GlobalConsole.set_console(self.console)

        # Cargar recursos
        self.load_stored_recources()

    def capture_coordinates(self):
        # Instancia de la clase
        capture_tool = ScreenCapture(self.root)

        # Capturar coordenadas
        self.selected_area = capture_tool.run()

        # Resaltar área seleccionada
        if self.selected_area:
            # capture_tool.highlight_selection(self.selected_area)

            # Mostrar área monitoreada
            start_x, start_y, end_x, end_y = self.selected_area
            status_detector_utilities = StatusDetectorUtilities()
            screenshot_array = status_detector_utilities.get_screenshot_array(start_x, start_y, end_x, end_y)
            self.show_image(screenshot_array)
    
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

    def show_image(self, screenshot_array):
        image = Image.fromarray(screenshot_array)

        # Convertir a un objeto compatible con Tkinter
        tk_image = ImageTk.PhotoImage(image)

        # Mostrar la imagen en el Label
        self.target_area.configure(image=tk_image, text="")  # Limpia el texto
        self.target_area.image = tk_image  # Almacena una referencia para evitar que se borre
       
    def monitoring_loop(self):
        status_detector_utilities = StatusDetectorUtilities()
        phone_alert = AlertManager()
        detector = StatusDetectorConfig(self.sound_path, self.pattern_path)

        while self.is_monitoring:
            try:
                start_x, start_y, end_x, end_y = self.selected_area
                screenshot_array = status_detector_utilities.get_screenshot_array(start_x, start_y, end_x, end_y)
                is_alive_pattern = status_detector_utilities.find_partial_pattern(screenshot_array, detector.pattern)
                self.show_image(screenshot_array)

                # Guardar imágenes para depuración
                cv2.imwrite("last_screenshot.png", screenshot_array)
                cv2.imwrite("pattern.png", detector.pattern_original)

                now = datetime.now()
                now_format = now.strftime("%Y-%m-%d %I:%M %p")

                if is_alive_pattern:
                    GlobalConsole.log(f"{now_format} ¡Personaje vivo! ✓")
                    detector.stop_alarm()
                else:
                    phone_alert.send_phone_alert("METIN2", "Personaje muerto!!!")
                    GlobalConsole.log(f"{now_format} ¡PERSONAJE MUERTO! ⚠")
                    detector.play_alarm()

                debounce_time = 30 if is_alive_pattern else 5   
                time.sleep(debounce_time)
                
            except Exception as e:
                print(f"Error en el monitoreo: {e}")
                time.sleep(5)  # Esperar antes de reintentar en caso de error

        detector.stop_alarm()  # Asegurarse de que la alarma se detenga al finalizar

    def toggle_monitoring(self):
        if not self.selected_area:
            GlobalConsole.log("Selecciona el área a monitorear")
            return

        if not self.is_monitoring:
            # Iniciar monitoreo
            self.is_monitoring = True
            self.monitor_button.config(text="Detener monitoreo")
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
            self.monitoring_thread.daemon = True  # El hilo se detendrá cuando se cierre la aplicación
            self.monitoring_thread.start()
        else:
            # Detener monitoreo
            self.is_monitoring = False
            self.monitor_button.config(text="Iniciar monitoreo")