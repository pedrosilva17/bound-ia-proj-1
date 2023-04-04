from constants import COLOR_DICT
import math
import pygame as pg
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'


class Interface:
    """Class representing the graphical interface for the game.
    """

    def __init__(self):
        """Initialize the parameters for the pygame window and board being drawn.
        """
        self.DEFAULT_WIDTH = 900
        self.DEFAULT_HEIGHT = 800
        self.CENTER_X = self.DEFAULT_WIDTH/2
        self.CENTER_Y = self.DEFAULT_HEIGHT/2
        self.OUTER_RADIUS = self.DEFAULT_HEIGHT-520
        self.OUTER_MIDDLE_RADIUS = self.OUTER_RADIUS - 70
        self.INNER_MIDDLE_RADIUS = self.OUTER_MIDDLE_RADIUS - 70
        self.INNER_RADIUS = self.INNER_MIDDLE_RADIUS - 70

    def ui_init(self):
        """Initialize and display the pygame window.
        """
        pg.init()
        self.bg_image = pg.image.load("./assets/background.jpg")
        self.screen = pg.display.set_mode(
            (self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT))
        self.screen.blit(self.bg_image, (100, 0))
        pg.display.flip()

    def xy_calc(self, layer: dict, angle: float, radius: int, offset: int = 0) -> list:
        """Calculate the screen coordinates for each one of the board's forks.

        Args:
            layer (dict): The dictionary of index keys pointing to the respective forks.
            angle (float): The angle inside the circle between two forks.
            radius (int): The radius of the circle connecting the forks.
            offset (int, optional): Additional spacing between forks. Defaults to 0.

        Returns:
            list: A list of tuples composed of forks and their respective screen coordinates.
        """
        temp = []
        for idx, point in enumerate(layer):
            x = radius * math.cos(angle*idx+offset) + self.CENTER_X
            y = radius * math.sin(angle*idx+offset) + self.CENTER_Y
            temp.append((point, (int(x), int(y))))
        return temp

    def vertex_positioning(self, board) -> list:
        """Calculate the screen positioning of each vertex (fork) of a given board.

        Args:
            board (Board): The board to be displayed.

        Returns:
            list: A list of tuples composed of forks and their respective screen coordinates.
        """
        ring_size = int(len(board.forks)/4)
        angle = (2*math.pi)/ring_size
        vertex_list = [e.index for (f, e) in board.forks.items()]
        outer = vertex_list[0:ring_size]
        del vertex_list[0:ring_size]
        inner = vertex_list[-ring_size:]
        del vertex_list[-ring_size:]
        for pos in vertex_list:
            if ring_size % 2 == 0:
                outer_middle = [x for x in vertex_list if x % 2 == 0]
                inner_middle = [x for x in vertex_list if x % 2 != 0]
            else:
                outer_middle = [x for x in vertex_list if x % 2 != 0]
                inner_middle = [x for x in vertex_list if x % 2 == 0]

        outer = self.xy_calc(outer, angle, self.OUTER_RADIUS, angle)
        outer_middle = self.xy_calc(
            outer_middle, angle, self.OUTER_MIDDLE_RADIUS)
        inner_middle = self.xy_calc(
            inner_middle, angle, self.INNER_MIDDLE_RADIUS, angle/2)
        inner = self.xy_calc(inner, angle, self.INNER_RADIUS, -angle/2)
        layers = outer + outer_middle + inner_middle + inner
        layers.sort(key=lambda x: x[0])
        return layers

    def render(self, board):
        """Render the display.

        Args:
            board (Board): The board to be displayed.
        """
        vertex_list = self.vertex_positioning(board)
        self.screen.blit(self.bg_image, (0, 0))
        index = 0
        font = pg.font.SysFont('arial', 9)
        for (p, e) in board.paths.items():
            for edge in e:
                pg.draw.line(
                    self.screen, (255, 255, 255),
                    vertex_list[p.index][1],
                    vertex_list[edge.index][1],
                    2)
        for (v, pos) in vertex_list:
            if board.get_fork(v).status.name == "Empty":
                pg.draw.circle(
                    self.screen, COLOR_DICT[board.get_fork(v).status.name],
                    pos, 10)
            else:
                pg.draw.circle(
                    self.screen, COLOR_DICT[board.get_fork(v).status.name],
                    pos, 15)
            if board.get_fork(v).status.name != "Empty":
                textColor = (255, 255, 255)
            else:
                textColor = (0, 0, 0)
            text = font.render(str(index), True, textColor)
            textRect = text.get_rect()
            textRect.center = pos
            self.screen.blit(text, textRect)
            index += 1
        pg.display.flip()

    def quit(self):
        """Close the graphical interface.
        """
        pg.quit()
