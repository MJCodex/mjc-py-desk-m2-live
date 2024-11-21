import logging
from PIL import ImageGrab
import numpy as np
import traceback
import cv2
import pyautogui

class StatusDetectorUtilities:

    def get_screenshot_array(self, x1, y1, x2, y2):
        # Retorna un screenshot array del area
        try:
            # Asegurar que las coordenadas estén en el orden correcto
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # Verificar que el área es válida
            if x2 <= x1 or y2 <= y1:
                logging.error("Área inválida seleccionada")
                return False
                
            # Captura la región especificada
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            screenshot_array = np.array(screenshot)
            
            return screenshot_array

        except Exception as e:
            logging.error(f"Error en check_red_in_area: {str(e)}")
            logging.error(traceback.format_exc())
            return False

    def find_partial_pattern(self, image, pattern, threshold=0.7):
        # Busca una coincidencia parcial del patrón en la imagen.
        # Retorna True si encuentra el patrón con suficiente similitud.
        # Asegurarse de que la imagen esté en escala de grises
        if len(image.shape) == 3:
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            image_gray = image

        # Realizar template matching
        result = cv2.matchTemplate(image_gray, pattern, cv2.TM_CCOEFF_NORMED)
        
        # Encontrar el valor máximo de coincidencia
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        return max_val >= threshold

    def get_screen_position(self):
        # Obtiene la posición del cursor con mejor manejo de errores

        try:
            x, y = pyautogui.position()
            logging.debug(f"Posición capturada: ({x}, {y})")
            return x, y
        except Exception as e:
            logging.error(f"Error al obtener posición: {str(e)}")
            return None, None
