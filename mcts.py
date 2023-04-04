import random
import math
from copy import deepcopy


class MCTS_node:
    def __init__(self, state, move, parent):
        self.state = state
        self.move = move
        self.parent = parent
        self.max_children = state[0].count_moves(
            state[0].player_piece, state[1])

        self.visits = 0
        self.value = 0
        self.ucb = 0
        self.children = []

    def update_value(self, nvalue):
        self.value += nvalue

    def update_visits(self):
        self.visits += 1

    def update_ucb(self, c=2):
        if self.parent is None:
            p_visits = 0
        else:
            p_visits = self.parent.visits

        self.ucb = self.value + c * math.sqrt(p_visits/self.visits)

    def add_child(self, child):
        self.children.append(child)


class MCTS:
    """Class representing the MCTS algorithm.
    """
    def __init__(self, root: MCTS_node, player):
        """Initialize a new instance of the MCTS algorithm.

        Args:
            root (MCTS_node): The starting point of the algorithm.
            player (_type_): _description_
        """
        self.root = root
        self.player = player
        self.leaves = [root]

    def select(self):
        map(lambda x: x.update_ucb(), self.leaves)
        filter(lambda x: check_children(x), self.leaves)

        self.leaves.sort(key=lambda x: x.ucb, reverse=True)
        return self.leaves[0]

    def check_children(self, node):
        if len(node.children) != node.max_children:
            return True

    def expand(self, node):

        moves = node.state[0].available_moves(
            node.state[0].player_piece, node.state[1])
        rand = random.randint(0, len(moves)-1)
        child = self.generate_node(moves[rand], node)
        node.add_child(child)

        self.leaves.append(child)

        if len(node.children) == node.max_children:
            self.leaves.remove(node)

        return child

    def simulate(self, node):
        end = False
        while not end:
            moves = node.state[0].available_moves(
                node.state[0].player_piece, node.state[1])
            rand = random.randint(0, len(moves)-1)
            node = self.generate_node(moves[rand], node)
            end = node.state[0].is_final()

        if node.state[0].simulate_winner() == self.player:
            return 1
        else:
            return -1

    def back_propagate(self, node, result):

        if node.parent == None:
            return
        node.update_value(result)
        node.update_visits()
        self.back_propagate(node.parent, result)

    def best_choice(self):
        self.root.children.sort(key = lambda x: x.value, reverse = True)
        return self.root.children[0]

    def generate_node(self, move, parent):

        state_copy = deepcopy(parent.state[0])
        history_copy = deepcopy(parent.state[1])
        state_copy.move(move[0], move[1], history_copy)
        history_copy.append(state_copy)

        return MCTS_node((state_copy, history_copy), move, parent)
