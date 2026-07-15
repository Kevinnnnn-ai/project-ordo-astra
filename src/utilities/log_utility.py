import numpy as np
import sys

class Log:
    def __init__(self, log_file):
        self.log_file = log_file

    def LogStart(self, instance):
        print(
            f'\nInstance ({instance.edge_weight_type}): {instance.instance_name}'
            f'\nNumber of nodes (n): {instance.number_of_nodes}'
            f'\nOptimal tour distance (fitness): {instance.optimal_fitness}'
            '\nCompiling and initializing GA...'
            '\n'
        )

        with open(self.log_file, 'w', newline='') as a:
            a.write(
                f'instanceName: {instance.instance_name}'
                f'\nn: {instance.number_of_nodes}'
                f'\noptFit: {instance.optimal_fitness}'
                '\n'
                '\ngenTime, gen, eliteFit, percentError:'
            )

    def LogGeneration(self, generation_time, generation_number, elite_fitness, percent_error):
        error_string = f'{percent_error:.3f}%' if percent_error is not None else 'N/A'
        print(
            f'Gen. Time: {generation_time:.3f}s, '
            f'Gen.: {generation_number}, '
            f'Elite: {elite_fitness}, '
            f'% Error: {error_string}'
        )

        error_value = f'{percent_error:.3f}' if percent_error is not None else 'N/A'
        with open(self.log_file, 'a', newline='') as a:
            a.write(f'\n{generation_time}, {generation_number}, {elite_fitness}, {error_value}')

    def LogEnd(self, elite_fitness, optimal_fitness, percent_error, end_time, start_time, tour):
        error_string = f'{percent_error:.3f}%' if percent_error is not None else 'N/A'
        print(
            f'\nElite tour distance (fitness): {elite_fitness}'
            f'\nOptimal tour distance (fitness): {optimal_fitness}'
            f'\nPercent Error (%): {error_string}'
            f'\nComputation Time (seconds): {end_time - start_time:.3f}s'
            '\n'
        )

        full_tour = np.array2string(tour, threshold=sys.maxsize)
        with open(self.log_file, 'a', newline='') as a:
            a.write(
                '\n'
                f'\ntour:\n{full_tour}'
                '\n'
                f'\neliteFit: {elite_fitness}'
                f'\npercentError: {percent_error}'
                f'\ncomputationTime: {end_time - start_time:.3f}s'
            )