from enum import Enum

class Piece(Enum):
    Empty = 0
    Red = 1
    Black = 2
    
COLOR_DICT = {"Black": (0,0,0), "Empty": (250, 197, 52), "Red": (255,0,0)}
    