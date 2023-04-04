import math
import random
import re
from copy import deepcopy
from typing import Callable
import numpy
from Graph import Graph, Vertex, Piece
from Interface import Interface
from constants import BOT_NAME
from mcts import MCTS, MCTS_node
from utils import parse_int_input


class Player:
    """Class representing a game's player, storing its name and piece.
    """

    def __init__(self, index: int, piece: Piece, name: str = ""):
        """Initialize a new player.

        Args:
            index (int): The index (order) of the player. Only used to generate a default name.
            piece (Piece): The piece that the player controls.
            name (str, optional): The name of the player.
        """
        self.index = index
        self.piece = piece
        if name == "":
            self.name = f"Player-{index}"
        else:
            self.name = name

    def __repr__(self):
        return self.name


class Board(Graph):
    """Class representing a game's board, which is essentially an extension of a graph.

    Args:
        Graph (Graph): The graph class being extended.
    """

    def __init__(self, outer_length: int = 5):
        """Initialize an empty board with the given outer layer length.
        Its size will equal the layer's length times 4.

        Args:
            outer_length (int, optional): The length of the outer layer. Defaults to 5.
        """
        super().__init__(outer_length * 4)

        # Connect every vertex of index i with every vertex of index i+i, except for the last vertex
        for i in range(outer_length * 4 - 1):
            v1 = self.get_vertex(i)
            v2 = self.get_vertex((i + 1))
            self.add_edge(v1, v2)

            # Connect vertices of the outer layer with the vertices directly below them.
            if i in range(outer_length - 1):
                v3 = self.get_vertex(outer_length + 2 + i * 2)
                self.add_edge(v1, v3)

            # Connect vertices of the inner layer with the vertices directly above them.
            elif i in range(outer_length + 1, outer_length * 3 - 1, 2):
                v3 = self.get_vertex(outer_length * 3 + 1 +
                                     (i - outer_length - 1) // 2)
                self.add_edge(v1, v3)

        # Create loops inside the different layers
        self.add_edge(self.get_vertex(outer_length - 1), self.get_vertex(0))
        self.add_edge(
            self.get_vertex(outer_length * 3 - 1),
            self.get_vertex(outer_length))
        self.add_edge(self.get_vertex(outer_length * 4 - 1),
                      self.get_vertex(outer_length * 3))

        self.outer_length = outer_length
        self.forks = self.vertex_list
        self.paths = self.adj_list

    def get_fork(self, index: int) -> Vertex:
        """Get the fork corresponding to the given index.

        Args:
            index (int): The fork's index.

        Returns:
            Vertex: A fork from the board, which is an instance of the Vertex class.
        """
        return super().get_vertex(index)

    def __repr__(self):
        return super().__repr__()


class State:
    """Class representing a game state, which stores the board, the moving player and the winner (if one exists after the move)
    """

    def __init__(self, player: Player, board: Board = Board(5)):
        """Initialize a new state with the given player and board.

        Args:
            player (Player): The player to execute a move.
            board (Board, optional): The current board.
            Defaults to a new Board instance of outer length 5 (if it is an initial state).
        """
        self.board = board
        self.player_piece = player.piece
        self.winner = None

    def get_player_piece_list(self, player_piece: Piece) -> list:
        """Get the list of pieces from the state's player, given its piece type.

        Args:
            player_piece (Piece): The piece controller by the state's player.

        Returns:
            list: The list of indices of the state player's pieces.
        """
        return [i for i in self.board.forks if self.board.get_fork(i).status == player_piece]

    def get_opponent_piece(self) -> Piece:
        """Get the opposite of the state player's piece, which represents the opponent's piece in a game.

        Returns:
            Piece: The piece with a value opposite to the player.
        """
        # 3 - 1 = 2 and 3 - 2 = 1, 1 and 2 are the values for the Red and Black pieces
        return Piece(3 - self.player_piece.value)

    def update_winner(self):
        """Update the winner in case a piece has no moves left.
        """
        paths = self.board.paths
        for fork in paths:
            if Piece.Empty not in [
                    f.status for f in paths[fork]] and fork.status != Piece.Empty:
                self.winner = Piece(3 - fork.status.value)
                return

    def simulate_winner(self) -> Piece | None:
        """Check and return a winner if it exists, without updating the state.

        Returns:
            Piece: The winning piece type.
        """
        paths = self.board.paths
        for fork in paths:
            if Piece.Empty not in [
                    f.status for f in paths[fork]] and fork.status != Piece.Empty:
                return Piece(3 - fork.status.value)

    def move(self, curr_index: int, move_index: int, state_history: list):
        """Execute a move, given the indices of the moving piece and the
        target fork, as well as the state's history.

        Args:
            curr_index (int): The index of the piece to be moved.
            move_index (int): The index of the fork to place the piece.
            state_history (list): The game's state history.

        Raises:
            ValueError: The move is invalid.
        """
        if self.valid_move(
                curr_index, move_index, self.player_piece, state_history):
            self.board.get_fork(move_index).set_status(self.player_piece)
            self.board.get_fork(curr_index).set_status(Piece.Empty)
            self.player_piece = Piece(
                3 - self.player_piece.value)  # Swap turns
        else:
            raise ValueError("Invalid move!")

    def valid_move(
            self, curr_index: int, move_index: int, player_piece: Piece,
            state_history: list) -> bool:
        """Check if a move is valid or not.

        Args:
            curr_index (int): The index of the piece to be moved.
            move_index (int): The index of the fork to place the piece.
            player_piece (Piece): The state player's piece.
            state_history (list): The game's state history.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        curr_fork = self.board.get_fork(curr_index)
        move_fork = self.board.get_fork(move_index)

        """
        A move is valid if:
            - curr_fork points to a non-empty fork (a piece)
            - The piece belongs to the state player
            - The target fork is in the piece's neighbourhood
            - The target fork is empty
            - It does not restart a previously closed movement loop, up to a certain length
            More info on stalemates present on the game's rulebook.
        """
        if (move_fork in self.board.paths[curr_fork]
                and curr_fork.status == player_piece
                and move_fork.status == Piece.Empty):
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
        """Get the available moves a given player can execute.

        Args:
            player_piece (Piece): The player's piece type.
            state_history (list): The game's state history.

        Returns:
            list: List of moves, composed of tuples in the format (chosen_piece_idx, target_fork_idx).
        """
        moves = []
        for i in self.get_player_piece_list(player_piece):
            for j in self.board.get_siblings(i):
                if self.valid_move(
                        i, j.index,
                        player_piece, state_history):
                    moves.append((i, j.index))
        return moves

    def count_moves(self, player_piece: Piece, state_history: list) -> int:
        """Count the number of moves available to a given player.

        Args:
            player_piece (Piece): The player's piece type.
            state_history (list): The game's state history.

        Returns:
            int: The number of available moves.
        """
        return len(self.available_moves(player_piece, state_history))

    def count_middle_pieces(self, player_piece: Piece) -> int:
        """Count the amount of pieces from a given player in the middle layer of the board.

        Args:
            player_piece (Piece): The player's piece type.

        Returns:
            int: The number of pieces in the middle layer.
        """
        return sum(
            self.get_player_piece_list(player_piece).count(i)
            for i in range(
                self.board.outer_length, self.board.outer_length * 4))

    def list_moves(self, player_piece: Piece) -> list:
        """List the number of moves available for each piece, given a player.

        Args:
            player_piece (Piece): The player's piece type.

        Returns:
            list: A list of the number of possible moves for each player piece.
        """
        player_path_status = [
            list(map(lambda fork: fork.status, v)) for k,
            v in self.board.paths.items() if k.status == player_piece]
        return [path.count(Piece.Empty) for path in player_path_status]

    def is_final(self) -> bool:
        """Check if a state is final or not.

        Returns:
            bool: True if the state is final, False otherwise.
        """
        paths = self.board.paths
        for fork in paths:
            if Piece.Empty not in [
                    f.status for f in paths[fork]] and fork.status != Piece.Empty:
                return True
        return False

    # Two states are considered equal if the board is the same.
    def __eq__(self, state):
        return self.board == state.board

    def __repr__(self):
        return self.board.__repr__()


class Bound:
    """Class representing a game instance.
    """

    def __init__(
            self, player_1: Player, player_2: Player, outer_length: int = 5,
            free_space: int = 0):
        """Initialize a new Bound game between two given players, given a board's outer length 
        and the free space on the outer/inner layer chosen by one of the players.

        Args:
            player_1 (Player): The starting player.
            player_2 (Player): The second player.
            outer_length (int): The length of the outer layer.
            free_space (int): The free space on the outer/inner layer.
        """
        self.state_history = []
        self.player_1 = player_1
        self.player_2 = player_2
        self.outer_length = outer_length

        self.state = State(self.player_1, Board(outer_length))
        self.ui = Interface()
        self.initial_board = self.state.board
        self.place_pieces(free_space)

    def place_pieces(self, free_space: int):
        """Place the pieces on the outer/inner layers of the board, given an index of a fork to leave empty
        (mirrored on the opposite layer).

        Args:
            free_space (int): The free space on the outer/inner layer.
        """
        if self.player_1.piece == Piece.Red:
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

    def ask_bot(self, bot_1: int, bot_2: int) -> tuple[int, int]:
        """Ask the user for a bot difficulty, if not already defined.

        Args:
            bot_1 (int): The integer representing the first bot difficulty
            bot_2 (int): The integer representing the second bot difficulty
            The arguments can also have the value 0 if the user is to be asked the difficulties,
            or -1 on one of the arguments if the player is supposed to be a human.

        Returns:
            tuple[int, int]: A tuple composed of the two integers representing the chosen bots.
        """
        if bot_1 == 0:
            bot_1 = parse_int_input(
                "Choose the difficulty for computer 1, from 1 (Very Easy) to 4 (Hard):\n"
                "1 - The Squirrel (Random moves)\n"
                "2 - The Raccoon (MCTS depth 50)\n"
                "3 - The Deer (Minimax depth 1)\n"
                "4 - The Fox (Minimax depth 3)\n", 1, 4)
        if bot_2 == 0:
            bot_2 = parse_int_input(
                "Choose the difficulty for computer 2, from 1 (Very Easy) to 4 (Hard):\n"
                "1 - The Squirrel (Random moves)\n"
                "2 - The Raccoon (MCTS depth 50)\n"
                "3 - The Deer (Minimax depth 1)\n"
                "4 - The Fox (Minimax depth 3)\n", 1, 4)
        return bot_1, bot_2

    def choose_bot(self, bot_choice: int) -> tuple[Callable, int]:
        """Get the strategy used by the bot of the chosen difficuly, as well as its depth.

        Args:
            bot_choice (int): The chosen bot difficulty.

        Returns:
            tuple[Callable, int]: A tuple composed of the strategy's function and its depth
            (or 0 if no depth is needed).
        """
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
        """Start a new game with the initialized class attributes.

        Args:
            mode (int): The gamemode chosen in the menu or predefined, from 1 to 3.
            bot_1 (int, optional): The first chosen bot difficulty. Defaults to 0.
            bot_2 (int, optional): The second chosen bot difficulty. Defaults to 0.
            A bot difficulty value of 0 means that the user will have to be asked their
            desired one.

        Returns:
            Player: The player that won the game, after it is played.
        """
        state_copy = deepcopy(self.state)
        self.state_history = [state_copy]

        match mode:
            case 1:
                winner = self.game_loop(self.ask_move, self.ask_move)
            case 2:
                bot_1, _ = self.ask_bot(bot_1, -1)
                self.player_2.name = BOT_NAME[bot_1]
                bot_1, depth_1 = self.choose_bot(bot_1)
                winner = self.game_loop(
                    self.ask_move, bot_1, next_player_depth=depth_1)
            case 3:
                bot_1, bot_2 = self.ask_bot(bot_1, bot_2)
                self.player_1.name = BOT_NAME[bot_1]
                self.player_2.name = BOT_NAME[bot_2]
                bot_1, depth_1 = self.choose_bot(bot_1)
                bot_2, depth_2 = self.choose_bot(bot_2)
                winner = self.game_loop(
                    bot_1, bot_2, depth_1, depth_2)

        if self.player_1.piece == winner:
            input(
                f"Winner: {self.player_1.name} ({self.player_1.piece.name})")
            self.ui.quit()
            return self.player_1
        else:
            input(
                f"Winner: {self.player_2.name} ({self.player_2.piece.name})")
            self.ui.quit()
            return self.player_2

    def game_loop(
            self, player_func: Callable, next_player_func: Callable,
            player_depth: int = 0, next_player_depth: int = 0) -> Piece:
        """The main game loop. Consists of executing a move, swapping players and
        adding the state to the state history, verifying if a winner has been declared on each iteration.

        Args:
            player_func (Callable): The starting player's strategy.
            next_player_func (Callable): The second player's strategy.
            player_depth (int, optional): The starting player's depth. Defaults to 0 (Strategy doesn't need depth).
            next_player_depth (int, optional): The second player's depth. Defaults to 0 (Strategy doesn't need depth).

        Returns:
            Piece: The piece type that won the game.
        """
        self.ui.ui_init()
        self.ui.render(self.state.board)
        eval_func, next_eval_func = self.evaluate_state_4, self.evaluate_state_4
        while not self.state_history[-1].winner:
            valid = False
            match player_func.__name__:
                case "execute_minimax_move":
                    player_func(eval_func, player_depth)
                    eval_func, next_eval_func = next_eval_func, eval_func
                case "ask_move":
                    while not valid:
                        valid = player_func()
                case _:
                    player_func()
            player_func, next_player_func = next_player_func, player_func
            player_depth, next_player_depth = next_player_depth, player_depth
            self.ui.render(self.state.board)
            if len(self.state_history) > 20:
                self.state_history = self.state_history[1:]

        return self.state.winner

    def ask_move(self) -> bool:
        """Ask a human player for a move and execute it (if it is valid).

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        piece = parse_int_input(
            f"{self.state.player_piece.name}, What piece do you move?\n",
            0, self.state.board.outer_length * 4 - 1)
        move = parse_int_input("Where do you move it?\n", 0,
                               self.state.board.outer_length * 4 - 1)
        try:
            self.state.move(piece, move, self.state_history)
            self.state.update_winner()
            state_copy = deepcopy(self.state)
            self.state_history.append(state_copy)
            return True
        except ValueError:
            print("Invalid move. Try again!")
            return False

    def random_move(self):
        """Select a random available move and execute it.
        """
        moves = self.state.available_moves(
            self.state.player_piece,
            self.state_history)
        piece, move = moves[random.randint(0, len(moves) - 1)]
        print(f"Move ({self.state.player_piece.name}): {(piece, move)}")
        self.state.move(piece, move, self.state_history)
        self.state.update_winner()
        state_copy = deepcopy(self.state)
        self.state_history.append(state_copy)
        return True

    # evaluate_state_n -> Board evaluation functions used by minimax.

    def evaluate_state_1(self, state: State, caller: Piece) -> int | float:
        """Evaluates the board based on: sum(no_player_moves) - sum(no_opp_moves)

        Args:
            state (State): The state storing the board to evaluate.
            caller (Piece): The piece type of the player that called the strategy.

        Returns:
            int | float: The evaluation result as an integer, except if the result is infinity
            (which is considered a float)
        """
        player = len(
            state.available_moves(
                state.player_piece,
                self.state_history))
        opponent = len(
            state.available_moves(
                state.get_opponent_piece(),
                self.state_history))
        value = player - opponent
        if 0 in state.list_moves(state.get_opponent_piece()):
            value = math.inf
        elif 0 in state.list_moves(state.player_piece):
            value = -math.inf
        return value if caller == state.player_piece else -value

    def evaluate_state_2(self, state: State, caller):
        """Evaluates the board based on: prod(no_player_moves) - prod(no_opp_moves)

        Args:
            state (State): The state storing the board to evaluate.
            caller (Piece): The piece type of the player that called the strategy.

        Returns:
            int | float: The evaluation result as an integer, except if the result is infinity
            (which is considered a float)
        """
        player = numpy.prod(state.list_moves(state.player_piece))
        opponent = numpy.prod(state.list_moves(state.get_opponent_piece()))
        value = player - opponent
        if opponent == 0:
            value = math.inf
        elif player == 0:
            value = -math.inf
        return value if caller == state.player_piece else -value

    def evaluate_state_3(self, state: State, caller):
        """Evaluates the board based on the sum of the two previous evaluation functions.

        Args:
            state (State): The state storing the board to evaluate.
            caller (Piece): The piece type of the player that called the strategy.

        Returns:
            int | float: The evaluation result as an integer, except if the result is infinity
            (which is considered a float)
        """
        value = self.evaluate_state_1(
            state, caller) + self.evaluate_state_2(state, caller)
        return value if caller == state.player_piece else -value

    # This is our prefered evaluation function.
    # Tries to prioritize moves that take control of the middle layer of the board,
    # while still considering the available move advantage it generates.
    def evaluate_state_4(self, state: State, caller):
        """Evaluates the board based on: 
        prod(no_player_moves) - prod(no_opp_moves) + no_player_middle_pieces

        Args:
            state (State): The state storing the board to evaluate.
            caller (Piece): The piece type of the player that called the strategy.

        Returns:
            int | float: The evaluation result as an integer, except if the result is infinity
            (which is considered a float)
        """
        player = numpy.prod(state.list_moves(state.player_piece))
        opponent = numpy.prod(state.list_moves(state.get_opponent_piece()))
        value = player - opponent + state.count_middle_pieces(
            state.player_piece)
        if opponent == 0:
            value = math.inf
        elif player == 0:
            value = -math.inf
        return value if caller == state.player_piece else -value

    def execute_minimax_move(self, evaluate_func: Callable, depth: int):
        """Run minimax to evaluate possible moves and execute one of the best.

        Args:
            evaluate_func (Callable): The evaluation function to be used in the algorithm.
            depth (int): The algorithm's depth, excluding the call to this function.
        """
        move_eval_list = []
        for move in self.state.available_moves(
                self.state.player_piece,
                self.state_history):
            history_copy = deepcopy(self.state_history)
            state_copy = deepcopy(self.state)
            state_copy.move(move[0], move[1], history_copy)
            history_copy.append(state_copy)
            minimax_val = minimax(
                state_copy, depth, False, -math.inf, math.inf, history_copy,
                evaluate_func, self.state.player_piece)
            move_eval_list.append((move, minimax_val))
            if minimax_val == math.inf:
                break

        move_eval_list = sorted(
            move_eval_list, key=lambda k: (k[1], k[0][1]), reverse=True)
        move_eval_list = list(
            filter(
                lambda k: k[1] == move_eval_list[0][1],
                move_eval_list))

        best_move = move_eval_list[random.randint(0, len(move_eval_list)-1)][0]
        print(
            f"Best Move ({self.state.player_piece.name}): {best_move}, value {move_eval_list[0][1]}")
        self.state.move(best_move[0], best_move[1], self.state_history)
        self.state.update_winner()
        state_copy = deepcopy(self.state)
        self.state_history.append(state_copy)

    def execute_mcts(self, iteration_total: int = 50):
        """Run Monte Carlo Tree Search with a given number of iterations to rate
        available moves and execute a (potentially) good one.

        Args:
            iteration_total (int, optional): The number of iterations. Defaults to 50.
        """
        state_copy = deepcopy(self.state)
        history_copy = deepcopy(self.state_history)

        mcts_root = MCTS_node((state_copy, history_copy), None, None)

        mcts = MCTS(mcts_root, self.state.player_piece)
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
        print(
            f"Best Move ({self.state.player_piece.name}): {best_move.move}, value {best_move.value}")
        self.state.move(
            best_move.move[0],
            best_move.move[1],
            self.state_history)
        self.state.update_winner()
        state_copy = deepcopy(self.state)
        self.state_history.append(state_copy)


