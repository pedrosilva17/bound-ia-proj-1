import random
import math

class MCTS:
    def __init__(self, root, player):
        self.root = root
        self.player = player
        self.leaves = list(root)

    def get_children(self):
        return self.children

    # def traverse(self):
    #     node = self.root
    #     while len(node.get_children()) > 0:
    #         if random:
    #             node = node.get_children()[random.randint(0, len(node.get_children()))]
    #         else:
    #             node = node.get_children().sort(lambda x: x.get_value())[0]  
    #     return node

    # def populate_children(self, node):
    #     moves = node.state.available_moves(node.state[0].get_player_piece(), node.state[1])
    #     child = generate_node(moves, node)
    #     node.add_child(state)
    #     self.leaves.append(child)
    #     if (node.children == node.max_children):
    #         self.leaves.remove(node)
    #     return child

    def generate_node(self, move, parent):

        state_copy = deepcopy(parent.state[0])
        history_copy = parent.state[1]
        state_copy.move(move[0], move[1], history_copy)
        history_copy.append(state_copy)

        return MCTS_node((state_copy, history_copy), move, parent)

    def select(self):
        map(lambda x: x.update_ucb(), self.leaves)
        return self.leaves.sort(lambda x: x.ucb)[0]

    def expand(self, node):

        moves = node.state.available_moves(node.state.get_player_piece(), node.state[1])
        rand = random.randint(0, len(moves))
        child = generate_node(moves[rand], node.state[1], node)
        node.add_child(state)

        if node.max_children != 0:
            self.leaves.append(child)

        if (node.children == node.max_children):
            self.leaves.remove(node)

        return child

    def simulate(self, node):
        end = false
        while not end:
            moves = node.state[0].available_moves(node.state[0].get_player_piece(), node.state[1])
            rand = random.randint(0, len(moves))
            node = generate_node(moves[rand], node)[0]
            end = node.state[0].is_final()

        if node.state[0].get_winner() == player:
            return 1
        else: 
            return -1

    def back_propagate(self, node, result):

        if node.get_parent() == None: return
        node.update_value(result)
        node.update_visits(result)
        back_propagate(node.get_parent(), result)

    def best_choice(self):

        return self.root.get_children().sort(lambda x: x.get_value())[0].get_move()

class MCTS_node:
    def __init__(self, state, move, parent):
        self.state = state
        self.move = move
        self.parent = parent
        self.max_children = state[0].count_moves(state[0].get_player_piece(), state[1])

        self.visits = 0
        self.value = 0
        self.ucb = 0
        self.children = []

    def update_value(self, nvalue):
        self.value += nvalue

    def update_visits(self):
        self.visits += 1

    def update_ucb(self, c=2):
        if parent == None:
            p_visits = 0
        else:
            p_visits = self.parent.visits

        self.ucb = self.value + c * math.sqrt(p_visits/self.visits)

    def add_child(self, child):
        self.children.append(child)
        
