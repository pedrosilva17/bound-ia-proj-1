#
# Deixar escolher colocação das 4 peças (jogador escolhe espaço que quer deixar livre, espaço livre do j2 colocado do lado oposto)
#

from Game import Bound, State, Player, Piece
from Interface import Interface

if __name__ == "__main__":
    p1 = Player(1, Piece.Red)
    p2 = Player(2, Piece.Black)
    s = State(p2)
    s.get_board().get_fork(0).set_status(Piece.Red)
    s.get_board().get_fork(19).set_status(Piece.Black)
    s.get_board().get_fork(1).set_status(Piece.Black)
    s.get_board().get_fork(4).set_status(Piece.Black)
    s.get_board().get_fork(6).set_status(Piece.Black)
    print(s)
    game = Bound(p2, p1, s)
    ui = Interface()
    run = True
    while run:
        winner = game.play(ui)
        ui.quit()
        run = False
    print("Winner: " + winner.name)