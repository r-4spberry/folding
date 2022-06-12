# -*- coding: cp1251 -*-
# from sys import platlibdir
import pygame
from random import randrange as rr
from math import sin, cos, tan, atan, pi
from time import sleep
from random import shuffle
from copy import deepcopy
import itertools
from sys import exit
YSCALE = (3 ** .5) / 2

def sign(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def dot(f1, f2):
    return f1.x * f2.x + f1.y * f2.y

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def rotate(self, fi):
        x_ = self.x * cos(fi) - self.y * sin(fi)
        y_ = self.x * sin(fi) + self.y * cos(fi)

        return Point(x_, y_)

    def mirror(self, f):
        v = f.vec()
        a = f.endp.y - f.startp.y
        b = -(f.endp.x - f.startp.x)
        c = -a * f.startp.x - b * f.startp.y
        l = (a * a + b * b) ** .5
        a /= l
        b /= l
        c /= l
        d = a * self.x + b * self.y + c
        x = self.x - 2 * a * d
        y = self.y - 2 * b * d
        return Point(x, y)

    def __str__(self):
        return f"{self.x}, {self.y}"

    def __eq__(self, other):
        if round(self.x,5) == round(other.x,5) and round(self.y,5) == round(other.y,5):
            return True
        return False

    def snap_to_grid(self):
        self.x = round(self.x)
        self.y = round(self.y / YSCALE) * YSCALE


class Fold:
    id_iter = itertools.count()
    def __init__(self, startp, endp, id = None, neighbors=None, startp_=None, endp_=None, state=None, side=None):
        
        self.startp = startp
        self.endp = endp
        if id is None:
            self.id = next(Fold.id_iter)
        else:
            self.id = id
        if neighbors is None:
            self.neighbors = []
        else:
            self.neighbors = neighbors
        if startp_ is None:
            self.startp_ = Point(startp.x, startp.y)
        else:
            self.startp_ = startp_
        if endp_ is None:
            self.endp_ = Point(endp.x, endp.y)
        else:
            self.endp_ = endp_
        if state is None:
            self.state = 0
        else:
            self.state = state
        if side is None:
            self.side = 0
        else:
            self.side = side

    def mirror(self, f):
        self.startp = self.startp.mirror(f)
        self.endp = self.endp.mirror(f)

    def vec(self):  # position of fold's middle
        return Point(self.endp.x - self.startp.x, self.endp.y - self.startp.y)

    def position(self, f):
        d1 = (f.endp.x - self.startp.x) * (self.endp.y - self.startp.y) - (f.endp.y - self.startp.y) * (
                    self.endp.x - self.startp.x)
        d2 = (f.startp.x - self.startp.x) * (self.endp.y - self.startp.y) - (f.startp.y - self.startp.y) * (
                    self.endp.x - self.startp.x)
        return sign(sign(round(d1, 5)) + sign(round(d2, 5)))

    def __str__(self):
        return f"({self.startp}), ({self.endp})"
    
    def __repr__(self):
        return f"Fold with id {self.id}"
    def type(self):
        if round(self.startp.y-self.endp.y,5) == 0:
            t = 'A'
        elif (self.endp.x-self.startp.x)*(self.endp.y - self.startp.y) > 0:
            t = 'B'
        else:
            t = 'C'
        return t
    def __eq__(self, other):
        if self.endp == other.endp and self.startp == other.startp:
            return True
        if self.endp == other.startp and self.startp == other.endp:
            return True
        return False

    def in_array(self, array):
        for other in array:
            if self.id == other.id:
                return True
        return False

class Triangle:
    def __init__(self, n):
        # a = 0, b = 1, c = 2
        self.n = n
        self.folds = [[], [], []]
        self.__create(n)
        self.define_neighbors()

    def __create(self, n):
        # A
        Fold.id_iter = itertools.count()
        for k in range(n + 1):
            self.folds[0].append([])
            y = k * 2
            for x in range(k, 2 * (n + 1) - k, 2):
                self.folds[0][-1].append(Fold(Point(x, y * YSCALE), Point(x + 2, y * YSCALE)))
                if k == 0:
                    self.folds[0][-1][-1].edge = True
                else:
                    self.folds[0][-1][-1].edge = True

        # B
        for k in range(n + 1):
            self.folds[1].append([])
            y = (n + 1) * 2 - k * 2
            for x in range((n + 1) + k, k * 2, -1):
                self.folds[1][-1].append(Fold(Point(x, y * YSCALE), Point(x - 1, (y - 2) * YSCALE)))
                y -= 2
                if k == 0:
                    self.folds[1][-1][-1].edge = True
                else:
                    self.folds[1][-1][-1].edge = True
        # C
        for k in range(n + 1):
            self.folds[2].append([])
            y = 0
            for x in range((n + 1) * 2 - k * 2, (n + 1) - k, -1):
                self.folds[2][-1].append(Fold(Point(x, y * YSCALE), Point(x - 1, (y + 2) * YSCALE)))
                y += 2
                if k == 0:
                    self.folds[2][-1][-1].edge = True
                else:
                    self.folds[2][-1][-1].edge = True
    def draw(self, scr, icolor, x, y, scale, thickness, initial=False):
        W = scr.get_width()
        H = scr.get_width()
        for ind_s, s in enumerate(self.folds):
            for ind_g, g in enumerate(s):
                for i in g:
                    if initial:
                        draw = 1
                        if ind_g != 0:
                            if i.state == -1:
                                color = (255, 0, 0)
                                draw = 1
                            elif i.state == 1:
                                color = (0, 0, 255)
                                draw = 1
                            else:
                                draw = 0
                        else:
                            color = icolor
                        if draw:
                            pygame.draw.line(scr, color,
                                               (x + i.startp_.x * scale, H - i.startp_.y * scale - y),
                                               (x + i.endp_.x * scale, H - i.endp_.y * scale - y), thickness)
                        else:
                            pygame.draw.line(scr, (255, 255, 255),
                                               (x + i.startp_.x * scale, H - i.startp_.y * scale - y),
                                               (x + i.endp_.x * scale, H - i.endp_.y * scale - y), thickness)
                    else:
                        pygame.draw.line(scr, ((ind_s == 0) * 20, (ind_s == 1) * 20, (ind_s == 2) * 20),
                                         (x + i.startp.x * scale, H - i.startp.y * scale - y),
                                         (x + i.endp.x * scale, H - i.endp.y * scale - y), thickness)

    def fold(self, ref, side, mode = 1):
        all = [c for a in self.folds for b in a for c in b]
        refs = [ref]
        connected = []
        line = []
        for fold in all:
            if fold == ref:
                if fold.startp == ref.endp:
                    fold.startp, fold.endp = fold.endp, fold.startp
                if not fold.in_array(refs):
                    refs.append(fold)
            if ref.position(fold) == 0:
                line.append(fold)
        #BFS
        queue = refs

        while len(queue) > 0:
            fold = queue.pop()
            if not fold.in_array(connected):
                connected.append(fold)
            for neighbor in fold.neighbors:
                if (not neighbor.in_array(queue)) and (not neighbor.in_array(connected)) and (ref.position(neighbor) == side):
                    queue.append(neighbor)
        
        for fold in line:
            n = 0
            for c in connected:
                if (not c.in_array(refs)) and (not c.in_array(line)):
                    if fold.in_array(c.neighbors):
                        n += 1
            if n > 1:
                connected.append(fold)
    
        for ax in range(len(self.folds)):
            for ind in range(len(self.folds[ax])):
                for fld in range(len(self.folds[ax][ind])):
                    if self.folds[ax][ind][fld].in_array(connected):
                        p = ref.position(self.folds[ax][ind][fld])
                        if p == side:
                            self.folds[ax][ind][fld].mirror(ref)
                            self.folds[ax][ind][fld].startp.snap_to_grid()
                            self.folds[ax][ind][fld].endp.snap_to_grid()
                        if ind > 0:
                            if p == side:
                                self.folds[ax][ind][fld].side = 1 - self.folds[ax][ind][fld].side
                            if p == 0 and self.folds[ax][ind][fld].state == 0:
                                if self.folds[ax][ind][fld].side:
                                    self.folds[ax][ind][fld].state = -1 if side else 1
                                else:
                                    self.folds[ax][ind][fld].state = 1 if side else -1
        # for ax in range(len(self.folds)):
        #     for ind in range(len(self.folds[ax])):
        #         for fld in range(len(self.folds[ax][ind])):
        #             p = ref.position(self.folds[ax][ind][fld])
        #             if p != side:
        #                 self.folds[ax][ind][fld] = self.folds[ax][ind][fld].mirror(ref)
        #                 self.folds[ax][ind][fld].startp.snap_to_grid()
        #                 self.folds[ax][ind][fld].endp.snap_to_grid()
        #             if ind > 0:
        #                 if p != side:
        #                     self.folds[ax][ind][fld].side = 1 - self.folds[ax][ind][fld].side
        #                 if p == 0 and self.folds[ax][ind][fld].state == 0:
        #                     if self.folds[ax][ind][fld].side:
        #                         self.folds[ax][ind][fld].state = -1 if side else 1
        #                     else:
        #                         self.folds[ax][ind][fld].state = 1 if side else -1
        pass

    def shift(self):
        minx = 1000000000000000000
        miny = 1000000000000000000
        maxx = -1
        maxy = -1
        for i in self.folds:
            for j in i:
                for k in j:
                    minx = min(minx, min(k.startp.x, k.endp.x))
                    maxx = max(maxx, max(k.startp.x, k.endp.x))
                    miny = min(miny, min(k.startp.y, k.endp.y))
                    maxy = max(maxy, max(k.startp.y, k.endp.y))
        if minx < 0:
            for ax in range(len(self.folds)):
                for ind in range(len(self.folds[ax])):
                    for fld in range(len(self.folds[ax][ind])):
                        self.folds[ax][ind][fld].startp.x -= minx
                        self.folds[ax][ind][fld].endp.x -= minx
                        self.folds[ax][ind][fld].startp.snap_to_grid()
                        self.folds[ax][ind][fld].endp.snap_to_grid()
        if maxx > (self.n + 1) * 2 + 0.01:
            for ax in range(len(self.folds)):
                for ind in range(len(self.folds[ax])):
                    for fld in range(len(self.folds[ax][ind])):
                        self.folds[ax][ind][fld].startp.x -= maxx - (self.n + 1) * 2
                        self.folds[ax][ind][fld].endp.x -= maxx - (self.n + 1) * 2
                        self.folds[ax][ind][fld].startp.snap_to_grid()
                        self.folds[ax][ind][fld].endp.snap_to_grid()
        if miny < 0:
            for ax in range(len(self.folds)):
                for ind in range(len(self.folds[ax])):
                    for fld in range(len(self.folds[ax][ind])):
                        self.folds[ax][ind][fld].startp.y -= miny
                        self.folds[ax][ind][fld].endp.y -= miny
                        self.folds[ax][ind][fld].startp.snap_to_grid()
                        self.folds[ax][ind][fld].endp.snap_to_grid()
        if maxy > (self.n + 1) * 2 * YSCALE + 0.5:
            for ax in range(len(self.folds)):
                for ind in range(len(self.folds[ax])):
                    for fld in range(len(self.folds[ax][ind])):
                        self.folds[ax][ind][fld].startp.y -= maxy - (self.n + 1) * 2 * YSCALE
                        self.folds[ax][ind][fld].endp.y -= maxy - (self.n + 1) * 2 * YSCALE
                        self.folds[ax][ind][fld].startp.snap_to_grid()
                        self.folds[ax][ind][fld].endp.snap_to_grid()
        minx = 1000000000000000000
        miny = 1000000000000000000
        maxx = -1
        maxy = -1
        for i in self.folds:
            for j in i:
                for k in j:
                    minx = min(minx, min(k.startp.x, k.endp.x))
                    maxx = max(maxx, max(k.startp.x, k.endp.x))
                    miny = min(miny, min(k.startp.y, k.endp.y))
                    maxy = max(maxy, max(k.startp.y, k.endp.y))
                    
    def define_neighbors(self):
        all = [c for a in self.folds for b in a for c in b]
        for i in range(len(all)):
            for j in range(i+1, len(all)):
                if all[j] not in all[i].neighbors and (all[i].startp == all[j].startp or all[i].endp == all[j].endp or all[i].startp == all[j].endp or all[i].endp == all[j].startp):
                    all[i].neighbors.append(all[j])
                    all[j].neighbors.append(all[i])
                    
    def get(self, id):
        all = [c for a in self.folds for b in a for c in b]
        for fold in all:
            if fold.id == id:
                return fold
        return None
        



def draw_arrow(scr, color, start, end, thickness):
    fi = -2 * pi + atan((end[0] - start[0]) / (end[1] - start[1])) if end[1] - start[1] != 0 else -pi / 2

    if end[1] > start[1]:
        p = Point(0, thickness * 4)
    else:
        p = Point(0, -thickness * 4)

    p = p.rotate(fi)
    p1 = p.rotate(pi / 11)
    p2 = p.rotate(2 * pi - pi / 11)

    fi = pi / 2 - 2 * pi - fi
    if end[0] < start[0] and end[1] > start[1]:
        p = Point(+thickness, 0)
    else:
        p = Point(-thickness, 0)
    p3 = p.rotate(fi)
    pygame.draw.aaline(scr, color, start, (end[0] - p3.x, end[1] - p3.y))
    pygame.draw.polygon(scr, color, (end, (end[0] + p1.x, end[1] - p1.y), (end[0] + p2.x, end[1] - p2.y)))
    # pygame.draw.circle(scr,(255,0,0), end, 1)


def draw_circles(scr, tr, x_shift, y_shift, scale, color, radius, edge = False):
    for i in tr.folds:
        if not edge:
            i = i[1:]
        for j in i:
            for k in j:
                x = (k.startp.x + k.endp.x) / 2 * scale + x_shift
                y = scr.get_height() - ((k.startp.y + k.endp.y) / 2) * scale - y_shift
                pygame.draw.circle(scr, color, (x, y), radius)
                font = pygame.font.SysFont(None, radius*2)
                img = font.render(str(k.id), True, (255,255,255))
                if k.id >= 10:
                    scr.blit(img, (x-radius*(2)**.5/2,y-radius*(2)**.5/2.5))
                else:
                    scr.blit(img, (x-radius*(2)**.5/5,y-radius*(2)**.5/2.5))
                


def check_circle_click(scr, tr, x_shift, y_shift, scale, radius, mx, my, edge = False):
    for i in tr.folds:
        if not edge:
            i = i[1:]
        for j in i:
            for k in j:
                x = (k.startp.x + k.endp.x) / 2 * scale + x_shift
                y = scr.get_height() - ((k.startp.y + k.endp.y) / 2) * scale - y_shift
                if (mx - x) ** 2 + (my - y) ** 2 < radius ** 2:
                    return k, x, y
    return None

class Button():
    def __init__(self, color, x,y,width,height, text=''):
        self.color = color
        self.ogcol = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self,win,outline=None):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4), 2, 3)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height), 2, 3)
        
        if self.text != '':
            font = pygame.font.SysFont('Consolas', 24)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos, ev):
        global STATE
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                self.color = (128,128,128)
            else:
                self.color = self.ogcol
        else:
            self.color = self.ogcol
        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pos[0] > self.x and pos[0] < self.x + self.width:
                    if pos[1] > self.y and pos[1] < self.y + self.height:
                        return True

