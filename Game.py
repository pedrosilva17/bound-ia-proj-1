#
# Controlar board states para evitar stalemates
#

from copy import deepcopy
from Graph import Graph, Vertex, Piece
from Interface import Interface
from utils import parse_int_input
import random, time, re, numpy, math, timeit


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
            v2 = self.get_vertex((i+1))
            self.add_edge(v1, v2)
            
            if i in range(outer_length - 1):
                v3 = self.get_vertex(outer_length + 2 + i * 2)
                self.add_edge(v1, v3)
            elif i in range(outer_length + 1, outer_length * 3 - 1, 2):
                v3 = self.get_vertex(outer_length * 3 + 1 + (i - outer_length - 1) // 2)
                self.add_edge(v1, v3)
                
        self.add_edge(self.get_vertex(outer_length - 1), self.get_vertex(0))
        self.add_edge(self.get_vertex(outer_length * 3 - 1), self.get_vertex(outer_length))
        self.add_edge(self.get_vertex(outer_length * 4 - 1), self.get_vertex(outer_length * 3))
        
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
            
    
    def move(self, curr_index: int, move_index: int, state_history: list) -> None:
        # TODO
        if self.valid_move(curr_index, move_index, self.player_piece, state_history):
            self.board.get_fork(move_index).set_status(self.player_piece)
            self.board.get_fork(curr_index).set_status(Piece.Empty)
            self.player_piece = Piece(3 - self.player_piece.value)  # Swap turns
        else:
            raise ValueError("Invalid move!")

        return self

    def valid_move(self, curr_index: int, move_index: int, player_piece: Piece, state_history: list) -> bool:
        curr_fork = self.board.get_fork(curr_index)
        move_fork = self.board.get_fork(move_index)
        
        if (move_fork in self.board.get_paths()[curr_fork]
                and curr_fork.get_status() == player_piece
                and move_fork.get_status() == Piece.Empty):
            state_copy = deepcopy(self)
            state_copy.board.get_fork(move_index).set_status(state_copy.player_piece)
            state_copy.board.get_fork(curr_index).set_status(Piece.Empty)
            
            #print(state_history)
            state_list = state_history[:-1]
            state_list.reverse()
            
            try:
                idx = state_list.index(self)
                return state_list.index(state_copy) != idx - 1
            except ValueError:
                return True
        else:
            return False    
    
    def available_moves(self, player_piece: Piece, state_history: list) -> list:
        moves = []
        for i in range(self.board.get_outer_length() * 4):
            for j in self.board.get_siblings(i):
                if self.valid_move(i, j.get_index(), player_piece, state_history):
                    moves.append((i, j.get_index()))
        return moves
    
    def count_moves(self, player_piece: Piece, state_history: list):
        return len(self.available_moves(player_piece, state_history))

    def list_moves(self, player_piece: Piece):
        player_path_status = [list(map(lambda fork: fork.get_status(), v)) for k, v in self.board.get_paths().items() if k.get_status() == player_piece]
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

    def __init__(self, player_1: Player, player_2: Player, outer_length: int, free_space: int) -> None:
        self.player_1 = player_1
        self.player_2 = player_2
        self.outer_length = outer_length
        
        self.state = State(self.player_1, Board(outer_length))
        self.ui = Interface()
        self.initial_board = self.state.get_board()
        self.place_pieces(free_space)
    
    
    def get_state(self) -> State:
        return self.state
    
    
    def place_pieces(self, free_space: int) -> None:
        if self.player_1.get_piece() == Piece.Red:
            for i in range(self.outer_length):
                if i == free_space: continue
                self.initial_board.get_fork(i).set_status(Piece.Red)
            for j in range(self.outer_length * 3, self.outer_length * 4):
                if ((j == self.outer_length * 3 + free_space - 1) 
                    or (j == self.outer_length * 4 - 1 and free_space == 0)): continue
                self.initial_board.get_fork(j).set_status(Piece.Black)
        else:
            for i in range(self.outer_length * 3, self.outer_length * 4):
                if i == free_space: continue
                self.initial_board.get_fork(i).set_status(Piece.Black)
            for j in range(self.outer_length):
                if ((j == free_space - self.outer_length * 3 + 1) 
                    or (j == 0 and free_space == self.outer_length * 4 - 1)): continue
                self.initial_board.get_fork(j).set_status(Piece.Red)
    
    
    def play(self, mode: int) -> Player:
        state_copy = deepcopy(self.state)
        self.state_history = [state_copy]
        match mode:
            case 1:
                winner = self.game_loop(self.ask_move, self.ask_move)
            case 2:
                winner = self.game_loop(self.ask_move, self.execute_minimax_move)
            case 3:
                winner = self.game_loop(self.random_move, self.random_move)
    
        if self.player_1.get_piece() == winner:
            input("Winner: " + self.player_1.get_name())
            self.ui.quit()
            return self.player_1
        else:
            input("Winner: " + self.player_2.get_name())
            self.ui.quit()
            return self.player_2
    
    
    def game_loop(self, player_func, next_player_func) -> Player:
        self.ui.render(self.state.get_board())
        while not self.state_history[-1].get_winner():
            # print(self.state.list_moves(self.state.get_player_piece()), self.state.list_moves(Piece(3 - self.state.get_player_piece().value)))
            # print(evaluate_state_1(self.state))
            # print(evaluate_state_2(self.state))
            # print(evaluate_state_3(self.state))
            match player_func.__name__:
                case "execute_minimax_move":
                    player_func(self.evaluate_state_2, 3)
                case _:
                    player_func()
            player_func, next_player_func = next_player_func, player_func
            # print(self.state)
            self.ui.render(self.state.get_board())
            
        return self.state.get_winner()
    
    
    def available_moves(self, player_piece: Piece, state_history: list) -> list:
        moves = []
        for i in range(self.state.board.get_outer_length() * 4):
            for j in self.state.board.get_siblings(i):
                if self.state.valid_move(i, j.get_index(), player_piece, state_history):
                    moves.append((i, j.get_index()))
        return moves

    
    def ask_move(self):
        piece = parse_int_input(f"{self.state.get_player_piece().name}, What piece do you move?\n",
                                0, self.state.get_board().get_outer_length() * 4 - 1)
        move = parse_int_input("Where do you move it?\n",
                               0, self.state.get_board().get_outer_length() * 4 - 1)
        try:
            self.state.move(piece, move, self.state_history)
            self.state.update_winner()
            state_copy = deepcopy(self.state)
            self.state_history.append(state_copy)
        except ValueError:
            print("Invalid move. Try again")

    
    def random_move(self):
        moves = self.available_moves(self.state.get_player_piece(), self.state_history)
        piece, move = moves[random.randint(0, len(moves) - 1)]
        self.state.move(piece, move, self.state_history)
        self.state.update_winner()
        state_copy = deepcopy(self.state)
        self.state_history.append(state_copy)

    def evaluate_state_1(self, state: State, caller):
        value = len(state.available_moves(state.get_player_piece(), self.state_history)) - len(state.available_moves(state.get_opponent_piece(), self.state_history))
        return value if caller == state.get_player_piece() else -value
        
    def evaluate_state_2(self, state: State, caller):
        value = numpy.prod(state.list_moves(state.get_player_piece())) - numpy.prod(state.list_moves(state.get_opponent_piece()))
        return value if caller == state.get_player_piece() else -value

    def evaluate_state_3(self, state: State, caller):
        value = self.evaluate_state_1(state) + self.evaluate_state_2(state)
        return value if caller == state.get_player_piece() else -value

    def execute_minimax_move(self, evaluate_func, depth: int):
        move_eval_list = []
        for move in self.available_moves(self.state.get_player_piece(), self.state_history):
            history_copy = self.state_history
            state_copy = deepcopy(self.state)
            state_copy.move(move[0], move[1], history_copy)
            history_copy.append(state_copy)
            minimax_val = minimax(state_copy, depth, False, -math.inf, math.inf, history_copy, evaluate_func, self.state.get_player_piece())
            move_eval_list.append((move, minimax_val))
        move_eval_list = sorted(move_eval_list, key = lambda k: k[1], reverse=True)
        print(move_eval_list)
        best_move = move_eval_list[0][0]

        self.state.move(best_move[0], best_move[1], self.state_history)
        self.state.update_winner()
        state_copy = deepcopy(self.state)
        self.state_history.append(state_copy)

def minimax(state: State, depth: int,maximizing: bool, alpha: int, beta: int, state_history, evaluate_func, caller):
    if depth == 0 or state.is_final(): return evaluate_func(state, caller)
    if maximizing:
        maxEval = -math.inf
        for move in state.available_moves(state.get_player_piece(), state_history):
            state_copy = deepcopy(state)
            history_copy = state_history
            state_copy.move(move[0], move[1], history_copy)
            history_copy.append(state_copy)
            evaluation = minimax(state_copy, depth-1, False, alpha, beta, state_history, evaluate_func, caller)
            maxEval = max(maxEval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha: break
        return maxEval
        
    minEval = math.inf
    for move in state.available_moves(state.get_player_piece(), state_history):
        state_copy = deepcopy(state)
        history_copy = deepcopy(state_history)
        state_copy.move(move[0], move[1], history_copy)
        history_copy.append(state_copy)
        evaluation = minimax(state_copy, depth-1, True, alpha, beta, history_copy, evaluate_func, caller)
        minEval = min(minEval, evaluation)
        beta = min(beta, evaluation)
        if beta <= alpha: break
    return minEval

def execute_mcts(state, player, state_history, iteration_total=50):

    mcts_root = MCTS_node(0, (state, state_history), None, None)

    mcts = MCTS(mcts_root, player)

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

    return mcts.best_choice()

# def mcts_expand(root, player, state_history, depth):
#     children = dict()
#     children[root] = (None, (root, state_history))
#     valid_moves = root.get_valid_moves(n_player, children)
#     node_states = mcts_create_states(valid_moves, player, state_history)
#     children[node] = (move, node_states)

# def mcts_create_states(moves, player, state_history):
#     states = dict()
#     for move in moves:
#         state_copy = deepcopy(state)
#         history_copy = state_history
#         state_copy.move(move[0], move[1], history_copy)
#         history_copy.append(state_copy)
#         states[move] = (state_copy, history_copy)
#     return states

# def mcts_simulate(state, player, state_history):
#     moves = state.available_moves(player, state_history)
#     piece, move = moves[random.randint(0, len(moves) - 1)]
#     final = false
#     n_state = state
#     while not final:
#         state_copy = deepcopy(n_state)
#         history_copy = state_history
#         state_copy.move(move[0], move[1], history_copy)
#         if state_copy.is_final():
#             return evaluate_final(state_copy, player)
#     return

# def evaluate_final(state, player):
#     paths = self.board.get_paths()
#     for fork in paths:
#         if Piece.Empty not in [f.get_status() for f in paths[fork]] and fork.get_status() != Piece.Empty:
#             if Piece(3 - fork.get_status().value) == player:
#                 return 1
#             else:
#                 return -1  
#     return None

def one_game() -> None:
    game_mode = parse_int_input("Choose your gamemode:\n"
                                "1- Human vs Human\n"
                                "2- Human vs Computer\n"
                                "3- Computer vs Computer\n",
                                1, 3)
    outer_length = parse_int_input("Choose a size for the board's outer circle.\n"
                                   "The board's size will be 4 times that number.\n"
                                   "Must be between 3 and 10, values between 5 and 8 work best.\n",
                                   3, 10)
    p1_name = re.sub(r'\W+', '', input("Player 1 - Insert your name. You will play first.\n"
                                       "Only alphanumeric characters and underscores will be stored.\n"))
    p2_name = re.sub(r'\W+', '', input("Player 2 - Insert your name.\n"
                                       "Only alphanumeric characters and underscores will be stored.\n"))
    p1_piece = parse_int_input("Player 1 - Choose your piece:\n"
                               "1 - Red, the outer pieces.\n"
                               "2 - Black, the inner pieces.\n",
                               1, 2)
    p2_piece = Piece(3 - p1_piece)
    if p1_piece == 1:
        free_space = parse_int_input(f"Player 1 - Choose the free space in your piece placement.\n"
                                     f"Keep in mind the Red pieces are placed on the outer circle.\n"
                                     f"Valid empty spaces: 0-{outer_length - 1}\n",
                                     0, outer_length - 1)
    else:
        free_space = parse_int_input(f"Player 1 - Choose the free space in your piece placement.\n"
                                     f"Keep in mind the Black pieces are placed on the inner circle.\n"
                                     f"Valid empty spaces: {outer_length * 3}-{outer_length * 4 - 1}\n",
                                     outer_length * 3, outer_length * 4 - 1)

    p1 = Player(1, Piece(p1_piece), p1_name)
    p2 = Player(2, Piece(p2_piece), p2_name)
    game = Bound(p1, p2, outer_length, free_space)
    run = True
    while run:
        winner = game.play(game_mode)
        run = False


def example():
    p1 = Player(1, Piece.Red, "player_1")
    p2 = Player(2, Piece.Black, "player_2")
    game = Bound(p1, p2, 5, 0)
    run = True
    while run:
        winner = game.play(2)
        run = False



def run_games(n_games: int) -> None:
    p1 = Player(1, Piece(Piece.Red), "Red")
    p2 = Player(2, Piece(Piece.Black), "Black")
    results = {"Red": 0, "Black": 0}
    for i in range(n_games):
        game = Bound(p1, p2, 5, 0)
        winner = game.play(3)
        print(f"Winner: {winner.get_name()}")
        results[winner.get_name()] += 1
    print(results)