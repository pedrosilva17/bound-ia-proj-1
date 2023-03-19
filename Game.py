#
# Controlar board states para evitar stalemates
#

from Graph import Graph, Vertex, Piece
from Interface import Interface
from utils import parse_int_input
import random, time, re, numpy


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
            
    
    def move(self, curr_index: int, move_index: int) -> None:
        # TODO
        if self.valid_move(curr_index, move_index, self.player_piece):
            self.board.get_fork(move_index).set_status(self.player_piece)
            self.board.get_fork(curr_index).set_status(Piece.Empty)
            self.player_piece = Piece(3 - self.player_piece.value)  # Swap turns
        else:
            raise ValueError("Invalid move!")


    def valid_move(self, curr_index: int, move_index: int, player_piece: Piece) -> bool:
        curr_fork = self.board.get_fork(curr_index)
        move_fork = self.board.get_fork(move_index)
        return (move_fork in self.board.get_paths()[curr_fork]
                and curr_fork.get_status() == player_piece
                and move_fork.get_status() == Piece.Empty)
    
    
    def available_moves(self, player_piece: Piece) -> list:
        moves = []
        for i in range(self.board.get_outer_length() * 4):
            for j in self.board.get_siblings(i):
                if self.valid_move(i, j.get_index(), player_piece):
                    moves.append((i, j.get_index()))
        return moves
    
    
    def count_moves(self, player_piece: Piece):
        return len(self.available_moves(player_piece))
    
    
    def list_moves(self, player_piece: Piece):
        player_path_status = [list(map(lambda fork: fork.get_status(), v)) for k, v in self.board.get_paths().items() if k.get_status() == player_piece]
        return [path.count(Piece.Empty) for path in player_path_status]
    
        
    def __repr__(self):
        return self.board.__repr__()
    
class Bound:

    def __init__(self, player_1: Player, player_2: Player, outer_length: int, free_space: int) -> None:
        self.player_1 = player_1
        self.player_2 = player_2
        self.outer_length = outer_length
        
        self.state = State(self.player_1, Board(outer_length))
        self.ui = Interface()
        self.initial_board = self.get_state().get_board()
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
        self.state_history = [self.state]
        match mode:
            case 1:
                winner = self.game_loop(self.ask_move, self.ask_move)
            case 2:
                winner = self.game_loop(self.ask_move, self.random_move)
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
            player_func()
            player_func, next_player_func = next_player_func, player_func
            # print(self.state)
            self.ui.render(self.state.get_board())
            
        return self.state.get_winner()

    
    def ask_move(self):
        piece = parse_int_input(f"{self.state.get_player_piece().name}, What piece do you move?\n",
                                0, self.state.get_board().get_outer_length() * 4 - 1)
        move = parse_int_input("Where do you move it?\n",
                               0, self.state.get_board().get_outer_length() * 4 - 1)
        try:
            self.state.move(piece, move)
            self.state.update_winner()
            self.state_history.append(self.state)
        except ValueError:
            print("Invalid move. Try again")

    
    def random_move(self):
        moves = self.state.available_moves(self.state.get_player_piece())
        piece, move = moves[random.randint(0, len(moves) - 1)]
        self.state.move(piece, move)
        self.state.update_winner()
        self.state_history.append(self.state)


def evaluate_state_1(state: State):
    return state.count_moves(state.get_player_piece()) - state.count_moves(state.get_opponent_piece())
    
    
def evaluate_state_2(state: State):
    return numpy.prod(state.list_moves(state.get_player_piece())) - numpy.prod(state.list_moves(state.get_opponent_piece()))


def evaluate_state_3(state: State):
    return evaluate_state_1(state) + evaluate_state_2(state)


def execute_minimax_move(evaluate_func, depth: int):
    # TODO
    pass


def minimax(state: State, depth: int, alpha: int, beta: int, maximizing: bool, player: Player, evaluate_func):
    # TODO
    pass


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
        winner = game.play(1)
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