def minimax(
        state: State, depth: int, maximizing: bool, alpha: int, beta: int,
        state_history: list, evaluate_func: Callable, caller: Piece) -> int | float:
    """The minimax algorithm. Select the best possible move considering
    the caller and his opponent's choices (depending on the depth).

    Args:
        state (State): The game state.
        depth (int): The algorithm's depth.
        maximizing (bool): If the current depth stores the maximum value (True) or not (False).
        alpha (int): The lower value bound to consider.
        beta (int): The upper value bound to consider.
        state_history (list): The game's state history.
        evaluate_func (Callable): The function that will evaluate the board.
        caller (Piece): The piece type of the player who called the first iteration of minimax.

    Returns:
        int | float: The evaluation result as an integer, except if the result is infinity
        (which is considered a float)
    """
    if depth == 0 or state.is_final():
        return evaluate_func(state, caller)
    if maximizing:
        max_eval = -math.inf
        for move in state.available_moves(
                state.player_piece,
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
    for move in state.available_moves(state.player_piece, state_history):
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


def one_game():
    """Prepare a single game of Bound.
    """
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
                "Player 1 - Insert your name. You will play first.\n"
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
    """Quickly setup a game of Bound (mostly used during testing).
    """
    p1 = Player(1, Piece.Red, "player_1")
    p2 = Player(2, Piece.Black, "player_2")
    game = Bound(p1, p2, 5, 0)
    run = True
    while run:
        game.play(3)
        run = False


def run_games(n_games: int = 100, rev_start_order: bool = False, bot_1: int = 1,
              bot_2: int = 1) -> dict:
    """Run an arbitrary amount of computer vs computer games while storing the wins for each player.

    Args:
        n_games (int, optional): The amount of games to run. Defaults to 100.
        rev_start_order (bool, optional): True if the Black pieces start, False otherwise. Defaults to False.
        bot_1 (int, optional): The first bot's difficulty. Defaults to 1.
        bot_2 (int, optional): The second bot's difficulty. Defaults to 1.

    Returns:
        dict: A dictionary with the two piece types as keys and their respective amount
        of wins as values.
    """
    p1 = Player(1, Piece(Piece.Red), "Red")
    p2 = Player(2, Piece(Piece.Black), "Black")
    results = {"Red": 0, "Black": 0}
    for i in range(n_games):
        if rev_start_order:
            game = Bound(p2, p1, 5, 19)
        else:
            game = Bound(p1, p2, 5, 0)
        winner = game.play(3, bot_1, bot_2)
        print(f"Winner: {winner.get_name()}")
        results[str(winner.piece.name)] += 1
        print(i)
    print(results)
    return results
