class _Node:
    def __init__(self, name, colour) -> None:
        self.name = name
        self.colour = colour
    def __repr__(self) -> str:
        return f"{self.name}"

class UndirectedGraph:
    def __init__(self) -> None:
        self.nodelist = []
        self.connections = {}

    def add_node(self, node_name):
        if type(node_name) == list:
            for node in node_name:
                if node in [existing_nodes.name for existing_nodes in self.nodelist]:
                    raise Exception(f'{node} exist(s) in the nodelist. Try again.')
                else:
                    self.nodelist.append(_Node(node, None))
        else:
            for nodeIndex in range (0, len(self.nodelist)):
                if self.nodelist[nodeIndex].name == node_name:
                    raise Exception(f'{self.nodelist[nodeIndex].name} already exists in the nodelist. Try Again')
            node = _Node(node_name, None)
            self.nodelist.append(node)

    def add_random_nodes(self, length):
        asc = 65
        for iters in range (0, length):
            node = _Node(chr(asc), None)
            self.nodelist.append(node)
            asc+=1

    def test_adjacency(self, fro, to):
        if fro not in [nodes.name for nodes in self.nodelist] and to not in [nodes.name for nodes in self.nodelist]:
            raise Exception(f'{fro} and {to} are both not in the list of defined nodes')
        elif fro not in [nodes.name for nodes in self.nodelist]:
            raise Exception(f'{fro} is not in the list of defined nodes')
        elif to not in [nodes.name for nodes in self.nodelist]:
            raise Exception(f'{to} is not in the list of defined nodes')
        else:
            if to not in self.connections or fro not in self.connections:
                return False
            if to in self.connections[fro]:
                return True
            else:
                return False
        
    def add_edge(self, fro, to):
        count_to = 0
        count_fro = 0
        for nodeIndex in range (0, len(self.nodelist)):
            if self.nodelist[nodeIndex].name == fro:
                count_fro+=1
            elif self.nodelist[nodeIndex].name == to:
                count_to+=1

        if count_to == 0 or count_fro == 0:
            raise Exception('Node not a part of defined graph. Try a different node or define it then try again.')
        
        elif self.test_adjacency(fro, to):
            raise Exception('Nodes are already connected.')
        
        if fro not in self.connections:
            self.connections[fro] = [to]
        else:
            self.connections[fro].append(to)

        if to not in self.connections:
            self.connections[to] = [fro]
        else:
            self.connections[to].append(fro)

    def remove_edge(self, fro, to):
        if fro not in self.connections[to] or to not in self.connections[fro]:
            raise Exception('Edges are not connected')
        else:
            self.connections[to].remove(fro)
            self.connections[fro].remove(to)
    
    def degree(self, node):
        count_node = 0
        for nodeIndex in range (0, len(self.nodelist)):
            if self.nodelist[nodeIndex].name == node:
                count_node+=1
        if count_node == 1:
            return len(self.connections[node])
        else:
            raise Exception('Node not present in graph, try again.')              
        
    def display_connections(self):
        return self.connections
    
    def construct_adjacency_matrix(self):
        from pandas import DataFrame

        adj_mat = []
        adj_mat_df = DataFrame(index=[nodes for nodes in self.connections], columns=[nodes for nodes in self.connections])
        for rows in adj_mat_df.index:
            for cols in self.connections[rows]:
                adj_mat_df[rows][cols] = 1
        adj_mat_df.fillna(0, inplace=True)
        for rows in adj_mat_df.index:
            row = []
            for cols in adj_mat_df.columns:
               row.append(adj_mat_df[cols][rows])
            adj_mat.append(row)

        return adj_mat  

def havelHakimi(degree_seq):
    if len(degree_seq) == 3:
        return degree_seq
    else:
        s = degree_seq.pop(0)
        for indices in range (0, s):
            degree_seq[indices] = degree_seq[indices]-1
        
        return havelHakimi(degree_seq)

