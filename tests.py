import csv
from Game import run_games

start_piece = {False: "Red", True: "Black"}
bot_depth = {3: "1", 4: "3"}


def save_results(n_games: int, rev_start_order: bool, bot_1: int, bot_2: int):
    """Run a certain amount of games, given the starting order and the two bot 
    difficulty values, and store the results in a CSV file.

    Args:
        n_games (int): The number of games to be played.
        rev_start_order (bool): True if the Black pieces start, False otherwise.
        bot_1 (int): The first bot's difficulty.
        bot_2 (int): The second bot's difficulty.
    """
    results = run_games(n_games, rev_start_order, bot_1, bot_2)
    filename = "black" if rev_start_order else "red"
    with open(f'results_{filename}.csv', mode='r') as file:
        reader = csv.reader(file)
        data = list(reader)
        if rev_start_order:
            data[bot_1][bot_2] = f"{results['Black']}-{results['Red']}"
        else:
            data[bot_1][bot_2] = f"{results['Red']}-{results['Black']}"

    with open(f'results_{filename}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)


print("--Red first--")
print("-mm1 x mm1-")
save_results(30, False, 3, 3)
print("-mm1 x mm3-")
save_results(10, False, 3, 4)
print("-mm3 x mm1-")
save_results(10, False, 4, 3)
print("-mm3 x mm3-")
save_results(10, False, 4, 4)
print("-mcts50 x random-")
save_results(20, False, 2, 1)
print("-random x mcts50-")
save_results(20, False, 1, 2)
print("-mcts50 x mm1-")
save_results(10, False, 2, 3)
print("-mm1 x mcts50-")
save_results(10, False, 3, 2)
print("-mcts50 x mm3-")
save_results(10, False, 2, 4)
print("-mm3 x mcts50-")
save_results(10, False, 4, 2)
print("-mcts50 x mcts50-")
save_results(10, False, 2, 2)
print("--Black first--")
print("-mm1 x mm1-")
save_results(30, True, 3, 3)
print("-mm1 x mm3-")
save_results(10, True, 3, 4)
print("-mm3 x mm1-")
save_results(10, True, 4, 3)
print("-mcts50 x random-")
save_results(10, True, 2, 1)
print("-random x mcts50-")
save_results(10, True, 1, 2)
print("-mcts50 x mm1-")
save_results(10, True, 2, 3)
print("-mm1 x mcts50-")
save_results(10, True, 3, 2)
print("-mcts50 x mm3-")
save_results(10, True, 2, 4)
print("-mm3 x mcts50-")
save_results(10, True, 4, 2)
print("-mcts50 x mcts50-")
save_results(10, True, 2, 2)
print("-mm3 x mm3-")
save_results(10, True, 4, 4)
