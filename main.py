#
# regex p filtrar inputs
#

import Game
import pygame
from utils import parse_int_input

if __name__ == "__main__":
    while True:
        opt = parse_int_input("BOUND\n"
                              "1 - One game\n"
                              "2 - Run 10000 games\n",
                              1, 2)
        match opt:
            case 1:
                Game.one_game()
            case 2:
                Game.run_games(10000)
            
    