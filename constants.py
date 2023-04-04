from enum import Enum


class Piece(Enum):
    """Enum class to represent the possible pieces in a game.

    Args:
        Enum (Enum): The Enum class being extended.
    """
    Empty = 0
    Red = 1
    Black = 2


# Dictionary of color names pointing to the RGB codes
COLOR_DICT = {"Black": (0, 0, 0), "Empty": (255, 255, 255), "Red": (184, 0, 0)}

# Dictionary of bot difficulty values pointing to their respective names
BOT_NAME = {1: "The Squirrel", 2: "The Raccoon", 3: "The Deer", 4: "The Fox"}
