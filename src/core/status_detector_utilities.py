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
    
    def find_partial_pattern(self, image, pattern, threshold=0.7, use_color=False, count_matches=False):
        """
        Busca una coincidencia parcial del patrón en la imagen.
        
        Args:
            image: Imagen donde buscar
            pattern: Patrón a buscar
            threshold: Umbral de similitud (0.0 a 1.0)
            use_color: Si True, usa información de color en lugar de escala de grises
            count_matches: Si True, retorna cantidad de coincidencias. Si False, retorna bool
        
        Returns:
            - Si count_matches=False: bool (True si encuentra al menos una coincidencia)
            - Si count_matches=True: int (cantidad de coincidencias encontradas)
        """
        try:
            if use_color:
                return self._find_pattern_with_color(image, pattern, threshold, count_matches)
            else:
                return self._find_pattern_grayscale(image, pattern, threshold, count_matches)
                
        except Exception as e:
            logging.error(f"Error en find_partial_pattern: {str(e)}")
            logging.error(traceback.format_exc())
            return 0 if count_matches else False
    
    def _find_pattern_grayscale(self, image, pattern, threshold, count_matches=False):
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
        
        if count_matches:
            # Contar TODAS las coincidencias que superen el umbral
            locations = np.nonzero(result >= threshold)
            matches = list(zip(*locations[::-1]))  # (x, y) de cada coincidencia
            
            # Eliminar coincidencias superpuestas (Non-Maximum Suppression simple)
            filtered_matches = self._filter_overlapping_matches(
                matches, 
                pattern_gray.shape[1],  # ancho del patrón
                pattern_gray.shape[0]   # alto del patrón
            )
            
            count = len(filtered_matches)
            return count
        else:
            # Modo original: solo verificar si existe al menos una
            _, max_val, _, _ = cv2.minMaxLoc(result)
            return max_val >= threshold
    
    def _find_pattern_with_color(self, image, pattern, threshold, count_matches=False):
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
        channels_results = []
        
        for i in range(3):  # B, G, R
            result = cv2.matchTemplate(
                image_bgr[:, :, i], 
                pattern_bgr[:, :, i], 
                cv2.TM_CCOEFF_NORMED
            )
            channels_results.append(result)
        
        # Promedio de las coincidencias en los 3 canales
        avg_result = np.mean(channels_results, axis=0)
        
        if count_matches:
            # Contar TODAS las coincidencias que superen el umbral
            locations = np.nonzero(avg_result >= threshold)
            matches = list(zip(*locations[::-1]))  # (x, y) de cada coincidencia
            
            # Eliminar coincidencias superpuestas
            filtered_matches = self._filter_overlapping_matches(
                matches, 
                pattern_bgr.shape[1],  # ancho del patrón
                pattern_bgr.shape[0]   # alto del patrón
            )
            
            count = len(filtered_matches)
            return count
        else:
            # Modo original: solo verificar si existe al menos una
            _, max_val, _, _ = cv2.minMaxLoc(avg_result)
            return max_val >= threshold
    
    def _filter_overlapping_matches(self, matches, pattern_width, pattern_height, overlap_threshold=0.5):
        """
        Filtra coincidencias superpuestas usando Non-Maximum Suppression.
        
        Args:
            matches: Lista de (x, y) coordenadas de coincidencias
            pattern_width: Ancho del patrón
            pattern_height: Alto del patrón
            overlap_threshold: Umbral de superposición (0.5 = 50% de superposición permitida)
        
        Returns:
            Lista filtrada de coincidencias sin superposiciones significativas
        """
        if not matches:
            return []
        
        # Si solo hay una coincidencia, retornarla directamente
        if len(matches) == 1:
            return matches
        
        filtered = []
        matches_sorted = sorted(matches, key=lambda m: (m[1], m[0]))  # Ordenar por Y, luego X
        
        for match in matches_sorted:
            x, y = match
            
            # Verificar si esta coincidencia se superpone significativamente con alguna ya aceptada
            is_overlapping = False
            for accepted_x, accepted_y in filtered:
                # Calcular superposición
                x_overlap = max(0, min(x + pattern_width, accepted_x + pattern_width) - max(x, accepted_x))
                y_overlap = max(0, min(y + pattern_height, accepted_y + pattern_height) - max(y, accepted_y))
                
                overlap_area = x_overlap * y_overlap
                pattern_area = pattern_width * pattern_height
                
                if overlap_area / pattern_area > overlap_threshold:
                    is_overlapping = True
                    break
            
            if not is_overlapping:
                filtered.append(match)
        
        return filtered