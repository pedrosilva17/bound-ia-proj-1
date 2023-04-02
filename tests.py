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
        data[bot_1][bot_2] = f"{results['Red']}-{results['Black']}"
    
    with open(f'results_{filename}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)

save_results(1, False, 4, 3)
save_results(1, False, 3, 4)

