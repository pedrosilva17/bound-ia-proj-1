#
# Controlar board states para evitar stalemates
#

from Graph import Graph, Vertex, Piece


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

        self.forks = self.vertex_list
        self.paths = self.adj_list
        
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
        log = 1
        for fork in paths:
            if Piece.Empty not in [f.get_status() for f in paths[fork]] and fork.get_status() != Piece.Empty:
                if log == 1: 
                    print(Piece.Empty not in [f.get_status() for f in paths[fork]])
                    print(fork.get_status() != Piece.Empty)
                    log = 0
                self.winner = self.player_piece if self.get_opponent_piece() == fork.get_status() else self.get_opponent_piece()
                return
            
    
    def move(self, curr_index: int, move_index: int) -> None:
        # TODO
        if self.valid_move(curr_index, move_index):
            self.board.get_fork(move_index).set_status(self.player_piece)
            self.board.get_fork(curr_index).set_status(Piece.Empty)
            self.player_piece = Piece(3 - self.player_piece.value)  # Swap turns
        else:
            raise ValueError("Invalid move!")


    def valid_move(self, curr_index: int, move_index: int) -> bool:
        curr_fork = self.board.get_fork(curr_index)
        move_fork = self.board.get_fork(move_index)
        return (move_fork in self.board.get_paths()[curr_fork]
                and curr_fork.get_status() == self.player_piece
                and move_fork.get_status() == Piece.Empty)
    

    def __repr__(self):
        return self.board.__repr__()
    
class Bound:
    # TODO
    def __init__(self, player_1: Player, player_2: Player, initial_state: State) -> None:
        self.player_1 = player_1
        self.player_2 = player_2
        self.state = initial_state
        self.state_history = [self.state]

    
    def play(self) -> Player:
        self.state_history = [State(self.player_1)]
        winner = self.game_loop()
        return winner
    
    def game_loop(self) -> Player:
        while not self.state_history[-1].get_winner():
            piece = int(input("What piece do you move? (0-19) "))
            move = int(input("Where to? (0-19) "))
            try:
                self.state.move(piece, move)
                self.state.update_winner()
                self.state_history.append(self.state)
            except ValueError:
                print("Invalid move. Try again")
            print(self.state)
        return self.state.get_winner()
