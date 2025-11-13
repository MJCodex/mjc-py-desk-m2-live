import tkinter as tk
from PIL import ImageGrab
import cv2
import numpy as np


class ScreenCapture:
    def __init__(self, master=None):
        """Inicializa la ventana secundaria."""
        if master is None:
            self.master = tk.Tk()
            self.master.withdraw()  # Ocultar ventana raíz
            self.owns_master = True
        else:
            self.master = master
            self.owns_master = False
        self.top = tk.Toplevel(self.master)
        self.top.attributes("-fullscreen", True)  # Pantalla completa
        self.top.attributes("-topmost", True)  # Siempre visible
        self.top.attributes("-alpha", 0.3)  # Ajustar transparencia (30%)
        self.top.configure(cursor="cross", bg="black")  # Cambiar cursor a cruz
        self.canvas = tk.Canvas(self.top, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Variables para la selección
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.selection_coordinates = None

        # Eventos del ratón
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def on_mouse_press(self, event):
        """Inicia la selección del área."""
        self.start_x, self.start_y = event.x, event.y
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", width=2)

    def on_mouse_drag(self, event):
        """Dibuja el rectángulo dinámicamente mientras se arrastra el ratón."""
        if self.rect_id:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_release(self, event):
        """Guarda las coordenadas finales y cierra la ventana secundaria."""
        end_x, end_y = event.x, event.y
        self.selection_coordinates = (self.start_x, self.start_y, end_x, end_y)
        print(f"Área seleccionada: {self.selection_coordinates}")
        self.top.destroy()  # Cierra la ventana secundaria después de la selección

    def highlight_selection(self, coordinates):
        """Resalta el área seleccionada mostrando únicamente el fragmento capturado."""
        x1, y1, x2, y2 = coordinates

        # Asegurar que las coordenadas sean válidas (x1 < x2, y1 < y2)
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        # Captura la pantalla completa
        screen = ImageGrab.grab()

        # Recortar la selección
        cropped = screen.crop((x1, y1, x2, y2))

        # Convertir a formato OpenCV para mostrarlo
        cropped_np = np.array(cropped)
        cropped_bgr = cv2.cvtColor(cropped_np, cv2.COLOR_RGB2BGR)

        # Mostrar el área recortada
        cv2.imshow("Área Seleccionada", cropped_bgr)
        cv2.waitKey(2000)  # Mostrar por 2 segundos
        cv2.destroyAllWindows()


    def run(self):
        """Ejecuta la ventana secundaria para capturar la selección."""
        self.master.wait_window(self.top)  # Espera hasta que se cierre la ventana
        if self.owns_master:
            self.master.destroy()
        return self.selection_coordinates
