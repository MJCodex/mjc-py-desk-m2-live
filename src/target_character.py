class TargetCharacter:
    def __init__(self, start_x: int | float, start_y: int | float, end_x: int | float, end_y: int | float, pattern_type: str, name: str = ""):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.pattern_type = pattern_type
        self.name = name