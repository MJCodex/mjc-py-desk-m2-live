import logging
from PIL import ImageGrab
import numpy as np
import traceback
import cv2

class StatusDetectorUtilities:
    def get_screenshot_array(self, x1, y1, x2, y2):
        """Retorna un screenshot array del área"""
        try:
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            if x2 <= x1 or y2 <= y1:
                logging.error("Área inválida seleccionada")
                return False
                
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            screenshot_array = np.array(screenshot)
            
            return screenshot_array
        except Exception as e:
            logging.error(f"Error en get_screenshot_array: {str(e)}")
            logging.error(traceback.format_exc())
            return False
    
    def find_partial_pattern(self, image, pattern, threshold=0.7, use_color=False):
        """
        Busca una coincidencia parcial del patrón en la imagen.
        
        Args:
            image: Imagen donde buscar
            pattern: Patrón a buscar
            threshold: Umbral de similitud (0.0 a 1.0)
            use_color: Si True, usa información de color en lugar de escala de grises
        
        Returns:
            True si encuentra el patrón con suficiente similitud
        """
        try:
            if use_color:
                # Modo COLOR: detecta diferencias de color (mejor para vida vs muerte)
                return self._find_pattern_with_color(image, pattern, threshold)
            else:
                # Modo ORIGINAL: escala de grises (para otros patrones)
                return self._find_pattern_grayscale(image, pattern, threshold)
                
        except Exception as e:
            logging.error(f"Error en find_partial_pattern: {str(e)}")
            logging.error(traceback.format_exc())
            return False
    
    def _find_pattern_grayscale(self, image, pattern, threshold):
        """Método original en escala de grises"""
        # Asegurarse de que la imagen esté en escala de grises
        if len(image.shape) == 3:
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            image_gray = image
        
        if len(pattern.shape) == 3:
            pattern_gray = cv2.cvtColor(pattern, cv2.COLOR_BGR2GRAY)
        else:
            pattern_gray = pattern
            
        # Realizar template matching
        result = cv2.matchTemplate(image_gray, pattern_gray, cv2.TM_CCOEFF_NORMED)
        
        # Encontrar el valor máximo de coincidencia
        _, max_val, _, _ = cv2.minMaxLoc(result)
        
        logging.debug(f"Similitud (escala de grises): {max_val:.3f}")
        
        return max_val >= threshold
    
    def _find_pattern_with_color(self, image, pattern, threshold):
        """Método alternativo que usa información de COLOR"""
        # Asegurar que ambas imágenes estén en BGR (formato OpenCV)
        if len(image.shape) == 2:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) if image.shape[2] == 3 else image
        
        if len(pattern.shape) == 2:
            pattern_bgr = cv2.cvtColor(pattern, cv2.COLOR_GRAY2BGR)
        else:
            pattern_bgr = cv2.cvtColor(pattern, cv2.COLOR_RGB2BGR) if pattern.shape[2] == 3 else pattern
        
        # Template matching en cada canal de color por separado
        channels_match = []
        
        for i in range(3):  # B, G, R
            result = cv2.matchTemplate(
                image_bgr[:, :, i], 
                pattern_bgr[:, :, i], 
                cv2.TM_CCOEFF_NORMED
            )
            _, max_val, _, _ = cv2.minMaxLoc(result)
            channels_match.append(max_val)
        
        # Promedio de las coincidencias en los 3 canales
        avg_match = np.mean(channels_match)
        
        logging.debug(f"Similitud por canal - B:{channels_match[0]:.3f}, "
                     f"G:{channels_match[1]:.3f}, R:{channels_match[2]:.3f}, "
                     f"Promedio:{avg_match:.3f}")
        
        return avg_match >= threshold