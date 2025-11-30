import os
import sys
import cv2
import logging
from typing import Dict, Any
from pygame import mixer

class PatternRegistry:
    """
    Registro centralizado de todos los patrones de detección.
    Permite agregar nuevos patrones sin modificar el código principal.
    """
    
    _instance = None
    _patterns: Dict[str, Dict[str, Any]] = {}
    _initialized = False
    
    # Configuración de patrones: agregar nuevos aquí
    PATTERN_DEFINITIONS = {
        'is_alive': {
            'file': 'pattern.png',
            'sound': 'alarm.mp3',
            'message_ok': '¡Personaje vivo! ✓',
            'message_fail': '¡PERSONAJE {name} MUERTO! ⚠',
            'threshold': 0.7,
            'priority': 1  # Mayor prioridad = se evalúa primero
        },
        'is_online': {
            'file': 'online_pattern.png',
            'sound': 'alarm.mp3',
            'message_ok': '¡Personaje conectado! ✓',
            'message_fail': '¡PERSONAJE {name} DESCONECTADO! ⚠',
            'threshold': 0.7,
            'priority': 2
        },
        'is_alive_in_group': {
            'file': 'death_group_pattern.png',
            'sound': 'alarm.mp3',
            'message_ok': '¡Personaje ok! ✓',
            'message_fail': '¡PERSONAJE {name} MUERTO! ⚠',
            'threshold': 0.99,
            'priority': 2,
            'alert_on_match': True,
            'use_color': True
        },
        'is_online_in_group': {
            'file': 'alive_group_pattern.png',
            'sound': 'alarm.mp3',
            'message_ok': '¡Todos conectados! ✓',
            'message_fail': '¡{count_matches} DESCONECTADO(S) EN GRUPO {name}! ⚠',
            'threshold': 0.8,
            'priority': 2,
            'use_color': False,
            'count_matches': True,      # ← NUEVO: activar conteo múltiple
            'expected_count': 3         # ← NUEVO: esperamos N conectados
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el registro de patrones (solo una vez)"""
        if not PatternRegistry._initialized:
            self._load_patterns()
            PatternRegistry._initialized = True
    
    def _get_base_path(self):
        """Obtiene la ruta base de recursos según el entorno"""
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, 'store')
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            return os.path.join(parent_dir, 'store')
    
    def _load_patterns(self):
        """Carga todos los patrones definidos en PATTERN_DEFINITIONS"""
        base_path = self._get_base_path()
        
        for pattern_type, config in self.PATTERN_DEFINITIONS.items():
            try:
                # Rutas completas
                pattern_path = os.path.join(base_path, config['file'])
                sound_path = os.path.join(base_path, config['sound'])
                
                # Validar existencia de archivos
                if not os.path.exists(pattern_path):
                    raise FileNotFoundError(f"Patrón no encontrado: {pattern_path}")
                if not os.path.exists(sound_path):
                    raise FileNotFoundError(f"Sonido no encontrado: {sound_path}")
                
                # Cargar imagen del patrón
                pattern_img = cv2.imread(pattern_path)
                if pattern_img is None:
                    raise ValueError(f"No se pudo cargar el patrón: {pattern_path}")
                
                # Cargar sonido
                alarm_sound = mixer.Sound(sound_path)
                
                # Guardar en registro
                self._patterns[pattern_type] = {
                    'pattern': pattern_img,
                    'sound': alarm_sound,
                    'message_ok': config['message_ok'],
                    'message_fail': config['message_fail'],
                    'threshold': config.get('threshold', 0.7),
                    'priority': config.get('priority', 999),
                    'alert_on_match': config.get('alert_on_match', False),
                    'use_color': config.get('use_color', False),
                    'count_matches': config.get('count_matches', False),
                    'expected_count': config.get('expected_count', None)
                }
                
            except Exception as e:
                logging.error(f"✗ Error cargando patrón '{pattern_type}': {str(e)}")
                raise
    
    def get_pattern(self, pattern_type: str) -> Dict[str, Any]:
        """Obtiene la configuración de un patrón específico"""
        if pattern_type not in self._patterns:
            raise ValueError(f"Patrón desconocido: '{pattern_type}'. Patrones disponibles: {list(self._patterns.keys())}")
        return self._patterns[pattern_type]
    
    def get_all_pattern_types(self):
        """Retorna lista de todos los tipos de patrones disponibles"""
        return sorted(self._patterns.keys(), key=lambda x: self._patterns[x]['priority'])
    
    def pattern_exists(self, pattern_type: str) -> bool:
        """Verifica si un patrón existe en el registro"""
        return pattern_type in self._patterns
    
    @classmethod
    def get_instance(cls):
        """Obtiene la instancia singleton del registro"""
        return cls()