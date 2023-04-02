#
# Controlar board states para evitar stalemates
#
import time
import math
import random
import re
from copy import deepcopy
from typing import Callable

import numpy

from Graph import Graph, Vertex, Piece
from Interface import Interface
from mcts import MCTS, MCTS_node
from utils import parse_int_input


class Player:

    def __init__(self, index: int, piece: Piece, name: str = "") -> None:
        self.index = index
        self.piece = piece
        if name == "":
            self.name = f"Player-{index}"
        else:
            self.name = name

    def get_index(self):
        return self.index

    def get_piece(self):
        return self.piece

    def get_opponent_piece(self):
        return Piece(3 - self.piece.value)

    def get_name(self):
        return self.name

    def __repr__(self):
        return self.name


class Board(Graph):

    def __init__(self, outer_length: int = 5) -> None:
        super().__init__(outer_length * 4)

        for i in range(outer_length * 4 - 1):
            v1 = self.get_vertex(i)
            v2 = self.get_vertex((i + 1))
            self.add_edge(v1, v2)

            if i in range(outer_length - 1):
                v3 = self.get_vertex(outer_length + 2 + i * 2)
                self.add_edge(v1, v3)
            elif i in range(outer_length + 1, outer_length * 3 - 1, 2):
                v3 = self.get_vertex(outer_length * 3 + 1 +
                                     (i - outer_length - 1) // 2)
                self.add_edge(v1, v3)

        self.add_edge(self.get_vertex(outer_length - 1), self.get_vertex(0))
        self.add_edge(
            self.get_vertex(outer_length * 3 - 1),
            self.get_vertex(outer_length))
        self.add_edge(self.get_vertex(outer_length * 4 - 1),
                      self.get_vertex(outer_length * 3))

        self.outer_length = outer_length
        self.forks = self.vertex_list
        self.paths = self.adj_list

    def get_outer_length(self) -> int:
        return self.outer_length

    def get_fork(self, index: int) -> Vertex:
        return super().get_vertex(index)

    def get_paths(self) -> dict:
        return self.paths

    def get_forks(self) -> dict:
        return self.forks

    def __repr__(self):
        return super().__repr__()


class State:

    def __init__(self, player: Player, board: Board = Board(5)) -> None:
        self.board = board
        self.player_piece = player.get_piece()
        self.winner = None

    def get_board(self):
        return self.board

    def get_player_piece(self):
        return self.player_piece

    def get_player_piece_list(self, player_piece: Piece):
        return [i for i in self.board.get_forks() if self.board.get_fork(i).get_status() == player_piece]

    def get_opponent_piece(self):
        return Piece(3 - self.player_piece.value)

    def get_winner(self) -> Player:
        return self.winner

    def update_winner(self):
        paths = self.board.get_paths()
        for fork in paths:
            if Piece.Empty not in [f.get_status() for f in paths[fork]] and fork.get_status() != Piece.Empty:
                self.winner = Piece(3 - fork.get_status().value)
                return

    def simulate_winner(self):
        paths = self.board.get_paths()
        for fork in paths:
            if Piece.Empty not in [f.get_status() for f in paths[fork]] and fork.get_status() != Piece.Empty:
                return Piece(3 - fork.get_status().value)

    def move(self, curr_index: int, move_index: int, state_history: list) -> None:
        # TODO
        # print(self.valid_move(curr_index, move_index, self.player_piece, state_history))
        if self.valid_move(
                curr_index, move_index, self.player_piece, state_history):
            self.board.get_fork(move_index).set_status(self.player_piece)
            self.board.get_fork(curr_index).set_status(Piece.Empty)
            self.player_piece = Piece(
                3 - self.player_piece.value)  # Swap turns
        else:
            raise ValueError("Invalid move!")

        return self

    def valid_move(
            self, curr_index: int, move_index: int, player_piece: Piece,
            state_history: list) -> bool:
        curr_fork = self.board.get_fork(curr_index)
        move_fork = self.board.get_fork(move_index)

        if (move_fork in self.board.get_paths()[curr_fork]
                and curr_fork.get_status() == player_piece
                and move_fork.get_status() == Piece.Empty):
            state_copy = deepcopy(self)
            state_copy.board.get_fork(move_index).set_status(
                state_copy.player_piece)
            state_copy.board.get_fork(curr_index).set_status(Piece.Empty)

            state_list = state_history[:-1]
            state_list.reverse()

            try:
                idx = state_list.index(self)
                return state_list.index(state_copy) != idx - 1
            except ValueError:
                return True
        else:
            return False

    def available_moves(
            self, player_piece: Piece, state_history: list) -> list:
        moves = []
        for i in self.get_player_piece_list(player_piece):
            for j in self.board.get_siblings(i):
                if self.valid_move(
                        i, j.get_index(),
                        player_piece, state_history):
                    moves.append((i, j.get_index()))
        return moves

    def count_moves(self, player_piece: Piece, state_history: list):
        return len(self.available_moves(player_piece, state_history))

    def count_middle_pieces(self, player_piece: Piece):
        return sum(
            self.get_player_piece_list(player_piece).count(i)
            for i in range(
                self.board.outer_length, self.board.outer_length * 4))

    def list_moves(self, player_piece: Piece):
        player_path_status = [
            list(map(lambda fork: fork.get_status(),
                     v)) for k, v in self.board.get_paths().items()
            if k.get_status() == player_piece]
        return [path.count(Piece.Empty) for path in player_path_status]

    def is_final(self):
        paths = self.board.get_paths()
        for fork in paths:
            if Piece.Empty not in [f.get_status() for f in paths[fork]] and fork.get_status() != Piece.Empty:
                return True
        return False

    def __eq__(self, state):
        return self.board == state.board

    def __repr__(self):
        return self.board.__repr__()


class Bound:

    def __init__(
            self, player_1: Player, player_2: Player, outer_length: int,
            free_space: int) -> None:
        self.state_history = []
        self.player_1 = player_1
        self.player_2 = player_2
        self.outer_length = outer_length

        self.state = State(self.player_1, Board(outer_length))
        # self.ui = Interface()
        self.initial_board = self.state.get_board()
        self.place_pieces(free_space)

    def get_state(self) -> State:
        return self.state

    def place_pieces(self, free_space: int) -> None:
        if self.player_1.get_piece() == Piece.Red:
            for i in range(self.outer_length):
                if i == free_space:
                    continue
                self.initial_board.get_fork(i).set_status(Piece.Red)
            for j in range(self.outer_length * 3, self.outer_length * 4):
                if ((j == self.outer_length * 3 + free_space - 1)
                        or (j == self.outer_length * 4 - 1 and free_space == 0)):
                    continue
                self.initial_board.get_fork(j).set_status(Piece.Black)
        else:
            for i in range(self.outer_length * 3, self.outer_length * 4):
                if i == free_space:
                    continue
                self.initial_board.get_fork(i).set_status(Piece.Black)
            for j in range(self.outer_length):
                if ((j == free_space - self.outer_length * 3 + 1)
                        or (j == 0 and free_space == self.outer_length * 4 - 1)):
                    continue
                self.initial_board.get_fork(j).set_status(Piece.Red)

    def ask_bot(self, bot_1, bot_2) -> tuple[Callable, Callable, int, int]:
        if bot_1 == 0:
            bot_1 = parse_int_input(
                "Choose the difficulty for computer 1, from 1 (Very Easy) to 4 (Hard):\n"
                "1- The Clueless (Random moves)\n"
                "2- The Statistician (MCTS depth 50)\n"
                "3- The Greedy (Minimax depth 1)\n"
                "4- The Omnissiah (Minimax depth 3)\n", 1, 4)
        if bot_2 == 0:
            bot_2 = parse_int_input(
                "Choose the difficulty for computer 2, from 1 (Very Easy) to 4 (Hard):\n"
                "1- The Clueless (Random moves)\n"
                "2- The Statistician (MCTS depth 50)\n"
                "3- The Greedy (Minimax depth 1)\n"
                "4- The Omnissiah (Minimax depth 3)\n", 1, 4)
        bot_1, depth_1 = self.choose_bot(bot_1)
        bot_2, depth_2 = self.choose_bot(bot_2)
        return bot_1, depth_1, bot_2, depth_2

    def choose_bot(self, bot_choice: int) -> tuple[Callable, int]:
        match bot_choice:
            case 1:
                return (self.random_move, 0)
            case 2:
                return (self.execute_mcts, 0)
            case 3:
                return (self.execute_minimax_move, 1)
            case 4:
                return (self.execute_minimax_move, 3)

    def play(self, mode: int, bot_1: int = 0, bot_2: int = 0) -> Player:
        state_copy = deepcopy(self.state)
        self.state_history = [state_copy]

        match mode:
            case 1:
                winner = self.game_loop(self.ask_move, self.ask_move)
            case 2:
                bot_1, depth_1, _, _ = self.ask_bot(bot_1, 1)
                winner = self.game_loop(
                    self.ask_move, bot_1, next_player_depth=depth_1)
            case 3:
                bot_1, depth_1, bot_2, depth_2 = self.ask_bot(bot_1, bot_2)
                winner = self.game_loop(
                    bot_1, bot_2, depth_1, depth_2)

        if self.player_1.get_piece() == winner:
            # input("Winner: " + self.player_1.get_name())
            # self.ui.quit()
            return self.player_1
        else:
            # input("Winner: " + self.player_2.get_name())
            # self.ui.quit()
            return self.player_2

    def game_loop(
            self, player_func, next_player_func, player_depth=0,
            next_player_depth=0) -> Player:
        # self.ui.ui_init()
        # self.ui.render(self.state.get_board())
        eval_func, next_eval_func = self.evaluate_state_4, self.evaluate_state_4
        # print(player_depth, next_player_depth)
        while not self.state_history[-1].get_winner():
            valid = False
            # print(self.state.list_moves(self.state.get_player_piece()), self.state.list_moves(Piece(3 - self.state.get_player_piece().value)))
            # print(evaluate_state_1(self.state))
            # print(evaluate_state_2(self.state))
            # print(evaluate_state_3(self.state))
            match player_func.__name__:
                case "execute_minimax_move":
                    player_func(eval_func, player_depth)
                    eval_func, next_eval_func = next_eval_func, eval_func
                case "execute_mcts":
                    player_func()
                case _:
                    while not valid:
                        valid = player_func()
            player_func, next_player_func = next_player_func, player_func
            player_depth, next_player_depth = next_player_depth, player_depth
            # print(self.state)
            # print(self.state_history)
            # self.ui.render(self.state.get_board())
            if len(self.state_history) > 20:
                self.state_history = self.state_history[1:]

        return self.state.get_winner()

    def available_moves(
            self, player_piece: Piece, state_history: list) -> list:
        moves = []
        for i in self.state.get_player_piece_list(player_piece):
            for j in self.state.board.get_siblings(i):
                if self.state.valid_move(
                        i, j.get_index(),
                        player_piece, state_history):
                    moves.append((i, j.get_index()))
        moves = sorted(moves, key=lambda k: k[1], reverse=True)
        return moves

    def ask_move(self):
        piece = parse_int_input(
            f"{self.state.get_player_piece().name}, What piece do you move?\n",
            0, self.state.get_board().get_outer_length() * 4 - 1)
        move = parse_int_input("Where do you move it?\n", 0,
                               self.state.get_board().get_outer_length() * 4 - 1)
        try:
            self.state.move(piece, move, self.state_history)
            self.state.update_winner()
            state_copy = deepcopy(self.state)
            self.state_history.append(state_copy)
            return True
        except ValueError:
            print("Invalid move. Try again")
            return False

    def random_move(self):
        moves = self.available_moves(
            self.state.get_player_piece(),
            self.state_history)
        piece, move = moves[random.randint(0, len(moves) - 1)]
        self.state.move(piece, move, self.state_history)
        self.state.update_winner()
        state_copy = deepcopy(self.state)
        self.state_history.append(state_copy)
        return True

    def evaluate_state_1(self, state: State, caller):
        player = len(
            state.available_moves(
                state.get_player_piece(),
                self.state_history))
        opponent = len(
            state.available_moves(
                state.get_opponent_piece(),
                self.state_history))
        value = player - opponent
        if opponent == 0:
            value = math.inf
        elif player == 0:
            value = -math.inf
        return value if caller == state.get_player_piece() else -value

    def evaluate_state_2(self, state: State, caller):
        player = numpy.prod(state.list_moves(state.get_player_piece()))
        opponent = numpy.prod(state.list_moves(state.get_opponent_piece()))
        value = player - opponent
        if opponent == 0:
            value = math.inf
        elif player == 0:
            value = -math.inf
        return value if caller == state.get_player_piece() else -value

    def evaluate_state_3(self, state: State, caller):
        value = self.evaluate_state_1(
            state, caller) + self.evaluate_state_2(state, caller)
        return value if caller == state.get_player_piece() else -value

    def evaluate_state_4(self, state: State, caller):
        player = numpy.prod(state.list_moves(state.get_player_piece()))
        opponent = numpy.prod(state.list_moves(state.get_opponent_piece()))
        value = player - opponent + state.count_middle_pieces(
            state.get_player_piece()) - state.count_middle_pieces(state.get_opponent_piece())
        if opponent == 0:
            value = math.inf
        elif player == 0:
            value = -math.inf
        return value if caller == state.get_player_piece() else -value

    def execute_minimax_move(self, evaluate_func, depth: int):
        move_eval_list = []
        for move in self.state.available_moves(
                self.state.get_player_piece(),
                self.state_history):
            history_copy = deepcopy(self.state_history)
            state_copy = deepcopy(self.state)
            state_copy.move(move[0], move[1], history_copy)
            history_copy.append(state_copy)
            # print(state_copy)
            minimax_val = minimax(
                state_copy, depth, False, -math.inf, math.inf, history_copy,
                evaluate_func, self.state.get_player_piece())
            move_eval_list.append((move, minimax_val))
            if minimax_val == math.inf:
                break

        move_eval_list = sorted(
            move_eval_list, key=lambda k: (k[1], k[0][1]), reverse=True)
        move_eval_list = list(
            filter(
                lambda k: k[1] == move_eval_list[0][1],
                move_eval_list))
        # print(move_eval_list)
        best_move = move_eval_list[random.randint(0, len(move_eval_list)-1)][0]

        # print(best_move[0], best_move[1])
        # print(self.state.valid_move(best_move[0], best_move[1], self.state.get_player_piece(), self.state_history))
        self.state.move(best_move[0], best_move[1], self.state_history)
        self.state.update_winner()
        state_copy = deepcopy(self.state)
        self.state_history.append(state_copy)

    def execute_mcts(self, iteration_total=50):
        state_copy = deepcopy(self.state)
        history_copy = deepcopy(self.state_history)

        mcts_root = MCTS_node((state_copy, history_copy), None, None)

        mcts = MCTS(mcts_root, self.state.get_player_piece())
        iteration = iteration_total

        while (iteration > 0):
            # Select
            node = mcts.select()
            # Expand
            leaf = mcts.expand(node)
            # Simulate
            result = mcts.simulate(leaf)
            # Back Propagate
            mcts.back_propagate(leaf, result)
            iteration -= 1

        best_move = mcts.best_choice()
        # print("Best Move: ", best_move.move, "\nWith value: ", best_move.value)
        self.state.move(
            best_move.move[0],
            best_move.move[1],
            self.state_history)
        self.state.update_winner()
        state_copy = deepcopy(self.state)
        self.state_history.append(state_copy)


def minimax(
        state: State, depth: int, maximizing: bool, alpha: int, beta: int,
        state_history, evaluate_func, caller):
    if depth == 0 or state.is_final():
        return evaluate_func(state, caller)
    if maximizing:
        max_eval = -math.inf
        for move in state.available_moves(
                state.get_player_piece(),
                state_history):
            state_copy = deepcopy(state)
            history_copy = deepcopy(state_history)
            state_copy.move(move[0], move[1], history_copy)
            history_copy.append(state_copy)
            evaluation = minimax(
                state_copy, depth - 1, False, alpha, beta, history_copy,
                evaluate_func, caller)
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval

    min_eval = math.inf
    for move in state.available_moves(state.get_player_piece(), state_history):
        state_copy = deepcopy(state)
        history_copy = deepcopy(state_history)
        state_copy.move(move[0], move[1], history_copy)
        history_copy.append(state_copy)
        evaluation = minimax(
            state_copy, depth - 1, True, alpha, beta, history_copy,
            evaluate_func, caller)
        min_eval = min(min_eval, evaluation)
        beta = min(beta, evaluation)
        if beta <= alpha:
            break
    return min_eval


def one_game() -> None:
    game_mode = parse_int_input("Choose your gamemode:\n"
                                "1- Human vs Human\n"
                                "2- Human vs Computer\n"
                                "3- Computer vs Computer\n",
                                1, 3)
    outer_length = parse_int_input(
        "Choose a size for the board's outer circle.\n"
        "The board's size will be 4 times that number.\n"
        "Must be between 3 and 10, values between 5 and 8 work best.\n", 3, 10)
    p1_name = "Computer 1"
    p2_name = "Computer 2"
    p1_piece = 1
    free_space = 0
    if game_mode < 3:
        p1_name = re.sub(
            r'\W+', '',
            input(
                "Player 1 - Insert your n        print(len(range(self.outer_length * 3, self.outer_length * 4)))ame. You will play first.\n"
                "Only alphanumeric characters and underscores will be stored.\n"))
        p1_piece = parse_int_input("Player 1 - Choose your piece:\n"
                                   "1 - Red, the outer pieces.\n"
                                   "2 - Black, the inner pieces.\n",
                                   1, 2)
        if p1_piece == 1:
            free_space = parse_int_input(
                f"Player 1 - Choose the free space in your piece placement.\n"
                f"Keep in mind the Red pieces are placed on the outer circle.\n"
                f"Valid empty spaces: 0-{outer_length - 1}\n", 0, outer_length - 1)
        else:
            free_space = parse_int_input(
                f"Player 1 - Choose the free space in your piece placement.\n"
                f"Keep in mind the Black pieces are placed on the inner circle.\n"
                f"Valid empty spaces: {outer_length * 3}-{outer_length * 4 - 1}\n",
                outer_length * 3, outer_length * 4 - 1)
        if game_mode < 2:
            p2_name = re.sub(
                r'\W+', '',
                input(
                    "Player 2 - Insert your name.\n"
                    "Only alphanumeric characters and underscores will be stored.\n"))

    p2_piece = Piece(3 - p1_piece)
    p1 = Player(1, Piece(p1_piece), p1_name)
    p2 = Player(2, Piece(p2_piece), p2_name)
    game = Bound(p1, p2, outer_length, free_space)
    run = True
    while run:
        game.play(game_mode)
        run = False


def example():
    p1 = Player(1, Piece.Red, "player_1")
    p2 = Player(2, Piece.Black, "player_2")
    game = Bound(p1, p2, 5, 0)
    run = True
    while run:
        game.play(3)
        run = False


def run_games(n_games: int = 100, rev_start_order: bool = False, bot_1: int = 1, bot_2: int = 2) -> dict:
    p1 = Player(1, Piece(Piece.Red), "Red")
    p2 = Player(2, Piece(Piece.Black), "Black")
    results = {"Red": 0, "Black": 0}
    for i in range(n_games):
        if rev_start_order:
            game = Bound(p2, p1, 5, 19)
        else:
            game = Bound(p1, p2, 5, 0)
        winner = game.play(3, bot_1, bot_2)
        # print(f"Last move: {game.state.get_opponent_piece()}")
        print(f"Winner: {winner.get_name()}")
        results[winner.get_name()] += 1
        # print(i)
    print(results)
    return results
