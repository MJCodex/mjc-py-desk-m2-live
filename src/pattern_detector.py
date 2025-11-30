from datetime import datetime
from typing import Dict, Any, List
from src.pattern_registry import PatternRegistry
from src.status_detector_utilities import StatusDetectorUtilities
from src.target_character import TargetCharacter

class PatternDetector:
    """
    Detector unificado que maneja la lógica de detección para TODOS los patrones.
    No necesita ser modificado al agregar nuevos patrones.
    """
    
    def __init__(self):
        self.pattern_registry = PatternRegistry.get_instance()
        self.utilities = StatusDetectorUtilities()
    
    def detect_character_patterns(self, character: TargetCharacter) -> List[Dict[str, Any]]:
        """
        Detecta todos los patrones configurados para un personaje.
        
        Args:
            character: El personaje objetivo a evaluar
            
        Returns:
            Lista de resultados de detección, uno por cada patrón del personaje
        """
        results = []
        
        # Capturar screenshot una sola vez para todos los patrones
        screenshot = self._capture_character_area(character)
        if screenshot is None:
            return results
        
        # Evaluar cada patrón del personaje
        for pattern_type in character.pattern_types:
            try:
                result = self._detect_single_pattern(
                    character=character,
                    pattern_type=pattern_type,
                    screenshot=screenshot
                )
                results.append(result)
                
            except Exception as e:
                # Agregar resultado de error
                results.append(self._create_error_result(character, pattern_type, str(e)))
        
        return results
    
    def _capture_character_area(self, character: TargetCharacter):
        """Captura el área de pantalla del personaje"""
        try:
            screenshot_array = self.utilities.get_screenshot_array(
                character.start_x,
                character.start_y,
                character.end_x,
                character.end_y
            )
            return screenshot_array
        except Exception as e:
            return None
    
    def _detect_single_pattern(
        self,
        character: TargetCharacter,
        pattern_type: str,
        screenshot
    ) -> Dict[str, Any]:

        pattern_config = self.pattern_registry.get_pattern(pattern_type)

        # Elegir si contamos coincidencias
        count_matches = pattern_config.get("count_matches", False)
        expected_count = pattern_config.get("expected_count", None)

        # Ejecutar detección usando la nueva API
        detection_result = self.utilities.find_partial_pattern(
            image=screenshot,
            pattern=pattern_config["pattern"],
            threshold=pattern_config["threshold"],
            use_color=pattern_config.get("use_color", False),
            count_matches=count_matches
        )

        # -------------------------------------------------------------
        # 1. Interpretar resultado según si es booleano o entero
        # -------------------------------------------------------------
        if count_matches:
            detected_count = detection_result

            # Si se espera N elementos y hay menos → estado incorrecto
            status_ok = True
            if expected_count is not None:
                status_ok = detected_count >= expected_count

        else:
            is_detected = bool(detection_result)

            # alert_on_match invierte la lógica
            alert_on_match = pattern_config.get("alert_on_match", False)

            status_ok = not is_detected if alert_on_match else is_detected

        # -------------------------------------------------------------
        # 2. Preparar mensajes dinámicos
        # -------------------------------------------------------------
        if count_matches:
            # Para patrones como is_online_in_group
            count_matches = 0
            if expected_count is not None:
                count_matches = max(0, expected_count - detected_count)

            if status_ok:
                message = pattern_config["message_ok"]
            else:
                message = pattern_config["message_fail"].format(
                    name=character.name,
                    count_matches=count_matches
                )
        else:
            # Patrones simples (is_alive, is_online)
            if status_ok:
                message = pattern_config["message_ok"]
            else:
                message = pattern_config["message_fail"].format(
                    name=character.name
                )

        # -------------------------------------------------------------
        # 3. Construir retorno
        # -------------------------------------------------------------
        now = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        return {
            "alarmed": not status_ok,
            "message": message,
            "name": character.name,
            "date": now,
            "pattern_type": pattern_type,
            "detected": detection_result
        }

    def _create_error_result(
        self,
        character: TargetCharacter,
        pattern_type: str,
        error_msg: str
    ) -> Dict[str, Any]:
        """Crea un resultado de error cuando falla la detección"""
        now = datetime.now()
        now_format = now.strftime("%Y-%m-%d %I:%M %p")
        
        return {
            'alarmed': True,
            'message': f'ERROR detectando {pattern_type} en {character.name}: {error_msg}',
            'name': character.name,
            'date': now_format,
            'pattern_type': pattern_type,
            'detected': False,
            'error': True
        }
    
    def detect_multiple_characters(
        self,
        characters: List[TargetCharacter]
    ) -> List[Dict[str, Any]]:
        """
        Detecta patrones para múltiples personajes.
        
        Returns:
            Lista plana de todos los resultados de detección
        """
        all_results = []
        
        for character in characters:
            character_results = self.detect_character_patterns(character)
            all_results.extend(character_results)
        
        return all_results