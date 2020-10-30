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

import sys
import networkx as nx
import dwave_networkx as dnx
from dwave.system import DWaveSampler, EmbeddingComposite
from dimod import BinaryQuadraticModel

# Import matplotlib.pyplot to draw graphs on screen
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

def get_qubo():
    """Returns a dictionary representing a QUBO.
    """
    # Create QUBO based on min(SUM(-xi - xj + 2xi*xj))
    Q = {}
    for i, j in G.edges:
        Q[(i, j)] = 2  # Add quadratic terms
    for i in G.nodes:
        Q[(i, i)] = (-1 * d[i])  # Add linear terms

    return Q

def get_ising():
    """Returns a dictionary representing the Ising formulation.
    """
    # Create empty Ising dicts for h and J
    h = {}
    J = {}
    
    # Populate Ising representation
    for u, v in G.edges:
        J[(u, v)] = 0.5
    for n in G.nodes:
        h[n] = 0 

    return h, J

def get_bqm(Q):
    """Returns a bqm representation of the problem.
    
    Args:
        Q(qubo): dictionary representing a QUBO
    """
    # Convert to bqm
    bqm = BinaryQuadraticModel.from_qubo(Q)

    return bqm


## ------- Main program -------
if __name__ == "__main__":

    # TODO: Consider updating such that graphs can be randomly generated based on user input of number of nodes
    # # Small Test Graph (solution = 2, 1)
    # nodes = [0, 1, 2]
    # edges = [(0, 1), (1, 2)]

    # Large Test Graph 4 (solution = 30)
    nodes = list(i for i in range(24))
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (0, 11), 
    (0, 12), (1, 13), (2, 14), (3, 15), (4, 16), (5, 17), (6, 18), (7, 19), (8, 20), (9, 21), (10, 22), (11, 23),
    (12, 16), (12, 20), (13, 17), (13, 21), (14, 18), (14, 22), (15, 19), (15, 23), (16, 20), (17, 21), (18, 22), (19, 23)]
    
    # Create graph as defined above
    G = nx.Graph()
    G.add_edges_from(edges)

    # Create dictionary for edges per node
    d = dict.fromkeys(G.nodes, 0)
    for i, j in G.edges:
        if i in d:
            d[i] += 1
        if j in d:
            d[j] += 1

    # Set formulation type based on user input
    formulation = sys.argv[1]

    # Set parameters to run the problem
    chainstrength = 3 # update as needed
    num_reads = 10 # update as needed
    sampler = EmbeddingComposite(DWaveSampler())

    # Formulate and run the problem based on command line input
    if formulation == "qubo":
        Q = get_qubo()
        sample_set = sampler.sample_qubo(Q, chain_strength=chainstrength, num_reads=num_reads)
    elif formulation == "ising":
        h, J = get_ising()
        sample_set = sampler.sample_ising(h, J, chain_strength=chainstrength, num_reads=num_reads)
    elif formulation == "bqm":
        Q = get_qubo()
        bqm = get_bqm(Q)
        sample_set = sampler.sample(bqm)

    # Determine the resulting sets
    result = list(sample_set.first.sample[i] for i in G.nodes)
    set_1, set_2 = [], []
    for i in range(len(result)):
        if result[i] == 1:
            set_1.append(i)
        else:
            set_2.append(i)
    
    # Calculate max_cuts
    max_cuts = 0
    for (i, j) in G.edges:
        if i in set_1 and j in set_2:
            max_cuts += 1
        elif j in set_1 and i in set_2:
            max_cuts += 1
    
    # Print the solution
    print('The maximum cut is achieved by dividing into sets of length', len(set_1), 'and', len(set_2))
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
    solution_name = "graph_solution.png"
    nx.draw_networkx(subset_1, pos=pos, with_labels=True, node_color='r', font_color='k')
    nx.draw_networkx(subset_0, pos=pos, with_labels=True, node_color='b', font_color='w')
    plt.savefig(solution_name, bbox_inches='tight')

    print("Your plots are saved to {} and {}".format(original_name, solution_name))