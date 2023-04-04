import csv
from Game import run_games
from constants import BOT_DIFFICULTY

start_piece = {False: "Red", True: "Black"}
bot_depth = {3: "1", 4: "3"}


def save_results(n_games: int, rev_start_order: bool, bot_1: int, bot_2: int):
    results = run_games(n_games, rev_start_order, bot_1, bot_2)
    filename = "black" if rev_start_order else "red"
    """
    with open("results.txt", mode='a+', encoding="utf-8") as file:
        file.write(
            f"LEVEL {BOT_DIFFICULTY[bot_1]}" +
            (f" DEPTH {bot_depth[bot_1]}" if bot_1 == 3 or bot_1 == 4 else "") +
            f" VS LEVEL {BOT_DIFFICULTY[bot_2]}" +
            (f" DEPTH {bot_depth[bot_2]}" if bot_2 == 3 or bot_2 == 4 else "") +
            f", STARTS: {start_piece[rev_start_order]}\n")
        file.write(f"Red: {results['Red']} Black: {results['B'new value'lack']}\n")
        file.write("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n\n")
    """
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
"""
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
"""
print("-mm3 x mcts50-")
save_results(10, False, 4, 2)
"""
"""
print("--Black first--")
"""
print("-mm1 x mm1-")
save_results(30, True, 3, 3)
print("-mm1 x mm3-")
save_results(10, True, 3, 4)
print("-mm3 x mm1-")
save_results(10, True, 4, 3)
"""
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
print("-mcts50 x mcts50- (red)")
save_results(10, False, 2, 2)
print("-mcts50 x mcts50- (black)")
save_results(10, True, 2, 2)
"""
print("-mm3 x mm3-")
save_results(10, True, 4, 4)
"""