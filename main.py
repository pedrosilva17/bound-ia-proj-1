from Game import State, Player, Piece

if __name__ == "__main__":
    p = Player(index=1, piece=Piece.Black)
    s = State(p)
    s.update_winner()
    print(s.get_board())
    print(s.get_winner())