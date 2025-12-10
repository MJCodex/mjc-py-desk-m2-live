from typing import List, Dict, Any, Optional

class TargetCharacter:
    """
    Representa un personaje objetivo con su área de captura y patrones a monitorear.
    Soporta múltiples patrones por personaje con configuración personalizada (ej: expected_count).
    """
    
    def __init__(
        self,
        start_x: int | float,
        start_y: int | float,
        end_x: int | float,
        end_y: int | float,
        pattern_types: List[str] | str = 'is_alive',  # Default: 'is_alive'
        name: str = "",
        patterns_config: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        """
        Args:
            start_x, start_y: Coordenadas superiores izquierdas del área
            end_x, end_y: Coordenadas inferiores derechas del área
            pattern_types: Lista de tipos de patrones o string único (retrocompatibilidad)
            name: Nombre identificador del personaje
            patterns_config: Dict con configuración personalizada por patrón
                            Ej: {'is_online_in_group': {'expected_count': 5}}
        """
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.name = name or "Sin nombre"
        
        # Normalizar pattern_types a lista
        if isinstance(pattern_types, str):
            self.pattern_types = [pattern_types]
        else:
            self.pattern_types = list(pattern_types)
        
        # Inicializar configuración de patrones
        self.patterns_config: Dict[str, Dict[str, Any]] = patterns_config or {}
        
        # Asegurar que todos los patrones tengan entrada en patterns_config
        for pattern_type in self.pattern_types:
            if pattern_type not in self.patterns_config:
                self.patterns_config[pattern_type] = {}
        
        # Validar que el área sea válida
        self._validate_area()
    
    def _validate_area(self):
        """Valida que las coordenadas del área sean correctas"""
        if self.end_x <= self.start_x or self.end_y <= self.start_y:
            raise ValueError(
                f"Área inválida para {self.name}: "
                f"({self.start_x}, {self.start_y}) -> ({self.end_x}, {self.end_y})"
            )
    
    def add_pattern(self, pattern_type: str, config: Optional[Dict[str, Any]] = None):
        """Agrega un nuevo patrón al personaje si no existe"""
        if pattern_type not in self.pattern_types:
            self.pattern_types.append(pattern_type)
        # Inicializar configuración si no existe
        if pattern_type not in self.patterns_config:
            self.patterns_config[pattern_type] = config or {}
    
    def remove_pattern(self, pattern_type: str):
        """Elimina un patrón del personaje"""
        if pattern_type in self.pattern_types:
            self.pattern_types.remove(pattern_type)
        if pattern_type in self.patterns_config:
            del self.patterns_config[pattern_type]
    
    def set_pattern_config(self, pattern_type: str, config: Dict[str, Any]):
        """Actualiza la configuración de un patrón específico"""
        if pattern_type not in self.pattern_types:
            raise ValueError(f"Patrón '{pattern_type}' no existe en este character")
        self.patterns_config[pattern_type] = config
    
    def get_pattern_config(self, pattern_type: str) -> Dict[str, Any]:
        """Obtiene la configuración de un patrón específico"""
        return self.patterns_config.get(pattern_type, {})
    
    def update_pattern_config_value(self, pattern_type: str, key: str, value: Any):
        """Actualiza un valor específico en la configuración de un patrón"""
        if pattern_type not in self.pattern_types:
            raise ValueError(f"Patrón '{pattern_type}' no existe en este character")
        if pattern_type not in self.patterns_config:
            self.patterns_config[pattern_type] = {}
        self.patterns_config[pattern_type][key] = value
    
    def has_pattern(self, pattern_type: str) -> bool:
        """Verifica si el personaje tiene un patrón específico"""
        return pattern_type in self.pattern_types
    
    def get_area_coords(self) -> tuple:
        """Retorna las coordenadas del área como tupla"""
        return (self.start_x, self.start_y, self.end_x, self.end_y)
    
    def get_area_size(self) -> tuple:
        """Retorna el tamaño del área (ancho, alto)"""
        width = self.end_x - self.start_x
        height = self.end_y - self.start_y
        return (width, height)
    
    def __repr__(self):
        """Representación string del personaje"""
        return (
            f"TargetCharacter(name='{self.name}', "
            f"area=({self.start_x},{self.start_y})-({self.end_x},{self.end_y}), "
            f"patterns={self.pattern_types}, config={self.patterns_config})"
        )
    
    def to_dict(self) -> dict:
        """Convierte el personaje a diccionario (útil para serialización)"""
        return {
            'name': self.name,
            'start_x': self.start_x,
            'start_y': self.start_y,
            'end_x': self.end_x,
            'end_y': self.end_y,
            'pattern_types': self.pattern_types,
            'patterns_config': self.patterns_config
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un TargetCharacter desde un diccionario"""
        return cls(
            start_x=data['start_x'],
            start_y=data['start_y'],
            end_x=data['end_x'],
            end_y=data['end_y'],
            pattern_types=data['pattern_types'],
            name=data.get('name', ''),
            patterns_config=data.get('patterns_config', {})
        )