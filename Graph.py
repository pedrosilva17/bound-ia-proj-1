from constants import Piece


class Vertex:
    """Class representing a vertex storing an index and a status.
    """

    def __init__(self, index: int, status: Piece = Piece.Empty):
        """Initialize a new vertex, given an index and a status (the piece type stored within).

        Args:
            index (int): The index of the vertex.
            status (Piece, optional): The type of piece stored in the vertex.
            Defaults to Piece.Empty.
        """
        self.index = index
        self.status = status

    def set_index(self, index: int):
        """Set a new index for the vertex.

        Args:
            index (int): The new index.
        """
        self.index = index

    def set_status(self, status: Piece):
        """Set a new status for the vertex.

        Args:
            status (Piece): The new status (new piece type).
        """
        self.status = status

    def __eq__(self, vertex):
        return self.index == vertex.index and self.status == vertex.status

    def __hash__(self):
        return hash(self.index)

    def __repr__(self):
        return f"{self.index}-{self.status.name}"


class Graph:
    """
    Class representing a graph composed of vertices (Vertex objects) and an adjacency list connecting them.
    Includes a vertex dictionary for easy vertex access.
    """

    def __init__(self, num_vertices: int = 0):
        """Initialize a new disconnected graph, given a number of vertices.

        Args:
            num_vertices (int, optional): Number of empty vertices to initialize the graph with. Defaults to 0.
        """
        self.vertex_list: dict = {}
        self.adj_list: dict = {}
        for i in range(num_vertices):
            self.add_vertex(Vertex(i))

    def get_vertex(self, index: int) -> Vertex:
        """Get the vertex with the given index.

        Args:
            index (int): The index of the desired vertex.

        Raises:
            KeyError: The index is not an integer.
            KeyError: The index does not correspond to a vertex in the graph.

        Returns:
            Vertex: The vertex with the specified index.
        """
        if type(index) != int:
            raise KeyError("Vertex indices must be integers.")
        if not self.vertex_list.get(index):
            raise KeyError("That vertex does not exist in the graph.")
        return self.vertex_list.get(index)

    def get_siblings(self, index: int) -> list:
        """Get the vertices connected to the vertex of the given index.

        Args:
            index (int): The index of the vertex.

        Returns:
            list: A list of the vertices connected to the specified vertex.
        """
        return self.adj_list.get(self.get_vertex(index))

    def add_vertex(self, vertex: Vertex):
        """Add a new vertex to the graph.

        Args:
            vertex (Vertex): The new vertex to be added.
        """
        if vertex.index not in self.vertex_list:
            self.adj_list[vertex] = []
            self.vertex_list[vertex.index] = vertex

    def add_edge(self, v1: Vertex, v2: Vertex):
        """Add a new edge to the graph connecting two given vertices in both directions.

        Args:
            v1 (Vertex): The first vertex.
            v2 (Vertex): The second vertex.
        """
        if v2 not in self.adj_list[v1]:
            self.adj_list[v1].append(v2)
        if v1 not in self.adj_list[v2]:
            self.adj_list[v2].append(v1)

    def remove_vertex(self, index: int):
        """Remove the vertex of a given index from the graph.

        Args:
            index (int): The index of the vertex.
        """
        for adj in self.adj_list:
            if self.get_vertex(index) in self.adj_list[adj]:
                self.adj_list[adj].pop(
                    self.adj_list[adj].index(self.get_vertex(index)))
        self.adj_list.pop(self.get_vertex(index))
        self.vertex_list.pop(index)

    def remove_edge(self, v1: Vertex, v2: Vertex):
        """Remove an edge from the graph.

        Args:
            v1 (Vertex): The vertex on one end of the edge.
            v2 (Vertex): The vertex on the other end of the edge.
        """
        self.adj_list[v1].remove(v2)
        self.adj_list[v2].remove(v1)

    def __eq__(self, graph):
        try:
            if len(self.adj_list) == len(graph.adj_list):
                for vertex in self.adj_list:
                    if self.adj_list[vertex] != graph.adj_list[vertex]:
                        return False
                return True
        except KeyError:
            return False

    def __repr__(self):
        return str(self.adj_list)
