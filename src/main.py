from pathlib import Path
from .utilities.instance_utility import Euclidean2D
from .genetic_algorithm.genetic_algorithm import RunGeneticAlgorithm

exclusions = set()
instance_type = 'euc_2d'
number_of_runs = 10
starting_run = 0

class Run:
    def __init__(self, instance_name, instance_type):
        self.instance_name = instance_name
        self.instance_type = instance_type

    def RunGeneticAlgorithmForInstance(self, number_of_runs, instance, starting_run):
        for i in range(number_of_runs):
            RunGeneticAlgorithm(instance, i + starting_run)

def GetInstanceNames(instances_file):
    instance_names = []
    for line in open(instances_file, 'r'):
        line = line.strip()
        if line and line not in exclusions:
            instance_names.append(line)
    return instance_names

if __name__ == '__main__':
    root_directory = Path(__file__).resolve().parents[1]
    instances_file = root_directory / 'res' / 'info' / 'euc-2d-instances.txt'
    instance_names = GetInstanceNames(instances_file)

    for instance_name in instance_names:
        run = Run(instance_name, instance_type)
        if instance_type == 'euc_2d':
            instance = Euclidean2D(instance_name)
        run.RunGeneticAlgorithmForInstance(number_of_runs, instance, starting_run)