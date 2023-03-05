import pygame as pg
import math
from constants import COLOR_DICT

class Interface:

    def __init__(self):            
        self.DEFAULT_WIDTH = 600
        self.DEFAULT_HEIGHT = 550
        self.CENTER_X = self.DEFAULT_WIDTH/2
        self.CENTER_Y = self.DEFAULT_HEIGHT/2
        self.OUTER_RADIUS = self.DEFAULT_HEIGHT-320
        self.OUTER_MIDDLE_RADIUS = self.OUTER_RADIUS - 70
        self.INNER_MIDDLE_RADIUS = self.OUTER_MIDDLE_RADIUS - 70
        self.INNER_RADIUS =  self.INNER_MIDDLE_RADIUS - 70

    def xy_calc(self, layer, angle, radius, offset=0):
        temp = []
        for idx,point in enumerate(layer):
            x = radius * math.cos(angle*idx+offset) + self.CENTER_X
            y = radius * math.sin(angle*idx+offset) + self.CENTER_Y
            temp.append((point, (int(x),int(y))))
        return temp


    def vertex_positioning(self, board):
        ring_size = int(len(board.get_forks())/4)
        angle = (2*math.pi)/ring_size
        angle_offset = ring_size/2-0.5
        vertex_list = [e.get_index() for (f,e) in board.get_forks().items()]
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

        print(outer_middle, inner_middle)

        outer = self.xy_calc(outer, angle, self.OUTER_RADIUS, angle)
        outer_middle = self.xy_calc(outer_middle, angle, self.OUTER_MIDDLE_RADIUS)
        inner_middle = self.xy_calc(inner_middle, angle, self.INNER_MIDDLE_RADIUS, angle/2)
        inner = self.xy_calc(inner, angle, self.INNER_RADIUS, -angle/2)
        layers = outer + outer_middle + inner_middle + inner
        layers.sort(key=lambda x: x[0])
        return layers


    def render(self, board):
        vertex_list = self.vertex_positioning(board)
        print(vertex_list)
        pg.init()
        screen = pg.display.set_mode((self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT))
        screen.fill((69, 227, 255))
        for (p,e) in board.get_paths().items():
            for edge in e:
                pg.draw.line(screen, (255,255,255), vertex_list[p.get_index()][1], vertex_list[edge.get_index()][1])
        for (v, pos) in vertex_list:
            pg.draw.circle(screen, COLOR_DICT[board.get_fork(v).get_status().name], pos, 5)
        

        pg.display.flip()       

    def quit(self):
        pg.quit()
