import numpy as np
import numba
import os
from pathlib import Path
from scipy.spatial.distance import cdist
from time import perf_counter
from ..utilities.log_utility import Log

population_size = 200
maximum_generations = 1000
selection_size = 7
order_crossover_rate = 0.85
swap_mutation_rate = 0.03
minimum_change = 1e-3
convergence_generation = 50
two_opt_percentile = 10

NO_GIL = True
CAN_PARALLEL = True
CAN_CACHE = True

ROOT_DIR = Path(__file__).resolve().parents[2]

@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def CreateTour(number_of_nodes):
    tour = np.arange(number_of_nodes)
    np.random.shuffle(tour)
    return tour

@numba.njit(parallel=CAN_PARALLEL, nogil=NO_GIL, cache=CAN_CACHE)
def CreatePopulation(population_size, number_of_nodes):
    population = np.empty((population_size, number_of_nodes), dtype=np.int64)
    for i in numba.prange(population_size):
        population[i] = CreateTour(number_of_nodes)
    return population

@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def CalculateIndividualFitness(number_of_nodes, tour, distance_matrix):
    fitness = 0.0
    for i in range(number_of_nodes - 1):
        fitness += distance_matrix[tour[i], tour[i + 1]]
    fitness += distance_matrix[tour[-1], tour[0]]
    return fitness

@numba.njit(parallel=CAN_PARALLEL, nogil=NO_GIL, cache=CAN_CACHE)
def CalculatePopulationFitness(population_size, number_of_nodes, population, distance_matrix):
    fitnesses = np.empty(population_size, dtype=np.float64)
    for i in numba.prange(population_size):
        fitnesses[i] = CalculateIndividualFitness(number_of_nodes, population[i], distance_matrix)
    return fitnesses

@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def RunSelection(fitnesses, selection_size):
    elite_index = np.random.randint(len(fitnesses))
    elite_fitness = fitnesses[elite_index]
    for i in range(1, selection_size):
        tour_index = np.random.randint(len(fitnesses))
        if fitnesses[tour_index] < elite_fitness:
            elite_fitness = fitnesses[tour_index]
            elite_index = tour_index
    return elite_index

@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def RunOrderCrossover(order_crossover_rate, parent_1, parent_2, number_of_nodes):
    if np.random.random() <= order_crossover_rate:
        lower_bound = np.random.randint(number_of_nodes)
        upper_bound = np.random.randint(number_of_nodes)
        while lower_bound == upper_bound:
            upper_bound = np.random.randint(number_of_nodes)
        if lower_bound > upper_bound:
            lower_bound, upper_bound = upper_bound, lower_bound

        child = np.full(number_of_nodes, -1, dtype=np.int64)
        child[lower_bound : upper_bound] = parent_1[lower_bound : upper_bound]

        fill = []
        subset = set(parent_1[lower_bound : upper_bound])
        for i in parent_2:
            if i not in subset:
                fill.append(i)

        j = 0
        for i in range(number_of_nodes):
            if child[i] == -1:
                child[i] = fill[j]
                j += 1
        return child

    else:
        if np.random.random() < 0.5:
            return parent_2.copy()
        return parent_1.copy()

@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def RunSwapMutation(swap_mutation_rate, tour, number_of_nodes):
    if np.random.random() < swap_mutation_rate:
        mutated_tour = tour.copy()

        gene_1 = np.random.randint(number_of_nodes)
        gene_2 = np.random.randint(number_of_nodes)
        while gene_1 == gene_2:
            gene_2 = np.random.randint(number_of_nodes)
        mutated_tour[gene_1], mutated_tour[gene_2] = mutated_tour[gene_2], mutated_tour[gene_1]
        return mutated_tour

    return tour

@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def GetElite(fitnesses, population):
    elite_fitness_index = np.argmin(fitnesses)
    elite_tour = population[elite_fitness_index].copy()
    elite_fitness = np.float64(fitnesses[elite_fitness_index])
    return elite_tour, elite_fitness

@numba.njit(parallel=CAN_PARALLEL, nogil=NO_GIL, cache=CAN_CACHE)
def MassCreatePopulation(population_size, fitnesses, selection_size, population, order_crossover_rate, swap_mutation_rate, number_of_nodes):
    new_population = np.empty((population_size - 1, number_of_nodes), dtype=np.int64)

    for i in numba.prange(1, population_size):
        tour_index_1 = RunSelection(fitnesses, selection_size)
        tour_index_2 = RunSelection(fitnesses, selection_size)
        while tour_index_1 == tour_index_2:
            tour_index_1 = RunSelection(fitnesses, selection_size)
        parent_1 = population[tour_index_1]
        parent_2 = population[tour_index_2]

        new_population[i - 1] = RunOrderCrossover(order_crossover_rate, parent_1, parent_2, number_of_nodes)
        new_population[i - 1] = RunSwapMutation(swap_mutation_rate, new_population[i - 1], number_of_nodes)
    return new_population