def edit():
    n = 4
    FPS = 30
    tr = Triangle(n)
    t = [(a, b) for a in range(3) for b in range(1, 5)]
    shuffle(t)
    x_shift = 20
    y_shift = 20
    if n == 2:
        scaling = 75
    if n == 3:
        scaling = 55
    if n == 4:
        scaling = 45
    pygame.init()
    scr = pygame.display.set_mode((500, 500))
    running = True
    
    button = Button((170, 170, 170), 500-140-10, 10, 140, 40, text="Завершить")
    scr.fill((200, 200, 200))
    # Сам треугольник
    tr.draw(scr, (20, 20, 20), x_shift, y_shift, scaling, 3, 1)
    # Миниатюра сгибов
    #tr.draw(scr, (20, 20, 20), 20, scr.get_height() - 100, 10, 3, 1)
    draw_circles(scr, tr, x_shift, y_shift, scaling, (150, 0, 0), 8, False)
    button.draw(scr)
    pygame.display.update()
    
    while running:
        pygame.time.wait(1000//FPS)
        events = pygame.event.get()
        for event in events:
            # Обработка сворачиваний
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                cxy = check_circle_click(scr, tr, x_shift, y_shift, scaling, 8, x, y, False)
                # Если пользователь нажал на круг
                if cxy is not None:
                    c, cx, cy = cxy
                    dragging = True
                    # Выбор стороны сворачивания
##                    while dragging:
##                        for event in pygame.event.get():
##                            if event.type == pygame.MOUSEBUTTONUP:
##                                dragging = False
##                        scr.fill((200, 200, 200))
##                        tr.draw(scr, (20, 20, 20), x_shift, y_shift, scaling, 3, 1)
##                        #tr.draw(scr, (20, 20, 20), 20, scr.get_height() - 100, 10, 3, 1)
##                        x, y = pygame.mouse.get_pos()
##                        draw_circles(scr, tr, x_shift, y_shift, scaling, (150, 0, 0), 8, False)
##                        draw_arrow(scr, (0, 200, 0), (cx, cy), (x, y), 5)
##                        pygame.display.update()
                    # Преобразование координат позиции мыши
                    x, y = pygame.mouse.get_pos()
                    x -= x_shift
                    x /= scaling
                    y = scr.get_height() - y - y_shift
                    y /= scaling

                    # С какой стороны от прямой находится мышь
                    v = Fold(Point(x, y), Point(x, y))
                    p = c.position(v)

                    #tr.fold(c, p)
                    if event.button == 1:
                        if c.state == 0:
                            c.state = 1
                        else:
                            c.state = -c.state
                    elif event.button == 3:
                        c.state = 0
                        
                    tr.shift()
                    scr.fill((200, 200, 200))
                    # Сам треугольник
                    tr.draw(scr, (20, 20, 20), x_shift, y_shift, scaling, 3, 1)
                    # Миниатюра сгибов
                    #tr.draw(scr, (20, 20, 20), 20, scr.get_height() - 100, 10, 3, 1)
                    draw_circles(scr, tr, x_shift, y_shift, scaling, (150, 0, 0), 8, False)
                    button.draw(scr)
                    pygame.display.update()
                    # print("-----------------------------------------")
                    # print(tr.folds[0][-1][0],tr.folds[0][-1][0].startp_,tr.folds[0][-1][0].endp_)
                    # print(tr.folds[1][-1][0],tr.folds[1][-1][0].startp_,tr.folds[1][-1][0].endp_)
                    # print(tr.folds[2][-1][0],tr.folds[2][-1][0].startp_,tr.folds[2][-1][0].endp_)
                    # print("-----------------------------------------")
            if button.isOver(pygame.mouse.get_pos(), events) == True:
                running = False
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
    pygame.quit()
    return tr

def main():
    n = 4
    FPS = 30
    tr = Triangle(n)
    t = [(a, b) for a in range(3) for b in range(1, 5)]
    shuffle(t)
    x_shift = 20
    y_shift = 20
    if n == 2:
        scaling = 75
    if n == 3:
        scaling = 55
    if n == 4:
        scaling = 45
    pygame.init()
    scr = pygame.display.set_mode((500, 500))
    running = True

    scr.fill((200, 200, 200))
    # Сам треугольник
    tr.draw(scr, (20, 20, 20), x_shift, y_shift, scaling, 3, 0)
    # Миниатюра сгибов
    tr.draw(scr, (20, 20, 20), 20, scr.get_height() - 100, 10, 1, 1)
    draw_circles(scr, tr, x_shift, y_shift, scaling, (150, 0, 0), 8, True)
    pygame.display.update()

    while running:
        pygame.time.wait(1000//FPS)
        for event in pygame.event.get():
            # Обработка сворачиваний
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                cxy = check_circle_click(scr, tr, x_shift, y_shift, scaling, 8, x, y, True)
                # Если пользователь нажал на круг
                if cxy is not None:
                    c, cx, cy = cxy
                    dragging = True
                    # Выбор стороны сворачивания
                    while dragging:
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONUP:
                                dragging = False
                        scr.fill((200, 200, 200))
                        tr.draw(scr, (20, 20, 20), x_shift, y_shift, scaling, 3, 0)
                        tr.draw(scr, (20, 20, 20), 20, scr.get_height() - 100, 10, 1, 1)
                        x, y = pygame.mouse.get_pos()
                        draw_circles(scr, tr, x_shift, y_shift, scaling, (150, 0, 0), 8, True)
                        draw_arrow(scr, (0, 200, 0), (cx, cy), (x, y), 5)
                        pygame.display.update()
                        
                    # Преобразование координат позиции мыши
                    x, y = pygame.mouse.get_pos()
                    x -= x_shift
                    x /= scaling
                    y = scr.get_height() - y - y_shift
                    y /= scaling

                    # С какой стороны от прямой находится мышь
                    v = Fold(Point(x, y), Point(x, y))
                    p = c.position(v)

                    tr.fold(c, -p)
                        
                    tr.shift()
                    scr.fill((200, 200, 200))
                    # Сам треугольник
                    tr.draw(scr, (20, 20, 20), x_shift, y_shift, scaling, 3, 0)
                    # Миниатюра сгибов
                    tr.draw(scr, (20, 20, 20), 20, scr.get_height() - 100, 10, 1, 1)
                    draw_circles(scr, tr, x_shift, y_shift, scaling, (150, 0, 0), 8, True)
                    pygame.display.update()
                    # print("-----------------------------------------")
                    # print(tr.folds[0][-1][0],tr.folds[0][-1][0].startp_,tr.folds[0][-1][0].endp_)
                    # print(tr.folds[1][-1][0],tr.folds[1][-1][0].startp_,tr.folds[1][-1][0].endp_)
                    # print(tr.folds[2][-1][0],tr.folds[2][-1][0].startp_,tr.folds[2][-1][0].endp_)
                    # print("-----------------------------------------")
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
    return tr

if __name__ == "__main__":
    main()
