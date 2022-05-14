import folder
from folder import YSCALE


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

def get_next_node_pair(node_pair,prev_node_pair,fold):

    mir_axis = fold[0].direction(fold[1])
    dir1 = node_pair[0].direction(prev_node_pair[0])
    dir2 = node_pair[1].direction(prev_node_pair[1])
    for i in range(len(fold)):
        if node_pair[0] == fold[i] and node_pair[1] == fold[i] and len(fold)-1 >= i+1:
            return [fold[i+1],fold[i+1]]
    for _ in range(6):
        dir1 = (dir1-1)%6
        dir2 = mirror_direction(dir1,mir_axis)
        state1, node1 = node_pair[0].get_connection(dir1)
        state2, node2 = node_pair[1].get_connection(dir2)
        if state1 == 2 or state2 == 2:
            return [node1,node2]










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

    def get_rightmost_connection(self, other):
        array = [4, 5, 0, 1, 2, 3]
        d1 = self.direction(other)
        array = array[d1:] + array[:d1]
        min_ind = 6
        return_node = None
        for _, n in other.connected_points:
            d2 = other.direction(n)
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
        dir_back_st = (dir_back - dir)%6
        for state, node in self.connected_points:
            cur_dir = self.direction(node)
            cur_dir_st = (cur_dir - dir)%6
            if dir_st < cur_dir_st < dir_back_st:
                folds.append(Fold(self, node, state))
        return folds

    def get_all_pairs(self):
        pairs = []
        for node in self.connected_points:
            pairs.append([self, node])
        return pairs

class Fold:
    def __init__(self,dot1,dot2,state):
        self.dot1 = dot1
        self.dot2 = dot2
        self.state = state
    def __eq__(self, other):
        if (self.dot1 == other.dot1 and self.dot2 == other.dot2) or (self.dot1 == other.dot2 and self.dot2 == other.dot1):
            return True
        return False
    def __str__(self):
        return '(' + str(self.dot1) + ', ' + str(self.dot2) + ')'

class Graph:
    def __init__(self, folds):
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
                print('ROTATION: ', rotation, end=' ')

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
                print(rotation)
            if is_possible1 and is_possible2:
                possible_folds.append(fold)
        return possible_folds

    # def get_nearest_pairs(self, fold):
    #     pairs = []
    #     mirror_dir = fold[0].direction(fold[1])
    #     for line_node in fold:
    #
    #     return pairs

    def get_legit_folds(self):
        possible_folds = self.get_possible_folds()
        for fold in possible_folds:
            mir_axis = fold[0].direction(fold[1])
            fold_pairs = []
            node_pairs = []
            cur_node_pairs = []
            next_node_pairs = []
            node_pairs.append([fold[0], fold[0]])
            node_pairs.append([fold[1], fold[1]])
            prev_node_pair = [fold[0], fold[0]]
            cur_node_pair = [fold[1], fold[1]]

            while not pair_equals(cur_node_pair,[fold[0], fold[0]]):

                next_node_pair = get_next_node_pair(cur_node_pair,prev_node_pair,fold)
                if not pair_equals(next_node_pair,[fold[0], fold[0]]):
                    node_pairs.append(next_node_pair)
                left_folds = cur_node_pair[0].get_all_left_folds(prev_node_pair[0],next_node_pair[0])
                for left_fold in left_folds:
                    left_dir = left_fold.dot1.direction(left_fold.dot2)
                    right_dir = mirror_direction(left_dir,mir_axis)
                    next_right = cur_node_pair[1].get_connection(right_dir)
                    right_fold = Fold(cur_node_pair[1],next_right[1],next_right[0])
                    if not pair_in_pairs([left_fold,right_fold],fold_pairs):
                        fold_pairs.append([left_fold,right_fold])
                    if not pair_in_pairs([left_fold.dot2,right_fold.dot2], cur_node_pairs):
                        cur_node_pairs.append([left_fold.dot2,right_fold.dot2])
                    if not pair_in_pairs([left_fold.dot2,right_fold.dot2], node_pairs):
                        node_pairs.append([left_fold.dot2,right_fold.dot2])
                prev_node_pair,cur_node_pair = cur_node_pair,next_node_pair
            for node_pair in node_pairs:
                print('NODE PAIR: ',[str(i) for i in node_pair])
            for fold_pair in fold_pairs:
                print('FOLD PAIR: ', [str(i) for i in fold_pair])


            # while not pair_equals(cur_dot_pair,[fold[0], fold[0]])




def main():
    tr = folder.main()
    array = []
    for axis in tr.folds:
        for ind in axis:
            for fld in ind:
                array.append(fld)
    g = Graph(array)
    for dot in g.points:
        for s, i in dot.connected_points:
            if s == 2:
                print("BORDER: ", [str(dot), str(i)])

    probable_folds = g.get_probable_folds()
    print('PROBABLE FOLDS:')
    for fold in probable_folds:
        print([str(i) for i in fold])
    possible_folds = g.get_possible_folds()
    print('POSSIBLE FOLDS:')
    for fold in possible_folds:
        print([str(i) for i in fold])
    legit_folds = g.get_legit_folds()


if __name__ == "__main__":
    main()
