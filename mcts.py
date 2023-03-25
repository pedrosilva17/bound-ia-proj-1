import random

class MCTS:
    def __init__(self, root, player):
        self.root = root
        self.player = player

    def get_children(self):
        return self.children

    def traverse(self, random):
        node = self.root
        while len(node.get_children()) > 0:
            if random:
                node = node.get_children()[random.randint(0, len(node.get_children()))]
            else:
                node = node.get_children().sort(lambda x: x.get_value())[0].get_move()
        
        return node
        
    def simulate(self, node):
        end = false
        while not end:
            moves = node.get_state().available_moves(node.get_state().get_player_piece(), node.get_history())
            rand = random.randint(0, len(moves))
            node = generate_nodes(moves[rand], node.get_history())[0]
            end = node.get_state().is_final()

        if node.state.get_winner() == player:
            return 1
        else: 
            return -1

    def back_propagate(self, node, result):
        if node.get_parent() == None: return
        node.update_value(result)
        back_propagate(node.get_parent(), result)

    def best_choice(self):
        return self.root.get_children().sort(lambda x: x.get_value())[0].get_move()

    def populate_children(self, node, depth):
        if depth == 0: return

        moves = node.get_state().available_moves(node.get_state().get_player_piece(), node.get_history())
        states = generate_nodes(moves, node.get_history(), node)
        for state in states:
            node.add_child(state)
            populate_children(state, depth-1)

    def generate_nodes(self, moves, state_history, parent):
        nodes = []

        for move in moves:
            state_copy = deepcopy(state)
            history_copy = state_history
            state_copy.move(move[0], move[1], history_copy)
            history_copy.append(state_copy)
            nodes.append(MCTS_node(state_copy, history_copy, move, parent))

        return nodes

class MCTS_node:
    def __init__(self, state, history, move, parent):
        self.state = state
        self.history = history
        self.move = move
        self.parent = parent

        self.visits = 0
        self.value = 0
        self.children = []

    def update_value(self, nvalue):
        self.value += nvalue

    def get_value(self):
        return self.value
    
    def get_move(self):
        return self.move
    
    def get_player(self):
        return self.player

    def get_history(self):
        return self.history

    def get_state(self):
        return self.state

    def get_parent(self):
        return self.parent

    def get_children(self):
        return self.children

    def add_child(self, child):
        self.children.append(child)
        
