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
        return self.next_player_piece
        
    def get_winner(self):
        return self.winner
        
    def update_winner(self):
        paths = self.board.get_paths()
        for fork in paths:
            if Piece.Empty not in [f.get_status() for f in paths[fork]] and fork.get_status() != Piece.Empty:
                self.winner = self.player_piece if self.next_player_piece == fork.get_status() else self.next_player_piece
                break
            
    
    def move(self, index: int) -> None:
        # TODO
        if self.board.get_fork(index).get_status() == Piece.Empty:
            self.board.get_fork(index).set_status(self.player_piece)
        self.player_piece = Piece(3 - self.player_piece.value)  # Swap turns
        return
    
class Bound:
    # TODO
    def __init__(self, player_1: Player, player_2: Player, state_list: list = []) -> None:
        self.player_1 = player_1
        self.player_2 = player_2
        self.state_list = state_list
        pass
    
    def play(self) -> None:
        pass
    
    def game_loop(self):
        pass
    
    
