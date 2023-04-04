import sys
import Game
from utils import parse_int_input

if __name__ == "__main__":
    while True:
        opt = parse_int_input("BOUND\n"
                              "1 - One game\n"
                              "2 - Run n games\n"
                              "3 - Example Game\n"
                              "0 - Exit\n",
                              0, 3)
        match opt:
            case 1:
                Game.one_game()
            case 2:
                n_games = parse_int_input(
                    "How many games do you want to run?\n")
                Game.run_games(n_games)
            case 3:
                Game.example()
            case 0:
                sys.exit(0)