@numba.njit(parallel=CAN_PARALLEL, nogil=NO_GIL, cache=CAN_CACHE)
def RunTwoOptOnPercentile(number_of_tours, population, fitnesses, distance_matrix, number_of_nodes, threshold):
    for i in numba.prange(number_of_tours):
        if fitnesses[i] <= threshold:
            population[i] = RunTwoOpt(number_of_nodes, population[i], distance_matrix)
            fitnesses[i] = CalculateIndividualFitness(number_of_nodes, population[i], distance_matrix)
    return population, fitnesses

@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def RunTwoOpt(number_of_nodes, tour, distance_matrix):
    has_improved = True
    while has_improved:
        has_improved = False
        for i in range(1, number_of_nodes - 2):
            for j in range(i + 1, number_of_nodes):
                node_1 = tour[i - 1]
                node_2 = tour[i]
                node_3 = tour[j]
                node_4 = tour[(j + 1) % number_of_nodes]
                if distance_matrix[node_1, node_2] + distance_matrix[node_3, node_4] > distance_matrix[node_1, node_3] + distance_matrix[node_2, node_4]:
                    tour[i : j + 1] = tour[i : j + 1][: : -1]
                    has_improved = True
    return tour

def RunGeneticAlgorithm(instance, run_number):
    run_directory = ROOT_DIR / 'stdout' / 'runs' / instance.instance_name
    if not run_directory.is_dir():
        print(f'WARNING: Cannot locate {run_directory}, creating it...')
        os.makedirs(run_directory, exist_ok=True)

    run_file = run_directory / f'{instance.instance_name}_{run_number}.txt'
    log = Log(run_file)

    optimal_fitness = instance.optimal_fitness
    number_of_nodes = instance.GetNumberOfNodes()
    nodes = instance.GetNodes()
    distance_matrix = np.round(cdist(nodes, nodes, 'euclidean')).astype(np.int64)

    start_time = perf_counter()
    log.LogStart(instance)

    generation_start_time = perf_counter()

    population = CreatePopulation(population_size, number_of_nodes)
    fitnesses = CalculatePopulationFitness(population_size, number_of_nodes, population, distance_matrix)
    elite_tour, elite_fitness = GetElite(fitnesses, population)

    percent_error = (elite_fitness - optimal_fitness) / optimal_fitness * 100 if optimal_fitness is not None else None
    generation_time = perf_counter() - generation_start_time
    log.LogGeneration(generation_time, 0, elite_fitness, percent_error)

    stagnant_generations = 0
    for generation_number in range(1, maximum_generations + 1):
        generation_start_time = perf_counter()

        offspring_population = MassCreatePopulation(population_size, fitnesses, selection_size, population, order_crossover_rate, swap_mutation_rate, number_of_nodes)
        offspring_fitnesses = CalculatePopulationFitness(population_size - 1, number_of_nodes, offspring_population, distance_matrix)
        threshold = np.percentile(offspring_fitnesses, two_opt_percentile)
        offspring_population, offspring_fitnesses = RunTwoOptOnPercentile(population_size - 1, offspring_population, offspring_fitnesses, distance_matrix, number_of_nodes, threshold)

        new_population = np.empty((population_size, number_of_nodes), dtype=np.int64)
        new_fitnesses = np.empty(population_size, dtype=np.float64)
        new_population[0] = elite_tour.copy()
        new_fitnesses[0] = elite_fitness
        new_population[1 :] = offspring_population
        new_fitnesses[1 :] = offspring_fitnesses

        population, fitnesses = new_population, new_fitnesses
        candidate_elite_tour, candidate_elite_fitness = GetElite(fitnesses, population)
        if candidate_elite_fitness < elite_fitness - minimum_change:
            elite_tour = candidate_elite_tour.copy()
            elite_fitness = candidate_elite_fitness
            stagnant_generations = 0
        else:
            stagnant_generations += 1
        elite_tour = RunTwoOpt(number_of_nodes, elite_tour.copy(), distance_matrix)
        elite_fitness = CalculateIndividualFitness(number_of_nodes, elite_tour, distance_matrix)

        percent_error = (elite_fitness - optimal_fitness) / optimal_fitness * 100 if optimal_fitness is not None else None
        generation_time = perf_counter() - generation_start_time
        log.LogGeneration(generation_time, generation_number, elite_fitness, percent_error)

        if (stagnant_generations >= convergence_generation) or (generation_number >= maximum_generations) or (optimal_fitness is not None and elite_fitness == optimal_fitness):
            end_time = perf_counter()
            log.LogEnd(elite_fitness, optimal_fitness, percent_error, end_time, start_time, elite_tour)
            return elite_fitness