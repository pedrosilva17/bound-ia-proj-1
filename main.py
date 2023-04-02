#
# regex p filtrar inputs
#

import Game
from utils import parse_int_input

if __name__ == "__main__":
    while True:
        opt = parse_int_input("BOUND\n"
                              "1 - One game\n"
                              "2 - Run n games\n"
                              "3 - Example Game\n",
                              1, 3)
        match opt:
            case 1:
                Game.one_game()
            case 2:
                n_games = parse_int_input("How many games do you want to run?")
                Game.run_games(n_games)
            case 3:
                Game.example()

            
    