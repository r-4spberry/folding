import folder
from folder import YSCALE
from folder import sign
import math
import copy
import pygame

counter = 0
def angle_of_vector(node):
    x = node.x
    y = node.y
    dist = (x ** 2 + y ** 2) ** 0.5
    if x >= 0 and y > 0:  # 1st quarter
        return math.asin(y / dist)
    elif x < 0 and y >= 0:  # 2nd quarter
        return math.pi - math.asin(y / dist)
    elif x <= 0 and y < 0:  # 3rd quarter
        return math.pi + math.asin(-y / dist)
    elif x > 0 and y <= 0:  # 4th quarter
        return 2 * math.pi - math.asin(-y / dist)


def subjective_direction(subj, obj):
    array = [0, 1, 2, 0, -2, -1]
    array = array[-subj:] + array[:-subj]
    return array[obj]


def mirror_direction(dir, axis):
    array = [[0, 5, 4, 3, 2, 1],
             [2, 1, 0, 5, 4, 3],
             [4, 3, 2, 1, 0, 5],
             [0, 5, 4, 3, 2, 1],
             [2, 1, 0, 5, 4, 3],
             [4, 3, 2, 1, 0, 5]]
    return array[axis][dir]


def pair_in_pairs(pair, pairs):
    for elem in pairs:
        if (pair[0] == elem[0] and pair[1] == elem[1]) or (pair[0] == elem[1] and pair[1] == elem[0]):
            return True
    return False


def pair_equals(pair1, pair2):
    if (pair1[1] == pair2[1] and pair1[0] == pair2[0]) or (pair1[0] == pair2[1] and pair1[1] == pair2[0]):
        return True
    return False


def get_next_node_pair(node_pair, prev_node_pair, fold):
    mir_axis = fold[0].direction(fold[1])
    dir1 = node_pair[0].direction(prev_node_pair[0])
    dir2 = node_pair[1].direction(prev_node_pair[1])
    for i in range(len(fold)):
        if node_pair[0] == fold[i] and node_pair[1] == fold[i] and len(fold) - 1 >= i + 1:
            return [fold[i + 1], fold[i + 1]]
    for _ in range(6):
        dir1 = (dir1 - 1) % 6
        dir2 = mirror_direction(dir1, mir_axis)
        state1, node1 = node_pair[0].get_connection(dir1)
        state2, node2 = node_pair[1].get_connection(dir2)
        if state1 == 2 or state2 == 2:
            return [node1, node2]


