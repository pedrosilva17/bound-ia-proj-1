from constants import Piece

class Vertex:
    def __init__(self, index: int, status: Piece = Piece.Empty):
        self.index = index
        self.status = status
    
    # Setters
    
    def set_index(self, index: int):
        self.index = index

    def set_status(self, status: Piece):
        self.status = status
        
    def __eq__(self, vertex):
        return self.index == vertex.index and self.status == vertex.status
    
    def __hash__(self):
        return hash(self.index)
        
    # Custom print
    
    def __repr__(self):
        return f"{self.index}-{self.status.name}"
    
    
class Graph:
    """
    Implements a graph composed of vertices (Vertex objects) and an adjacency list connecting them.
    Includes a vertex dictionary for easy vertex access.

    """
    def __init__(self, num_vertices: int = 0):
        """Constructor
        
        Args:
            num_vertices (int, optional): Number of unconnected empty vertices to initialize the graph with. Defaults to 0.
        """
        self.vertex_list: dict = {}
        self.adj_list: dict = {}
        for i in range(num_vertices):
            self.add_vertex(Vertex(i))
        
    # Getters
        
    def get_vertex(self, index: int) -> Vertex:
        """_summary_

        Args:
            index (int): _description_

        Raises:
            KeyError: _description_
            KeyError: _description_

        Returns:
            Vertex: _description_
        """
        if type(index) != int:
            raise KeyError("Vertex indices must be integers.")
        if not self.vertex_list.get(index):
            raise KeyError("That vertex does not exist in the graph.")
        return self.vertex_list.get(index)
        
    
    def get_siblings(self, index: int) -> list:
        """_summary_

        Args:
            index (int): _description_

        Returns:
            list: _description_
        """
        return self.adj_list.get(self.get_vertex(index))
    
    # Add
    
    def add_vertex(self, vertex: Vertex):
        """_summary_

        Args:
            vertex (Vertex): _description_
        """
        if vertex.index not in self.vertex_list:
            self.adj_list[vertex] = []
            self.vertex_list[vertex.index] = vertex
            
    def add_edge(self, v1: Vertex, v2: Vertex):
        """_summary_

        Args:
            v1 (Vertex): _description_
            v2 (Vertex): _description_
        """
        if v2 not in self.adj_list[v1]:
            self.adj_list[v1].append(v2)
        if v1 not in self.adj_list[v2]:
            self.adj_list[v2].append(v1)
    
    # Remove
    
    def remove_vertex(self, index: int):
        """_summary_

        Args:
            index (int): _description_
        """
        for adj in self.adj_list:
            if self.get_vertex(index) in self.adj_list[adj]:
                self.adj_list[adj].pop(self.adj_list[adj].index(self.get_vertex(index)))
        self.adj_list.pop(self.get_vertex(index))
        self.vertex_list.pop(index)

    def remove_edge(self, v1: Vertex, v2):
        """_summary_

        Args:
            v1 (_type_): _description_
            v2 (_type_): _description_
        """
        self.adj_list[v1].remove(v2)
        self.adj_list[v2].remove(v1)
        
    def __eq__(self, graph):
        try:
            if len(self.adj_list) == len(graph.adj_list):
                for vertex in self.adj_list:
                        if self.adj_list[vertex] != graph.adj_list[vertex]: return False
                return True
        except KeyError:
            return False
                
        
    # Custom print    
        
    def __repr__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return str(self.adj_list)
    