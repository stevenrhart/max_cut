# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

## ------- import packages -------
# Import networkx for graph tools
import networkx as nx

# Import dwave_networkx for d-wave graph tools/functions
import dwave_networkx as dnx

# Import dwave.system packages for the QPU
from dwave.system import DWaveSampler, EmbeddingComposite

# Import matplotlib.pyplot to draw graphs on screen
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

def create_graph(edges):
    """Returns a graph based on the specified list of edges.

    Args:
        edges(list of tuples): each tuple represents an edge in the graph
    """
    # Create empty graph
    G = nx.Graph()

    # Add edges to graph - this also adds the nodes
    G.add_edges_from(edges)

    return G

def get_qubo(nodes, edges):
    """Returns a dictionary representing a QUBO.

    Args:
        nodes(list of integers): nodes for the graph
        edges(list of tuples): each tuple represents an edge in the graph
    """
    # Create dict to track number of edges per node
    d = dict.fromkeys(nodes, 0)

    # Create QUBO representation
    Q = {}
    
    for i, j in G.edges:
        # Add quadratic terms 
        Q[(i, j)] = 2 
        
        # Populate d for number of edges per node
        if i in d:
            d[i] += 1
        if j in d:
            d[j] += 1

    for i in G.nodes:
        # Add linear terms
        Q[(i, i)] = (-1 * d[i])

    return Q

def run_on_qpu(Q, sampler, chainstrength, num_reads):
    """Runs the QUBO problem Q on the sampler provided.

    Args:
        Q(dict): a representation of a QUBO
        sampler(dimod.Sampler): a sampler that uses the QPU
        chain_strength(int): the chainstrength value to use in the sampler
        num_reads(int): the number of reads to use in the sampler 
    """
    sample_set = sampler.sample_qubo(Q, chain_strength=chainstrength, num_reads=num_reads)

    return sample_set

## ------- Main program -------
if __name__ == "__main__":

    # # Test Graph 0 (solution = 2, 1)
    # nodes = [0, 1, 2]
    # edges = [(0, 1), (1, 2)]

    # # Test Graph 1 (solution = 2, 3)
    # nodes = [0, 1, 2, 3, 4]
    # edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)]

    # # Test Graph 2
    # nodes = [0, 1, 2, 3, 4, 5, 6]
    # edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 0)]

    # Test Graph 4 (solution = 30)
    nodes = list(i for i in range(24))
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (0, 11), 
    (0, 12), (1, 13), (2, 14), (3, 15), (4, 16), (5, 17), (6, 18), (7, 19), (8, 20), (9, 21), (10, 22), (11, 23),
    (12, 16), (12, 20), (13, 17), (13, 21), (14, 18), (14, 22), (15, 19), (15, 23), (16, 20), (17, 21), (18, 22), (19, 23)]
    
    G = create_graph(edges)
    Q = get_qubo(nodes, edges)

    chainstrength = 3 # update
    num_reads = 100 # update

    # Define the sampler and run the problem
    sampler = EmbeddingComposite(DWaveSampler())
    sample_set = run_on_qpu(Q, sampler, chainstrength, num_reads)
    
    # Print the solution
    # print(sample_set) 
    result = list(sample_set.first.sample[i] for i in nodes)
    set_1 = []
    set_2 = []
    for i in range(len(result)):
        if result[i] == 1:
            set_1.append(i)
        else:
            set_2.append(i)
    print('The maximum cut is achieved by dividing into sets of length', len(set_1), 'and', len(set_2))

    # Calculate max_cuts
    max_cuts = 0
    for (i, j) in edges:
        if i in set_1 and j in set_2:
            max_cuts += 1
        elif j in set_1 and i in set_2:
            max_cuts += 1
    print('The maximum number of cuts is ', max_cuts)
    print(set_1, set_2)

    # Visualize the results
    subset_1 = G.subgraph(set_1)
    not_set_1 = list(set(G.nodes()) - set(set_1))
    subset_0 = G.subgraph(not_set_1)
    pos = nx.spring_layout(G)
    plt.figure()

    # Save original problem graph
    original_name = "graph_original.png"
    nx.draw_networkx(G, pos=pos, with_labels=True)
    plt.savefig(original_name, bbox_inches='tight')

    # Save solution graph
    # Note: red nodes are in the set, blue nodes are not
    solution_name = "graph_solution.png"
    nx.draw_networkx(subset_1, pos=pos, with_labels=True, node_color='r', font_color='k')
    nx.draw_networkx(subset_0, pos=pos, with_labels=True, node_color='b', font_color='w')
    plt.savefig(solution_name, bbox_inches='tight')

    print("Your plots are saved to {} and {}".format(original_name, solution_name))