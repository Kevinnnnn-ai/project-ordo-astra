import os
import numpy as np
import matplotlib.pyplot as plt
import tsplib95
from pathlib import Path

class Plot:
    def __init__(self):
        self.root_directory = Path(__file__).resolve().parents[2]
        self.instance_directory = self.root_directory / 'res' / 'tsplib' / 'tsp'
        self.instance_plot_directory = self.root_directory / 'stdout' / 'instance-plots'
        self.run_directory = self.root_directory / 'stdout' / 'runs'
        self.analysis_directory = self.root_directory / 'stdout' / 'analysis'

        self.percent_error_fit_power = 'log-linear'
        self.computation_time_fit_power = 'log-linear'
        self.can_show_aggregate_convergence = True
        self.can_show_aggregate_convergence_statistics = True

    def PlotEuclidean2DInstances(self):
        if not self.instance_plot_directory.is_dir():
            print(f'WARNING: Cannot locate {self.instance_plot_directory}')
            os.makedirs(self.instance_plot_directory, exist_ok=True)
            return
        if not self.instance_directory.is_dir():
            print(f'ERROR: Cannot locate {self.instance_directory}')
            return

        for instance_file in self.instance_directory.iterdir():
            if instance_file.is_file() and (instance_file.suffix == '.tsp'):
                try:
                    instance = tsplib95.load(instance_file)
                    if instance.edge_weight_type == 'EUC_2D':
                        nodes = instance.node_coords.values()
                        coordinates = np.array(list(nodes))
                        x = coordinates[:, 0]
                        y = coordinates[:, 1]

                        plt.clf()
                        plt.scatter(x, y, marker='o', c='blue', s=5)
                        plt.axis('equal')

                        name = instance.name
                        number_of_nodes = len(coordinates)
                        plt.title(f'{name}, n = {number_of_nodes}, 2D Euclidean TSP')
                        plt.xlabel('X-Coordinate')
                        plt.ylabel('Y-Coordinate')

                        plt.savefig(rf'{self.instance_plot_directory}\{name}.png')
                        plt.close()

                except Exception as e:
                    print(e)

                    if not self.run_directory.is_dir():
                        print(f'Cannot locate {self.run_directory}')
                        return

    def DrawFitCurve(self, axis, number_of_nodes_array, position_array, medians, fit_power, variable_symbol):
        if fit_power == 'log-linear':
            mask = medians > 0
            if mask.sum() < 2:
                print('Skipping log-linear fit: need at least 2 positive medians.')
                return

            exponent, log_coefficient = np.polyfit(np.log(number_of_nodes_array[mask]), np.log(medians[mask]), 1)
            coefficient = float(np.exp(log_coefficient))
            exponent = float(exponent)

            fit = lambda number_of_nodes: coefficient * number_of_nodes ** exponent
            label = f'Fit: ${variable_symbol} = {coefficient:.3e} \\cdot n^{{{exponent:.3f}}}$ (log-linear)'

        else:
            power = float(fit_power)
            coefficient = np.dot(medians, number_of_nodes_array ** power) / np.dot(number_of_nodes_array ** power, number_of_nodes_array ** power)
            fit = lambda number_of_nodes: coefficient * number_of_nodes ** power
            label = f'Fit: ${variable_symbol} = {coefficient:.3e} \\cdot n^{{{power}}}$'

        degree = min(3, len(position_array) - 1)
        coefficients = np.polyfit(position_array, np.log(number_of_nodes_array), degree)
        fine_positions = np.linspace(position_array[0], position_array[-1], 500)
        fine_numbers_of_nodes = np.exp(np.polyval(coefficients, fine_positions))
        axis.plot(fine_positions, fit(fine_numbers_of_nodes), '--', color='red', linewidth=1.5, label=label, zorder=6)

    def ThinXAxisTicks(self, axis, positions, sorted_numbers_of_nodes, maximum_labels=20):
        axis.set_xticks(positions)
        stride = max(1, -(-len(positions) // maximum_labels))
        labels = [
            str(number_of_nodes) if i % stride == 0 else ''
            for i, number_of_nodes in enumerate(sorted_numbers_of_nodes)
        ]
        axis.set_xticklabels(labels)

    def PlotComputationTimeVersusNumberOfNodes(self):
        if not self.analysis_directory.is_dir():
            print(f'WARNING: Cannot locate {self.analysis_directory}, creating it...')
            os.makedirs(self.analysis_directory, exist_ok=True)
        if not self.run_directory.is_dir():
            print(f'ERROR: Cannot locate {self.run_directory}')
            return

        data_by_number_of_nodes = {}
        for instance_directory in self.run_directory.iterdir():
            if not instance_directory.is_dir():
                continue

            for run_file in instance_directory.iterdir():
                if not run_file.is_file() or run_file.suffix != '.txt':
                    continue
                try:
                    number_of_nodes = None
                    computation_time = None
                    with open(run_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('n:'):
                                number_of_nodes = int(line.split(':', 1)[1].strip())
                            elif line.startswith('computationTime:'):
                                computation_time = float(line.split(':', 1)[1].strip().rstrip('s'))
                    if number_of_nodes is not None and computation_time is not None:
                        data_by_number_of_nodes.setdefault(number_of_nodes, []).append(computation_time)

                except Exception as e:
                    print(e)

        if not data_by_number_of_nodes:
            print('No data found.')
            return

        sorted_numbers_of_nodes = sorted(data_by_number_of_nodes.keys())
        times_per_number_of_nodes = [data_by_number_of_nodes[number_of_nodes] for number_of_nodes in sorted_numbers_of_nodes]
        positions = list(range(1, len(sorted_numbers_of_nodes) + 1))
        number_of_nodes_array = np.array(sorted_numbers_of_nodes, dtype=float)
        position_array = np.array(positions, dtype=float)

        _, axis = plt.subplots(figsize=(10, 6))

        blue = (0.122, 0.467, 0.706)
        blue_fill = (0.122, 0.467, 0.706, 0.2)

        box_plot = axis.boxplot(
            times_per_number_of_nodes,
            positions=positions,
            widths=0.5,
            patch_artist=True,
            showfliers=True,
            medianprops=dict(linewidth=0),
        )

        for patch in box_plot['boxes']:
            patch.set_facecolor(blue_fill)
            patch.set_edgecolor(blue)
            patch.set_linewidth(1.5)
        for whisker in box_plot['whiskers']:
            whisker.set_color(blue)
            whisker.set_linewidth(1.5)
        for cap in box_plot['caps']:
            cap.set_color(blue)
            cap.set_linewidth(1.5)
        for flier in box_plot['fliers']:
            flier.set(marker='o', color=blue, alpha=0.5, markersize=4)

        medians = np.array([np.median(times) for times in times_per_number_of_nodes])
        axis.plot(positions, medians, 'o', color='#D4AC00', markersize=6, zorder=5, label='Median')
        axis.plot(positions, medians, '-', color='#D4AC00', linewidth=1.5, zorder=4)

        self.DrawFitCurve(axis, number_of_nodes_array, position_array, medians, self.computation_time_fit_power, variable_symbol='t')

        self.ThinXAxisTicks(axis, positions, sorted_numbers_of_nodes)
        axis.set_xlabel('n')
        axis.set_ylabel('Computation Time (s)')
        axis.set_title('Computation Time vs n')
        axis.legend()
        axis.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

        plt.tight_layout()
        plt.savefig(rf'{self.analysis_directory}\computation_time_vs_n.png')
        plt.close()

    def PlotPercentErrorVersusNumberOfNodes(self):
        if not self.analysis_directory.is_dir():
            print(f'WARNING: Cannot locate {self.analysis_directory}, creating it...')
            os.makedirs(self.analysis_directory, exist_ok=True)
        if not self.run_directory.is_dir():
            print(f'WARNING: Cannot locate {self.run_directory}, creating it...')
            os.makedirs(self.run_directory, exist_ok=True)
            return

        data_by_number_of_nodes = {}
        for instance_directory in self.run_directory.iterdir():
            if not instance_directory.is_dir():
                continue

            for run_file in instance_directory.iterdir():
                if not run_file.is_file() or run_file.suffix != '.txt':
                    continue
                try:
                    number_of_nodes = None
                    percent_error = None
                    with open(run_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('n:'):
                                number_of_nodes = int(line.split(':', 1)[1].strip())
                            elif line.startswith('percentError:'):
                                percent_error = float(line.split(':', 1)[1].strip())

                    if number_of_nodes is not None and percent_error is not None:
                        data_by_number_of_nodes.setdefault(number_of_nodes, []).append(percent_error)

                except Exception as e:
                    print(e)

        if not data_by_number_of_nodes:
            print('No data found.')
            return

        sorted_numbers_of_nodes = sorted(data_by_number_of_nodes.keys())
        errors_per_number_of_nodes = [data_by_number_of_nodes[number_of_nodes] for number_of_nodes in sorted_numbers_of_nodes]
        positions = list(range(1, len(sorted_numbers_of_nodes) + 1))
        number_of_nodes_array = np.array(sorted_numbers_of_nodes, dtype=float)
        position_array = np.array(positions, dtype=float)

        _, axis = plt.subplots(figsize=(10, 6))

        blue = (0.122, 0.467, 0.706)
        blue_fill = (0.122, 0.467, 0.706, 0.2)

        box_plot = axis.boxplot(
            errors_per_number_of_nodes,
            positions=positions,
            widths=0.5,
            patch_artist=True,
            showfliers=True,
            medianprops=dict(linewidth=0),
        )

        for patch in box_plot['boxes']:
            patch.set_facecolor(blue_fill)
            patch.set_edgecolor(blue)
            patch.set_linewidth(1.5)
        for whisker in box_plot['whiskers']:
            whisker.set_color(blue)
            whisker.set_linewidth(1.5)
        for cap in box_plot['caps']:
            cap.set_color(blue)
            cap.set_linewidth(1.5)
        for flier in box_plot['fliers']:
            flier.set(marker='o', color=blue, alpha=0.5, markersize=4)

        medians = np.array([np.median(errors) for errors in errors_per_number_of_nodes])
        axis.plot(positions, medians, 'o', color='#D4AC00', markersize=6, zorder=5, label='Median')
        axis.plot(positions, medians, '-', color='#D4AC00', linewidth=1.5, zorder=4)

        self.DrawFitCurve(axis, number_of_nodes_array, position_array, medians, self.percent_error_fit_power, variable_symbol='e')

        self.ThinXAxisTicks(axis, positions, sorted_numbers_of_nodes)
        axis.set_xlabel('n')
        axis.set_ylabel('Percent Error (%)')
        axis.set_title('Percent Error vs n')
        axis.legend()
        axis.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

        plt.tight_layout()
        plt.savefig(rf'{self.analysis_directory}\percent-error-vs-n.png')
        plt.close()

    def ParseTour(self, run_file):
        indices = []
        is_in_tour = False
        with open(run_file, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('tour:'):
                    is_in_tour = True
                    continue

                if not is_in_tour:
                    continue

                if not stripped:
                    if indices:
                        break
                    continue

                cleaned = stripped.replace('[', '').replace(']', '')
                for token in cleaned.split():
                    try:
                        indices.append(int(token))
                    except ValueError:
                        is_in_tour = False
                        break

                if stripped.endswith(']'):
                    break

        return np.array(indices, dtype=int)

    def PlotTour(self, instance_name, run_index=0):
        if not self.analysis_directory.is_dir():
            print(f'WARNING: Cannot locate {self.analysis_directory}, creating it...')
            os.makedirs(self.analysis_directory, exist_ok=True)

        instance_file = self.instance_directory / f'{instance_name}.tsp'
        run_file = self.run_directory / instance_name / f'{instance_name}_{run_index}.txt'

        if not instance_file.is_file():
            print(f'Cannot locate {instance_file}')
            return

        if not run_file.is_file():
            print(f'Cannot locate {run_file}')
            return

        try:
            instance = tsplib95.load(instance_file)
            if instance.edge_weight_type != 'EUC_2D':
                print(f'{instance_name} is not EUC_2D')
                return

            coordinates = np.array(list(instance.node_coords.values()))
            tour = self.ParseTour(run_file)
            if tour.size == 0:
                print(f'No tour found in {run_file}')
                return

            elite_fitness = None
            percent_error = None
            with open(run_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('eliteFit:'):
                        elite_fitness = float(line.split(':', 1)[1].strip())
                    elif line.startswith('percentError:'):
                        percent_error = float(line.split(':', 1)[1].strip())

            cycle = np.append(tour, tour[0])
            x = coordinates[cycle, 0]
            y = coordinates[cycle, 1]

            _, axis = plt.subplots(figsize=(8, 8))
            axis.plot(x, y, color=(0.894, 0.102, 0.110), linewidth=1.0, zorder=3)
            axis.scatter(coordinates[:, 0], coordinates[:, 1], color=(0.122, 0.467, 0.706), s=15, zorder=2, alpha=0.4)
            axis.axis('equal')

            title = f'{instance_name} tour, run {run_index}, n = {coordinates.shape[0]}'
            if elite_fitness is not None and percent_error is not None:
                title += f'\nelite = {elite_fitness:.0f}, percent error = {percent_error:.3f}%'
            axis.set_title(title)
            axis.set_xlabel('X-Coordinate')
            axis.set_ylabel('Y-Coordinate')
            axis.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)

            plt.tight_layout()
            plt.savefig(rf'{self.analysis_directory}\{instance_name}-tour-{run_index}.png')
            plt.close()

        except Exception as e:
            print(e)

    def ParseConvergence(self, run_file):
        generations = []
        errors = []
        is_in_data = False
        with open(run_file, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('genTime, gen, eliteFit, percentError:'):
                    is_in_data = True
                    continue
                if not is_in_data:
                    continue
                if stripped.startswith('tour:'):
                    break
                if not stripped:
                    continue
                parts = stripped.split(',')
                if len(parts) < 4:
                    break
                try:
                    generation_number = int(parts[1].strip())
                    error = parts[3].strip()
                    if error == 'N/A':
                        continue
                    generations.append(generation_number)
                    errors.append(float(error))
                except ValueError:
                    break
        return np.array(generations, dtype=int), np.array(errors, dtype=float)

    def PlotConvergence(self, instance_name, run_index=0):
        if not self.analysis_directory.is_dir():
            print(f'WARNING: Cannot locate {self.analysis_directory}, creating it...')
            os.makedirs(self.analysis_directory, exist_ok=True)

        run_file = self.run_directory / instance_name / f'{instance_name}_{run_index}.txt'
        if not run_file.is_file():
            print(f'Cannot locate {run_file}')
            return

        try:
            generations, errors = self.ParseConvergence(run_file)
            mask = generations != 0
            generations, errors = generations[mask], errors[mask]
            if generations.size == 0:
                print(f'No convergence data found in {run_file}')
                return

            _, axis = plt.subplots(figsize=(10, 5))
            axis.plot(generations, errors, color=(0.122, 0.467, 0.706), linewidth=1.5)
            axis.set_xlabel('Generation')
            axis.set_ylabel('Percent Error (%)')
            axis.set_title(f'{instance_name} convergence, run {run_index}')
            axis.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
            plt.tight_layout()
            plt.savefig(rf'{self.analysis_directory}\{instance_name}-convergence-{run_index}.png')
            plt.close()

        except Exception as e:
            print(e)

    def PlotAggregateConvergence(self):
        if not self.analysis_directory.is_dir():
            print(f'WARNING: Cannot locate {self.analysis_directory}, creating it...')
            os.makedirs(self.analysis_directory, exist_ok=True)

        if not self.run_directory.is_dir():
            print(f'Cannot locate {self.run_directory}')
            return

        try:
            all_curves = []
            for instance_directory in self.run_directory.iterdir():
                if not instance_directory.is_dir():
                    continue
                for run_file in instance_directory.iterdir():
                    if not run_file.is_file() or run_file.suffix != '.txt':
                        continue
                    generations, errors = self.ParseConvergence(run_file)
                    mask = generations != 0
                    generations, errors = generations[mask], errors[mask]
                    if generations.size == 0:
                        continue
                    all_curves.append((generations, errors))

            all_curves = [(g, e) for g, e in all_curves if len(e) >= 2]

            if not all_curves:
                print(f'No convergence data found in {self.run_directory}')
                return

            common_x_values = np.linspace(0, 1, 200)
            interpolated_errors = []
            for curve_generations, curve_errors in all_curves:
                normalized_x_values = (curve_generations - curve_generations[0]) / (curve_generations[-1] - curve_generations[0])
                interpolated_errors.append(np.interp(common_x_values, normalized_x_values, curve_errors))
            generations = common_x_values
            matrix = np.array(interpolated_errors)

            first_quartile = np.percentile(matrix, 25, axis=0)
            third_quartile = np.percentile(matrix, 75, axis=0)
            interquartile_range = third_quartile - first_quartile
            upper_whisker = third_quartile + 1.5 * interquartile_range
            lower_whisker = first_quartile - 1.5 * interquartile_range

            outlier_mask = np.any((matrix > upper_whisker) | (matrix < lower_whisker), axis=1)
            outlier_curves = matrix[outlier_mask]
            inlier_curves = matrix[~outlier_mask]

            if inlier_curves.shape[0] >= 2:
                first_quartile = np.percentile(inlier_curves, 25, axis=0)
                third_quartile = np.percentile(inlier_curves, 75, axis=0)
                median = np.median(inlier_curves, axis=0)
            else:
                median = np.median(matrix, axis=0)

            _, axis = plt.subplots(figsize=(10, 5))

            if self.can_show_aggregate_convergence:
                for curve in outlier_curves:
                    axis.plot(generations, curve, color=(0.5, 0.5, 0.5), linewidth=0.8, alpha=0.15, zorder=1)
                for curve in inlier_curves:
                    axis.plot(generations, curve, color=(0.5, 0.5, 0.5), linewidth=0.8, alpha=0.15, zorder=1)

            if self.can_show_aggregate_convergence_statistics:
                axis.plot(generations, first_quartile, color='red', linewidth=1.0, linestyle='--', label='Q1 / Q3', zorder=3)
                axis.plot(generations, third_quartile, color='red', linewidth=1.0, linestyle='--', zorder=3)
                axis.plot(generations, median, color='red', linewidth=1.5, label='Median', zorder=4)

            axis.set_xlabel('Normalized Generation')
            axis.set_ylabel('Percent Error (%)')
            axis.set_title(f'aggregate convergence ({matrix.shape[0]} runs)')
            if self.can_show_aggregate_convergence_statistics:
                axis.legend()
            axis.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

            plt.tight_layout()
            plt.savefig(rf'{self.analysis_directory}\convergence-aggregate.png')
            plt.close()

        except Exception as e:
            print(e)

    def PlotHeatMap(self, instance_name):
        if not self.analysis_directory.is_dir():
            print(f'WARNING: Cannot locate {self.analysis_directory}, creating it...')
            os.makedirs(self.analysis_directory, exist_ok=True)

        instance_file = self.instance_directory / f'{instance_name}.tsp'
        run_directory = self.run_directory / instance_name

        if not instance_file.is_file():
            print(f'WARNING: Cannot locate {instance_file}, creating it...')
            return
        if not run_directory.is_dir():
            print(f'WARNING: Cannot locate {run_directory}, creating it...')
            os.makedirs(run_directory, exist_ok=True)

        try:
            instance = tsplib95.load(instance_file)
            if instance.edge_weight_type != 'EUC_2D':
                print(f'{instance_name} is not EUC_2D')
                return

            coordinates = np.array(list(instance.node_coords.values()))
            edge_counts = {}
            number_of_tours = 0

            for run_file in run_directory.iterdir():
                if not run_file.is_file() or run_file.suffix != '.txt':
                    continue

                tour = self.ParseTour(run_file)
                if tour.size == 0:
                    continue

                number_of_tours += 1
                cycle = np.append(tour, tour[0])
                for i in range(len(tour)):
                    node_1, node_2 = int(cycle[i]), int(cycle[i + 1])
                    key = (node_1, node_2) if node_1 < node_2 else (node_2, node_1)
                    edge_counts[key] = edge_counts.get(key, 0) + 1

            if number_of_tours == 0:
                print(f'No tours found in {run_directory}')
                return

            _, axis = plt.subplots(figsize=(10, 8))
            color_map = plt.get_cmap('YlOrRd')

            for (node_1, node_2), count in sorted(edge_counts.items(), key=lambda kv: kv[1]):
                frequency = count / number_of_tours
                axis.plot(
                    [coordinates[node_1, 0], coordinates[node_2, 0]],
                    [coordinates[node_1, 1], coordinates[node_2, 1]],
                    color=color_map(frequency),
                    linewidth=0.5 + 2.0 * frequency,
                    alpha=0.3 + 0.7 * frequency,
                    zorder=3,
                )

            axis.scatter(coordinates[:, 0], coordinates[:, 1], c='black', s=10, zorder=2)
            axis.axis('equal')
            axis.set_title(f'{instance_name} edge heat map across {number_of_tours} trials, n = {coordinates.shape[0]}')
            axis.set_xlabel('X-Coordinate')
            axis.set_ylabel('Y-Coordinate')

            scalar_mappable = plt.cm.ScalarMappable(cmap=color_map, norm=plt.Normalize(vmin=0, vmax=1))
            scalar_mappable.set_array([])
            color_bar = plt.colorbar(scalar_mappable, ax=axis)
            color_bar.set_label('Edge usage frequency')

            plt.tight_layout()
            plt.savefig(rf'{self.analysis_directory}\{instance_name}_heatmap.png')
            plt.close()

        except Exception as e:
            print(e)