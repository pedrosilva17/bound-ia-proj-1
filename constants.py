from enum import Enum

class Piece(Enum):
    Empty = 0
    Red = 1
    Black = 2
    
    
COLOR_DICT = {"Black": (0,0,0), "Empty": (255, 255, 255), "Red": (184,0,0)}

BOT_DIFFICULTY = {1: "random_move", 2: "execute_mcts", 3: "execute_minimax", 4: "execute_minimax"}

BOT_NAME = {1: "The Squirrel", 2: "The Raccoon", 3: "The Deer", 4: "The Fox"}