class Node:
    def __init__(self, x, y, connected_points=None):
        self.x = x
        self.y = y
        if connected_points is None:
            self.connected_points = []
        else:
            self.connected_points = connected_points

    def dist(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __eq__(self, other):
        if round(self.x) == round(other.x) and round(self.y, 5) == round(other.y, 5):
            return True
        return False

    def snap_to_grid(self):
        self.x = round(self.x)
        self.y = round(self.y / YSCALE) * YSCALE

    def add_connection(self, other, state):
        self.connected_points.append([state, other])

    def change_connection(self, other, state):
        for i in range(len(self.connected_points)):
            if self.connected_points[i][1] == other:
                self.connected_points[i][0] = state
                break

    def change_connection_complete(self, other, state):
        for i in range(len(self.connected_points)):
            if self.connected_points[i][1] == other:
                self.connected_points[i][0] = state
                self.connected_points[i][1] = other
                break

    def __str__(self):
        return f'({self.x},{self.y})'

    def direction(self, other):
        exists = False
        for _, i in self.connected_points:
            if i == other:
                exists = True
                break

        if exists:
            if other.x - self.x > 0 and round(self.y - other.y, 5) == 0:
                return 0
            elif other.x - self.x < 0 and round(self.y - other.y, 5) == 0:
                return 3
            elif other.x - self.x > 0 and other.y - self.y > 0:
                return 1
            elif other.x - self.x < 0 and other.y - self.y > 0:
                return 2
            elif other.x - self.x < 0 and other.y - self.y < 0:
                return 4
            elif other.x - self.x > 0 and other.y - self.y < 0:
                return 5
        else:
            return None

    def get_rightmost_connection(self, next_node):
        array = [4, 5, 0, 1, 2, 3]
        d1 = self.direction(next_node)
        array = array[d1:] + array[:d1]
        min_ind = 6
        return_node = None
        for _, n in next_node.connected_points:
            d2 = next_node.direction(n)
            ind = array.index(d2)
            if ind < min_ind:
                min_ind = ind
                return_node = n
                # print('return node: ',return_node)
        return return_node

    def get_connection(self, dir):
        for state, node in self.connected_points:
            if self.direction(node) == dir:
                return state, node
        return None
        pass

    def is_border(self):
        for state, node in self.connected_points:
            if state == 2:
                return True
        return False

    def get_all_left_folds(self, prev_node, next_node):
        folds = []
        dir = self.direction(next_node)
        dir_back = self.direction(prev_node)
        dir_st = 0
        dir_back_st = (dir_back - dir) % 6
        for state, node in self.connected_points:
            cur_dir = self.direction(node)
            cur_dir_st = (cur_dir - dir) % 6
            if dir_st < cur_dir_st < dir_back_st:
                folds.append(Fold(self, node, state))
        return folds

    def get_all_folds(self):
        folds = []
        for state, node in self.connected_points:
            folds.append(Fold(self, node, state))
        return folds

    def mirror(self, f):
        v = f.vec()
        a = f.dot2.y - f.dot1.y
        b = -(f.dot2.x - f.dot1.x)
        c = -a * f.dot1.x - b * f.dot1.y
        l = (a * a + b * b) ** .5
        a /= l
        b /= l
        c /= l
        d = a * self.x + b * self.y + c
        x = self.x - 2 * a * d
        y = self.y - 2 * b * d
        self.x = x
        self.y = y
        self.snap_to_grid()

    # def mirror(self, f):
    #     v = f.vec()
    #     a = f.endp.y - f.startp.y
    #     b = -(f.endp.x - f.startp.x)
    #     c = -a * f.startp.x - b * f.startp.y
    #     l = (a * a + b * b) ** .5
    #     a /= l
    #     b /= l
    #     c /= l
    #     d = a * self.x + b * self.y + c
    #     x = self.x - 2 * a * d
    #     y = self.y - 2 * b * d
    #     return Point(x, y)
    def position(self, f):

        node = Node(self.x - f.dot1.x, self.y - f.dot1.y)
        node2 = Node(f.dot2.x - f.dot1.x, f.dot2.y - f.dot1.y)
        b = angle_of_vector(node)
        a = angle_of_vector(node2)

        if a > math.pi:
            if b < a and b > a - math.pi:
                return 1
            else:
                return -1
        elif a <= math.pi:
            if b > a and b < a + math.pi:
                return -1
            else:
                return 1

    # def position(self, f):
    #     d1 = (f.endp.x - self.startp.x) * (self.endp.y - self.startp.y) - (f.endp.y - self.startp.y) * (
    #                 self.endp.x - self.startp.x)
    #     d2 = (f.startp.x - self.startp.x) * (self.endp.y - self.startp.y) - (f.startp.y - self.startp.y) * (
    #                 self.endp.x - self.startp.x)
    #     return sign(sign(round(d1, 5)) + sign(round(d2, 5)))
    def switch_connection_state(self):
        for i in range(len(self.connected_points)):
            if self.connected_points[i][0] != 2:
                self.connected_points[i][0] *= -1

    def delete_duplicates(self):
        new_dots = []
        for state, node in self.connected_points:
            is_in = False
            for state1,node1 in new_dots:
                if node == node1:
                    is_in = True
                    break
            if not is_in:
                new_dots.append([state,node])
        self.connected_points = new_dots


class Fold:
    def __init__(self, dot1, dot2, state):
        self.dot1 = dot1
        self.dot2 = dot2
        self.state = state

    def __eq__(self, other):
        if (self.dot1 == other.dot1 and self.dot2 == other.dot2) or (
                self.dot1 == other.dot2 and self.dot2 == other.dot1):
            return True
        return False

    def __str__(self):
        return '(' + str(self.dot1) + ', ' + str(self.dot2) + ')'

    def is_opposite(self, other):
        if self.state == 1 and other.state == -1:
            return True
        if self.state == -1 and other.state == 1:
            return True
        if self.state == 2:
            return True
        if other.state == 2:
            return True
        if self.state == 0 and other.state == 0:
            return True
        return False

    def vec(self):
        return Node(self.dot2.x - self.dot1.x, self.dot2.y - self.dot1.y)


class Graph:
    def __init__(self, folds=[]):
        self.points = []
        for fld in folds:
            dot1 = Node(fld.endp_.x, fld.endp_.y)
            dot2 = Node(fld.startp_.x, fld.startp_.y)
            if self.already_in(dot1):
                for d in self.points:
                    if d == dot1:
                        dot1 = d
                        break
            else:
                self.points.append(dot1)
            if self.already_in(dot2):
                for d in self.points:
                    if d == dot2:
                        dot2 = d
                        break
            else:
                self.points.append(dot2)

            dot1.add_connection(dot2, fld.state)
            dot2.add_connection(dot1, fld.state)
        self.create_borders()

    def already_in(self, p):
        for i in self.points:
            if i == p:
                return True
        return False

    def create_borders(self):
        try:
            cur_node = self.points[0]
            next_node = cur_node
            found = True
            while found:
                found = False
                for _, node in cur_node.connected_points:
                    if cur_node.direction(node) == 0:
                        next_node = node
                        found = True
                        break

                cur_node = next_node
            min_ind = 6
            start_node = cur_node
            for _, node in cur_node.connected_points:
                if min_ind > cur_node.direction(node) > 0:
                    next_node = node
                    min_ind = cur_node.direction(node)
            next_node.change_connection(cur_node, 2)
            cur_node.change_connection(next_node, 2)
            prev_node, cur_node = cur_node, next_node
            while cur_node != start_node:
                next_node = prev_node.get_rightmost_connection(cur_node)
                cur_node.change_connection(next_node, 2)
                next_node.change_connection(cur_node, 2)
                prev_node, cur_node = cur_node, next_node
        except:
            pass

    def get_probable_folds(self):
        array_forward = []
        array_backward = []
        for n in self.points:
            for st, cn in n.connected_points:
                if st == -1:
                    add = True
                    for elem in array_forward:
                        if (elem[0] == n and elem[1] == cn) or (elem[1] == n and elem[0] == cn):
                            add = False
                            break
                    if add:
                        array_forward.append([n, cn])

                elif st == 1:
                    add = True
                    for elem in array_backward:
                        if (elem[0] == n and elem[1] == cn) or (elem[1] == n and elem[0] == cn):
                            add = False
                            break
                    if add:
                        array_backward.append([n, cn])

        probable_folds = []

        for array in [array_forward, array_backward]:
            found_line = True
            long_lines = []
            long_line = []
            while found_line:
                found_line = False
                if len(long_line) == 0:
                    if len(array) != 0:
                        long_line.append(array[0][0])
                        long_line.append(array[0][1])
                        array.pop(0)
                        found_line = True
                else:
                    for i in range(len(array)):
                        if array[i][0] == long_line[-1] and array[i][0].direction(array[i][1]) == long_line[
                            -2].direction(long_line[-1]):
                            found_line = True
                            long_line.append(array[i][1])
                            array.pop(i)
                            break
                        elif array[i][0] == long_line[0] and array[i][0].direction(array[i][1]) == long_line[
                            1].direction(long_line[0]):
                            found_line = True
                            long_line = [array[i][1]] + long_line
                            array.pop(i)
                            break
                        elif array[i][1] == long_line[-1] and array[i][1].direction(array[i][0]) == long_line[
                            -2].direction(long_line[-1]):
                            found_line = True
                            long_line.append(array[i][0])
                            array.pop(i)
                            break
                        elif array[i][1] == long_line[0] and array[i][1].direction(array[i][0]) == long_line[
                            1].direction(long_line[0]):
                            found_line = True
                            long_line = [array[i][0]] + long_line
                            array.pop(i)
                            break
                    if not found_line:
                        found_line = True
                        long_lines.append(long_line)
                        long_line = []

            for line in long_lines:
                for sp in range(0, len(line)):
                    for ep in range(sp + 2, len(line) + 1):
                        probable_folds.append(line[sp:ep:1])
        return probable_folds

    def get_possible_folds(self):
        possible_folds = []
        probable_folds = self.get_probable_folds()
        for fold in probable_folds:
            # print(fold[0])
            is_possible1 = False
            is_possible2 = False
            is_possible3 = True
            for _, node in fold[0].connected_points:
                if is_possible1:
                    break
                rotation = 0
                prev_node = fold[0]
                # print('fold: ', fold[0])
                # print('node:', node)
                while node != fold[0]:
                    # print('fold: ',fold[0])
                    # print('node:', node)
                    next_node = prev_node.get_rightmost_connection(node)
                    rotation += subjective_direction(prev_node.direction(node), node.direction(next_node))
                    prev_node, node = node, next_node
                if rotation > 0:
                    is_possible1 = True
                # print('ROTATION: ', rotation, end=' ')

            for _, node in fold[-1].connected_points:
                if is_possible2:
                    break
                rotation = 0
                prev_node = fold[-1]
                while node != fold[-1]:
                    next_node = prev_node.get_rightmost_connection(node)
                    rotation += subjective_direction(prev_node.direction(node), node.direction(next_node))
                    prev_node, node = node, next_node
                if rotation > 0:
                    is_possible2 = True
                # print(rotation)
            for i in range(1,len(fold)-1):
                if is_possible3:
                    for _, node in fold[i].connected_points:
                        if  not  is_possible3:
                            break
                        rotation = 0
                        prev_node = fold[i]
                        while node != fold[i]:
                            next_node = prev_node.get_rightmost_connection(node)
                            rotation += subjective_direction(prev_node.direction(node), node.direction(next_node))
                            prev_node, node = node, next_node
                        if rotation > 0:
                            is_possible3 = False

                        # print(rotation)
            if is_possible1 and is_possible2 and is_possible3:
                possible_folds.append(fold)
        return possible_folds

    def get_intersection_points(self,fold):
        mir_axis = fold[0].direction(fold[1])
        fold_pairs = []
        node_pairs = []
        cur_node_pairs = []
        next_node_pairs = []
        node_pairs.append([fold[0], fold[0]])
        node_pairs.append([fold[1], fold[1]])
        prev_node_pair = [fold[0], fold[0]]
        cur_node_pair = [fold[1], fold[1]]

        while not pair_equals(cur_node_pair, [fold[0], fold[0]]):

            next_node_pair = get_next_node_pair(cur_node_pair, prev_node_pair, fold)
            if not pair_in_pairs(next_node_pair, node_pairs):
                node_pairs.append(next_node_pair)
            left_folds = cur_node_pair[0].get_all_left_folds(prev_node_pair[0], next_node_pair[0])
            for left_fold in left_folds:
                left_dir = left_fold.dot1.direction(left_fold.dot2)
                right_dir = mirror_direction(left_dir, mir_axis)
                next_right = cur_node_pair[1].get_connection(right_dir)
                right_fold = Fold(cur_node_pair[1], next_right[1], next_right[0])
                if not pair_in_pairs([left_fold, right_fold], fold_pairs):
                    fold_pairs.append([left_fold, right_fold])
                if not pair_in_pairs([left_fold.dot2, right_fold.dot2], node_pairs):
                    cur_node_pairs.append([left_fold.dot2, right_fold.dot2])
            prev_node_pair, cur_node_pair = cur_node_pair, next_node_pair
        found = True
        while found:
            found = False
            next_node_pairs = []
            for cur_node_pair in cur_node_pairs:
                for f in cur_node_pair[0].get_all_folds():
                    dir1 = f.dot1.direction(f.dot2)
                    dir2 = mirror_direction(dir1, mir_axis)
                    _ = cur_node_pair[1].get_connection(dir2)
                    if _ is not None:
                        fold_pair = [f, Fold(cur_node_pair[1], _[1], _[0])]
                        if not pair_in_pairs(fold_pair, fold_pairs) and fold_pair[0].state != 2 and fold_pair[
                            1].state != 2:
                            fold_pairs.append(fold_pair)
                        next_node_pair = [fold_pair[0].dot2, fold_pair[1].dot2]
                        if (not pair_in_pairs(next_node_pair, next_node_pairs)) and (
                                not pair_in_pairs(next_node_pair, node_pairs)):
                            next_node_pairs.append(next_node_pair)
            if len(next_node_pairs) != 0:
                found = True
            for cur_node_pair in cur_node_pairs:
                if not pair_in_pairs(cur_node_pair, node_pairs):
                    node_pairs.append(cur_node_pair)
                # node_pairs = node_pairs+cur_node_pairs
            cur_node_pairs = next_node_pairs
        return node_pairs, fold_pairs

    def get_all_points_to_the_left(self,fold):
        nodes = []
        prob_next_nodes = []
        cur_node = fold[1]
        prev_node = fold[0]
        while fold[0] != cur_node:
            is_in_fold = False
            for i in range(len(fold)):
                if fold[i] == cur_node:
                    is_in_fold = True
                    break
            if is_in_fold:
                if i < len(fold)-1:
                    next_node = fold[i+1] # prev_node.get_rightmost_connection(cur_node)
                    folds = cur_node.get_all_left_folds(prev_node, next_node)
                else:
                    back_dir = (cur_node.direction(prev_node)-1)%6
                    while True:
                        a = cur_node.get_connection(back_dir)
                        if a is not None:
                            state,n = a
                            if state == 2:
                                next_node = n
                                break
                        back_dir = (back_dir-1)%6

                    folds = cur_node.get_all_left_folds(prev_node, next_node)
            else:
                next_node = prev_node.get_rightmost_connection(cur_node)
                folds = cur_node.get_all_left_folds(prev_node, next_node)
            if cur_node not in nodes:
                nodes.append(cur_node)
            if next_node not in nodes:
                nodes.append(next_node)
            for f in folds:
                if f.dot2 not in prob_next_nodes:
                    prob_next_nodes.append(f.dot2)
            prev_node,cur_node = cur_node,next_node
        next_nodes = []
        for node in prob_next_nodes:
            if node not in nodes:
                next_nodes.append(node)
        while len(next_nodes) != 0:
            nodes = nodes + next_nodes
            cur_nodes = next_nodes
            next_nodes = []
            for node in cur_nodes:
                for _, con_node in node.connected_points:
                    if (con_node not in nodes) and (con_node not in next_nodes):
                        next_nodes.append(con_node)
        return nodes










    def get_legit_folds(self):
        possible_folds = self.get_possible_folds()
        legit_folds = []
        for fold in possible_folds:
            node_pairs, fold_pairs = self.get_intersection_points(fold)

            is_legit = True
            for fold_pair in fold_pairs:
                if not (fold_pair[0].is_opposite(fold_pair[1]) and fold_pair[1].is_opposite(fold_pair[0])):
                    is_legit = False
                    break
            if is_legit:
                legit_folds.append(fold)

            # for node_pair in node_pairs:
            #     print('NODE PAIR: ',[str(i) for i in node_pair])
            # for fold_pair in fold_pairs:
            #     print('FOLD PAIR: ', [str(i) for i in fold_pair])

            # while not pair_equals(cur_dot_pair,[fold[0], fold[0]])
        return legit_folds

    # def copy(self):
    #     copy_graph = Graph()
    #     for init_node in self.points:
    #         copy_node = Node(init_node.x, init_node.y)
    #         exists = False
    #         for n in copy_graph.points:
    #             if n == copy_node:
    #                 copy_node = n
    #                 exists = True
    #                 break
    #         if not exists:
    #             copy_graph.points.append(copy_node)
    #         for state, con_node in init_node.connected_points:
    #             copy_con_node = Node(con_node.x, con_node.y)
    #             exists = False
    #             for n in copy_graph.points:
    #                 if n == copy_con_node:
    #                     copy_con_node = n
    #                     exists = True
    #                     break
    #             if not exists:
    #                 copy_graph.points.append(copy_con_node)
    #             copy_node.add_connection(copy_con_node, state)
    #     return copy_graph

    def fold(self,a_fold):
        global counter
        new_fold = []
        for n in a_fold:
            for p in self.points:
                if p == n:
                    new_fold.append(p)
                    break
        fold = new_fold
        # print("----------------------------------------")
        # print("BEGIN POINTS: ")
        # for p in self.points:
        #     print(p)
        # print("FOLD: ")
        # for p in fold:
        #     print(p)
        mirror_fold = Fold(fold[0], fold[1], 0)
        right_points = self.get_all_points_to_the_left(fold[::-1])
        left_points = []
        for p in self.points:
            if p not in right_points:
                left_points.append(p)

        if len(right_points) > len(left_points):
            right_points, left_points = left_points,right_points

        for p in right_points:
            p.mirror(mirror_fold)
            p.switch_connection_state()
        pairs = []
        singles = []
        while len(right_points) != 0:
            is_pair = False
            r = right_points.pop(0)
            for i in range(len(left_points)):
                if left_points[i] == r:
                    is_pair = True
                    l = left_points.pop(i)
                    break
            if is_pair:
                pairs.append([l,r])
            else:
                singles.append(r)

        for i in left_points:
            singles.append(i)
        # print("---------------------------------------------")
        # print("POINTS:")
        # for p in self.points:
        #     print(p)
        # print("SINGLES:")
        # for p in singles:
        #     print(p)
        # print("PAIRS:")
        # for p in pairs:
        #     print(p[0],p[1])
        # print("---------------------------------------------")


        for n in fold:
            n.delete_duplicates()
        for p in pairs:
            for dir in range(6):
                l_c = p[0].get_connection(dir)
                if l_c is not None:
                    left_state, left_con = l_c
                r_c = p[1].get_connection(dir)
                if r_c is not None:
                    right_state, right_con = r_c
                if (l_c is not None) and (r_c is not None):
                    state_real = min(left_state,right_state)
                    if state_real == 2:
                        state_real = 0
                    con_real = left_con
                    p[0].change_connection_complete(con_real,state_real)
                    con_real.change_connection_complete(p[0],state_real)
                elif (l_c is not None) and (r_c is None):
                    state_real = left_state
                    con_real = left_con
                    p[0].change_connection_complete(con_real, state_real)
                    con_real.change_connection_complete(p[0], state_real)
                elif (l_c is None) and (r_c is not None):
                    state_real = right_state
                    con_real = right_con
                    p[0].add_connection(con_real,state_real)
                    con_real.change_connection_complete(p[0],state_real)
        final_array = []
        for p in pairs:
            if p[0] not in final_array:
                final_array.append(p[0])
        for n in singles:
            if n not in final_array:
                final_array.append(n)
        for n in fold:
            if n not in final_array:
                final_array.append(n)
        self.points = final_array
        self.create_borders()
        # print('AAAAAAAAAAAAAAAAAAAAA')
        counter+=1
        return self






    # def fold(self, fold):
    #     mirror_fold = Fold(fold[0], fold[1], 0)
    #     new_fold = []
    #     for n in fold:
    #         for p in self.points:
    #             if p == n:
    #                 new_fold.append(p)
    #                 break
    #     fold = new_fold
    #     left_points = []
    #     right_points = []
    #     right_points = self.get_all_points_to_the_left(fold[::-1])
    #     for node in self.points:
    #         if node not in right_points:
    #             left_points.append(node)
    #     # print("LEFT POINTS:")
    #     # for point in left_points:
    #     #     print(point)
    #     # print("RIGHT POINTS:")
    #     # for point in right_points:
    #     #     print(point)
    #     for point in right_points:
    #         point.mirror(mirror_fold)
    #     for point in right_points:
    #         if point not in fold:
    #             point.switch_connection_state()
    #
    #     pairs = []
    #     not_pairs = []
    #
    #     while len(left_points) != 0:
    #         pair = [left_points.pop(0)]
    #         for i in range(len(right_points)):
    #             if right_points[i] == pair[0]:
    #                 pair.append(right_points.pop(i))
    #                 break
    #         if len(pair) == 2:
    #             pairs.append(pair)
    #         else:
    #             not_pairs.append(pair[0])
    #     for node in right_points:
    #         not_pairs.append(node)
    #     print('PAIRS:')
    #     for pair in pairs:
    #         print([str(i) for i in pair])
    #     print('NOT PAIRS:')
    #     for node in not_pairs:
    #         print(str(node))
    #     for pair in pairs:
    #         node = pair[0]
    #         for dir in range(6):
    #             conn_real = pair[0].get_connection(dir)
    #             conn_fake = pair[1].get_connection(dir)
    #             connected = False
    #             if conn_real is not None:
    #                 connected = True
    #                 state_real, conn_real = conn_real
    #                 node.change_connection_complete(conn_real, state_real)
    #                 conn_real.change_connection_complete(node, state_real)
    #             if conn_fake is not None:
    #                 state_fake, conn_fake = conn_fake
    #                 if connected:
    #                     if state_real == 2:
    #                         node.change_connection_complete(conn_real, state_fake)
    #                         conn_real.change_connection_complete(node, state_fake)
    #                 else:
    #                     node.add_connection(conn_fake, state_fake)
    #                     conn_fake.change_connection_complete(node, state_fake)
    #     for fold_node in fold:
    #         for pair in pairs:
    #             for state, con_node in fold_node.connected_points:
    #                 if con_node == pair[0]:
    #                     arr = []
    #                     state_arr = []
    #                     for i in range(len(fold_node.connected_points)):
    #                         if fold_node.connected_points[i][1] == pair[0]:
    #                             arr.append(i)
    #                             # state_arr.append(fold_node.connected_points[i][0])
    #                             for state, k in pair[0].connected_points:
    #                                 if k == fold_node:
    #                                     state_arr.append(state)
    #                                     break
    #                     for i in arr[::-1]:
    #                         fold_node.connected_points.pop(i)
    #                     fold_node.add_connection(pair[0], min(state_arr))
    #                     pair[0].change_connection_complete(fold_node, min(state_arr))
    #                     break
    #     final_array = []
    #     for fold_node in fold:
    #         if fold_node not in final_array:
    #             final_array.append(fold_node)
    #     for pair in pairs:
    #         if pair[0] not in final_array:
    #             final_array.append(pair[0])
    #     for node in not_pairs:
    #         if node not in final_array:
    #             final_array.append(node)
    #     self.points = final_array
    #     self.create_borders()
    #     return self

    def draw(self, scr :pygame.display, x=0, y=0, scaling=1):
        x_mid = sum([self.points[i].x for i in range(len(self.points))])/len(self.points)
        y_mid = sum([self.points[i].y for i in range(len(self.points))])/len(self.points)
        WIDTH = scr.get_width()
        HEIGHT = scr.get_width()
        for node in self.points:
            for state, con_node in node.connected_points:
                if state == 2:
                    color = (0, 128, 0)
                elif state == -1:
                    color = (128, 0, 0)
                elif state == 1:
                    color = (0, 0, 128)
                else:
                    color = (255, 255, 255)
                print(node.x*scaling + x_mid,WIDTH-node.y*scaling-HEIGHT + 500)
                print(con_node.x*scaling + x_mid,WIDTH-con_node.y*scaling-HEIGHT + 500)
                pygame.draw.line(scr,color,((node.x+x)*scaling+300,WIDTH-(node.y+y)*scaling-HEIGHT + 500),(300+(con_node.x+x)*scaling,WIDTH-(con_node.y+y)*scaling-HEIGHT + 500),5)


# def recursive_fold(elem, array):
#     legit_folds = elem.get_legit_folds()
#     if len(legit_folds) == 0:
#         return elem, []
#     else:
#         for i in range(len(legit_folds)):
#             if type(i) != list:
#                 copy_graph = copy.deepcopy(elem)
#                 copy_graph.fold(legit_folds[i])
#                 array.append(recursive_fold(copy_graph,[]))
#     return elem, array
def recursive_fold(array):
    for i in range(len(array)):
        if type(array[i]) != list:
            legit_folds = array[i].get_legit_folds()
            for f in legit_folds:
                c_elem = copy.deepcopy(array[i])
                c_elem.fold(f)
                array[i+1].append(recursive_fold([c_elem,[]]))
    return array


def recursive_ret(array):


    yield array[0]
    for a in array[1]:
        k = recursive_ret(a)
        for i in k:
            yield i #recursive_ret(a).__next__()
        yield array[0]
    #yield array[0]



def main():
    FPS = 30
    tr = folder.edit()
    array = []
    for axis in tr.folds:
        for ind in axis:
            for fld in ind:
                array.append(fld)
    g = Graph(array)
    # copy_graph = copy.deepcopy(g)
    # for dot in g.points:
    #     for s, i in dot.connected_points:
    #         if s == 2:
    #             print("BORDER: ", [str(dot), str(i)])
    #
    # probable_folds = g.get_probable_folds()
    # print('PROBABLE FOLDS:')
    # for fold in probable_folds:
    #     print([str(i) for i in fold])
    # possible_folds = g.get_possible_folds()
    # print('POSSIBLE FOLDS:')
    # for fold in possible_folds:
    #     print([str(i) for i in fold])
    # legit_folds = copy_graph.get_legit_folds()
    # print('LEGIT FOLDS:')
    # for fold in legit_folds:
    #     print([str(i) for i in fold])
    #
    # print('CONNECTIONS IN COPY:')
    # for node in copy_graph.points:
    #     for state, con_node in node.connected_points:
    #         if state == -1 or state == 1:
    #             print(node, con_node)
    # copy_graph.fold(legit_folds[0])
    # print("BORDERS AFTER FOLD:")
    # for p in copy_graph.points:
    #     for st, cp in p.connected_points:
    #         if st == 2:
    #             print(Fold(p,cp,st))
    # print("LEFT AFTER FOLD:")
    # for p in copy_graph.points:
    #     for st, cp in p.connected_points:
    #         if st == 1:
    #             print(Fold(p, cp, st))
    # print("RIGHT AFTER FOLD:")
    # for p in copy_graph.points:
    #     for st, cp in p.connected_points:
    #         if st == -1:
    #             print(Fold(p, cp, st))
    # legit_folds = copy_graph.get_legit_folds()
    # print("FOLD: ",[str(i) for i in legit_folds[0]])
    # copy_graph.fold(legit_folds[0])
    # print("BORDERS AFTER FOLD:")
    # for p in copy_graph.points:
    #     for st, cp in p.connected_points:
    #         if st == 2:
    #             print(Fold(p, cp, st))
    # print("LEFT AFTER FOLD:")
    # for p in copy_graph.points:
    #     for st, cp in p.connected_points:
    #         if st == 1:
    #             print(Fold(p, cp, st))
    # print("RIGHT AFTER FOLD:")
    # for p in copy_graph.points:
    #     for st, cp in p.connected_points:
    #         if st == -1:
    #             print(Fold(p, cp, st))
    #
    # print("BORDERS BEFORE FOLD:")
    # for p in g.points:
    #     for st, cp in p.connected_points:
    #         if st == 2:
    #             print(Fold(p, cp, st))
    # print("LEFT BEFORE FOLD:")
    # for p in g.points:
    #     for st, cp in p.connected_points:
    #         if st == 1:
    #             print(Fold(p, cp, st))
    # print("RIGHT BEFORE FOLD:")
    # for p in g.points:
    #     for st, cp in p.connected_points:
    #         if st == -1:
    #             print(Fold(p, cp, st))
    legit_folds = g.get_legit_folds()
    # print("TO THE LEFT:")
    # for i in g.get_all_points_to_the_left(legit_folds[0]):
    #     print(str(i))
    # print("TO THE RIGHT:")
    # for i in g.get_all_points_to_the_left(legit_folds[0][::-1]):
    #     print(str(i))
    #raise Exception

    array = recursive_fold([g,[]])
    print(array)
    pygame.init()
    scr = pygame.display.set_mode((700, 700))
    running = True

    scr.fill((200, 200, 200))
    button = folder.Button((170, 170, 170), 0, 10, 700, 40, text="Нажмите SPACE чтобы перейти на следующую итерацию.")
    button.draw(scr)
    pygame.display.update()
    drawer = recursive_ret(array)
    elem = drawer.__next__()
    # print("TYPE: ",type(elem))
    scr.fill((200, 200, 200))
    button.draw(scr)
    elem.draw(scr=scr, x=-4, y=0, scaling=40)
    pygame.display.update()
    while running:
        pygame.time.wait(1000//FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    try:
                        elem = drawer.__next__()
                        # print("TYPE: ",type(elem))
                        scr.fill((200, 200, 200))
                        button.draw(scr)
                        elem.draw(scr=scr, x=-4, y=0, scaling=40)
                        pygame.display.update()
                    except StopIteration:
                        scr.fill((200, 200, 200))
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()


if __name__ == "__main__":
    main()