def generate_graph(size, type_of_graph):

    def generate_complete_graph(size):
        complete_graph = UndirectedGraph()
        complete_graph.add_random_nodes(size)
        from copy import deepcopy
        nodelist2 = [n.name for n in complete_graph.nodelist]
        nodelist3 = []
        for node in complete_graph.nodelist:
            nodelist3 = deepcopy(nodelist2)
            nodelist3.remove(node.name)
            complete_graph.connections[node.name] = [nodes for nodes in nodelist3]

        del nodelist2, nodelist3
        return complete_graph
    
    def generate_cycle_graph(size):
        cycle_graph = UndirectedGraph()
        cycle_graph.add_random_nodes(size)
        for indices in range(0, len(cycle_graph.nodelist)-1):
            cycle_graph.nodelist[indices]
            cycle_graph.add_edge(cycle_graph.nodelist[indices].name, cycle_graph.nodelist[indices+1].name)
        cycle_graph.add_edge(cycle_graph.nodelist[len(cycle_graph.nodelist)-1].name, cycle_graph.nodelist[0].name)

        return cycle_graph
    
    def generate_bipartite_graph(size):
        if type(size) != tuple:
            raise Exception('Size for a bipartite graph has to be a tuple of form (NumberOfNodes_set1, NumberOfNodes_set2)')
        else:
            bipartite_graph = UndirectedGraph()
            set1_length = size[0]
            set2_length = size[1]
            bipartite_graph.add_random_nodes(set1_length+set2_length)
            set1 = [bipartite_graph.nodelist[index] for index in range(0, set1_length)]
            set2 = [bipartite_graph.nodelist[index] for index in range(set1_length, set1_length+set2_length)]
            from random import randint
            counter = randint(3, set1_length*set2_length)

            while counter > 0:
                fro = set1[randint(0, set1_length-1)].name
                to = set2[randint(0, set2_length-1)].name
                while bipartite_graph.test_adjacency(fro, to):
                    fro = set1[randint(0, set1_length-1)].name
                    to = set2[randint(0, set2_length-1)].name
                bipartite_graph.add_edge(fro, to)
                counter-=1
            return bipartite_graph
    
    keywords = {
        'complete': generate_complete_graph,
        'cycle': generate_cycle_graph,
        'bipartite': generate_bipartite_graph
    }

    return keywords[type_of_graph](size)

# Bipartite: Build a code/logic such that 2 things are achieved:-
#   1. The connections are easily found (mostly using graph.connections)
#   2. Simultaneous updation of the node.colour attribute is made possible (a node object needs to be there, not possible with node.name as node.name is a string)

def dfs(graph_obj, source_node):
    if source_node == None:
        import random
        source = graph_obj.nodelist[random.randint(0, len(graph_obj.connections)-1)]
    elif source_node in graph_obj.connections:
        for node in graph_obj.nodelist:
            if node.name == source_node:
                source = node
    else:
        raise Exception('Node not in nodelist. Try again')

    frontier = []
    frontier.append(source.name)
    traversed = []
    while len(frontier)!=0:
        visitedNode = frontier.pop()
        traversed.append(visitedNode)
        for neighbour in graph_obj.connections[visitedNode]:
            if neighbour not in traversed and neighbour not in frontier:
                frontier.append(neighbour)

    return traversed

def bfs(graph_obj, source_node):
    if source_node == None:
        from random import randint
        source = graph_obj.nodelist[randint(0, len(graph_obj.connections)-1)]
    elif source_node in graph_obj.connections:
        for node in graph_obj.nodelist:
            if node.name == source_node:
                source = node
    else:
        raise Exception('Node not in nodelist. Try again')

    frontier = []
    frontier.append(source.name)
    traversed = []
    from copy import deepcopy
    while len(frontier)!=0:
        visited = frontier.pop(0)
        traversed.append(visited)
        adj = deepcopy(graph_obj.connections[visited])
        adj.reverse()
        for neighbour in adj:
            if neighbour not in traversed and neighbour not in frontier:
                frontier.append(neighbour)
        
    return traversed

def is_isomorphic(graph_obj1, graph_obj2):
    adjacency_matrix1 = graph_obj1.construct_adjacency_matrix()
    adjacency_matrix2 = graph_obj2.construct_adjacency_matrix()
    if len(graph_obj1.connections)!=len(graph_obj2.connections):
        return False
    else:
        no_of_edges1 = 0
        no_of_edges2 = 0
        for row in range(0, len(graph_obj1.connections)):
            for col in range (0, len(graph_obj1.connections)):
                if col>row and adjacency_matrix1[row][col] == 1:
                    no_of_edges1+=1
        for row in range(0, len(graph_obj2.connections)):
            for col in range (0, len(graph_obj2.connections)):
                if col>row and adjacency_matrix2[row][col] == 1:
                    no_of_edges2+=1

        if no_of_edges1!=no_of_edges2:
            return False
        
        else:
            degrees_1 = {}
            degrees_2 = {}
            for i in range(len(graph_obj1.nodelist)):
                degrees_1[str(i)] = 0
                degrees_2[str(i)] = 0

            for row in adjacency_matrix1:
                deg1 = sum(row)
                degrees_1[str(deg1)]+=1
            for row in adjacency_matrix2:
                deg2 = sum(row)
                degrees_2[str(deg2)]+=1

            if degrees_1 != degrees_2:
                return False
            else:
                return True