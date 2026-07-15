import numpy as np
import tsplib95 as tl
from pathlib import Path

def GetOptimalFitnesses(optimal_fitnesses_file):
    optimal_fitnesses = {}
    if not optimal_fitnesses_file.exists():
        return optimal_fitnesses

    with open(optimal_fitnesses_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' not in line:
                continue

            key, value = line.split(':', 1)
            try:
                optimal_fitnesses[key.strip()] = int(value.strip())
            except ValueError:
                continue

    return optimal_fitnesses

class Euclidean2D:
    def __init__(self, instance_name):
        self.instance_type = 'Euclidean 2D TSP'
        self.root_directory = Path(__file__).resolve().parents[2]
        self.optimal_fitnesses_file = self.root_directory / 'res' / 'info' / 'opt-fits.txt'

        self.instance_name = instance_name
        self.instance_file = self.root_directory / 'res' / 'tsplib' / 'tsp' / f'{instance_name}.tsp'
        self.instance = tl.load(self.instance_file)

        self.edge_weight_type = self.instance.edge_weight_type
        nodes = self.instance.node_coords.values()
        self.nodes = np.array(list(nodes))
        self.optimal_fitness = GetOptimalFitnesses(self.optimal_fitnesses_file).get(self.instance_name)
        self.number_of_nodes = self.nodes.shape[0]

    def GetNodes(self):
        return self.nodes

    def GetNumberOfNodes(self):
        return self.number_of_nodes