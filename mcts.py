import random
import math
from copy import deepcopy


class MCTS_node:
    """A node of the Tree Structure of MCTS
    """

    def __init__(self, state, move, parent):
        """Initialize a MCTS node with its state, the move that originated it and its parent node

        Args:
            state (State): The node's state
            move (tuple): The move that originated it
            parent (MCTS_node): The parent node
        """
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
        """Update a value of a node

        Args:
            nvalue (int): The new value to be added to self.value
        """
        self.value += nvalue

    def update_visits(self):
        """
        Add a visit to the node
        """
        self.visits += 1

    def update_ucb(self, c=2):
        """Update the Upper Confidence Bound value

        Args:
            c (int, optional): The confidence constant value. Defaults to 2.
        """
        if self.parent is None:
            p_visits = 0
        else:
            p_visits = self.parent.visits

        self.ucb = self.value + c * math.sqrt(p_visits/self.visits)

    def add_child(self, child):
        """Add a children to the node

        Args:
            child (MCTS_node): Add an MCTS_node child to this node
        """
        self.children.append(child)


class MCTS:
    """Class representing the MCTS algorithm.
    """

    def __init__(self, root: MCTS_node, player):
        """Initialize a new instance of the MCTS algorithm.

        Args:
            root (MCTS_node): The starting point of the algorithm.
            player (Piece): The player that is calling MCTS (the one using it as its method of move decidal)
        """
        self.root = root
        self.player = player
        self.leaves = [root]

    def select(self):
        """Select the leaf to be expanded based on its UCB

        Returns:
            MCTS_node: The selected node
        """
        map(lambda x: x.update_ucb(), self.leaves)
        filter(lambda x: check_children(x), self.leaves)

        self.leaves.sort(key=lambda x: x.ucb, reverse=True)
        return self.leaves[0]

    def check_children(self, node):
        """Checks if found all children

        Args:
            node (MCTS_node): The node to be checked

        Returns:
            boolean: True if 
        """
        if len(node.children) != node.max_children:
            return True

    def expand(self, node):
        """Expand a node to one of its children

        Args:
            node (MCTS_node): Node to be expanded

        Returns:
            MCTS_node: The expanded child
        """

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
        """Simulates a game from a node until it reaches an end state

        Args:
            node (MCTS_node): The node from which the simulation will begin

        Returns:
            integer: Returns 1 if self.player won, -1 otherwise
        """
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
        """Back propagates result from node to its parent, until the root is reached, updating the nodes' values

        Args:
            node (MCTS_node): The node to be updated, and the child of the following node
            result (integer): The value to be updated
        """

        if node.parent == None:
            return
        node.update_value(result)
        node.update_visits()
        self.back_propagate(node.parent, result)

    def best_choice(self):
        """Finds the best choice from the root's children

        Returns:
            MCTS_node: The best child (highest value)
        """
        self.root.children.sort(key=lambda x: x.value, reverse=True)
        return self.root.children[0]

    def generate_node(self, move, parent):
        """Creates an MCTS_node

        Args:
            move (tuple): The move that originated this node
            parent (MCTS_node): The parent MCTS_node

        Returns:
            MCTS_node: The created MCTS_node
        """

        state_copy = deepcopy(parent.state[0])
        history_copy = deepcopy(parent.state[1])
        state_copy.move(move[0], move[1], history_copy)
        history_copy.append(state_copy)

        return MCTS_node((state_copy, history_copy), move, parent)
