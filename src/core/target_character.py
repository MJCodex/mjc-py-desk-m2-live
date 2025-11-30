from typing import List

class TargetCharacter:
    """
    Representa un personaje objetivo con su área de captura y patrones a monitorear.
    Ahora soporta múltiples patrones por personaje.
    """
    
    def __init__(
        self,
        start_x: int | float,
        start_y: int | float,
        end_x: int | float,
        end_y: int | float,
        pattern_types: List[str] | str,  # Ahora puede ser lista o string único
        name: str = ""
    ):
        """
        Args:
            start_x, start_y: Coordenadas superiores izquierdas del área
            end_x, end_y: Coordenadas inferiores derechas del área
            pattern_types: Lista de tipos de patrones a monitorear (ej: ['is_alive', 'is_online'])
                          o un string único para retrocompatibilidad (ej: 'is_alive')
            name: Nombre identificador del personaje
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
        
        # Validar que el área sea válida
        self._validate_area()
    
    def _validate_area(self):
        """Valida que las coordenadas del área sean correctas"""
        if self.end_x <= self.start_x or self.end_y <= self.start_y:
            raise ValueError(
                f"Área inválida para {self.name}: "
                f"({self.start_x}, {self.start_y}) -> ({self.end_x}, {self.end_y})"
            )
    
    def add_pattern(self, pattern_type: str):
        """Agrega un nuevo patrón al personaje si no existe"""
        if pattern_type not in self.pattern_types:
            self.pattern_types.append(pattern_type)
    
    def remove_pattern(self, pattern_type: str):
        """Elimina un patrón del personaje"""
        if pattern_type in self.pattern_types:
            self.pattern_types.remove(pattern_type)
    
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
            f"patterns={self.pattern_types})"
        )
    
    def to_dict(self) -> dict:
        """Convierte el personaje a diccionario (útil para serialización)"""
        return {
            'name': self.name,
            'start_x': self.start_x,
            'start_y': self.start_y,
            'end_x': self.end_x,
            'end_y': self.end_y,
            'pattern_types': self.pattern_types
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
            name=data.get('name', '')
        )