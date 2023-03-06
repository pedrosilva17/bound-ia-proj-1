#
# Deixar escolher colocação das 4 peças (jogador escolhe espaço que quer deixar livre, espaço livre do j2 colocado do lado oposto)
#

from Game import Bound, State, Board, Player, Piece
from Interface import Interface
import pygame

if __name__ == "__main__":
    outer_length = int(input("Board outer circle size: "))
    p1_name = input("P1 name: ")
    p2_name = input("P2 name: ")
    
    p1_piece = int(input("P1 piece: (1- Red) (2-Black): "))
    while p1_piece != 1 and p1_piece != 2:
        p1_piece = int(input("P1 piece: (1- Red) (2-Black)"))
    p2_piece = Piece(3 - p1_piece)
    
    free_space = int(input(f"P1 piece placement: Choose free space (Red 0-{outer_length - 1}, Black {outer_length * 3}-{outer_length * 4 - 1}): "))
    while ((p1_piece == 1 and free_space not in range(outer_length)) 
    or (p1_piece == 2 and free_space not in range(outer_length * 3, outer_length * 4))):
        free_space = int(input(f"P1 piece placement: Choose free space (Red 0-{outer_length - 1}, Black {outer_length * 3}-{outer_length * 4 - 1}): "))
    p1 = Player(1, Piece(p1_piece), p1_name)
    p2 = Player(2, Piece(p2_piece), p2_name)
    game = Bound(p1, p2, outer_length, free_space)
    run = True
    while run:
        winner = game.play()
        input("Winner: " + winner.name)
        run = False