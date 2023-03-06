from enum import Enum

class Piece(Enum):
    Empty = 0
    Red = 1
    Black = 2
    
COLOR_DICT = {"Black": (11,114,16), "Empty": (228, 185, 88), "Red": (184,0,0)}
    