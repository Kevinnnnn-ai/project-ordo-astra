import os
import numpy as np
import matplotlib.pyplot as plt
import tsplib95
from pathlib import Path



class Plot:
    def __init__(self):
        self.rootDir = Path(__file__).resolve().parents[2]
        self.instanceDir = self.rootDir / 'res' / 'tsplib' / 'tsp'
        self.instPlotDir = self.rootDir / 'stdout' / 'instance-plots'
        self.runDir = self.rootDir / 'stdout' / 'runs'
        self.analysisDir = self.rootDir / 'stdout' / 'analysis'

        self.errVsNFit = 'log-linear'
        self.compTimeVsNFit = 'log-linear'
        self.canShowAggConverge = True
        self.canShowAggConvergeStats = True



    def plotEuc2DInstances(self):
        if not self.instPlotDir.is_dir():
            print(f'WARNING: Cannot locate {self.instPlotDir}')
            os.makedirs(self.instPlotDir, exist_ok=True)
            return
        if not self.instanceDir.is_dir():
            print(f'ERROR: Cannot locate {self.instanceDir}')
            return

        for instanceFile in self.instanceDir.iterdir():
            if instanceFile.is_file() and (instanceFile.suffix == '.tsp'):
                try:
                    instance = tsplib95.load(instanceFile)
                    if instance.edge_weight_type == 'EUC_2D':
                        nodes = instance.node_coords.values()
                        coords = np.array(list(nodes))
                        x = coords[:, 0]
                        y = coords[:, 1]

                        plt.clf()
                        plt.scatter(x, y, marker='o', c='blue', s=5)
                        plt.axis('equal')

                        name = instance.name
                        n = len(coords)
                        plt.title(f'{name}, n = {n}, 2D Euclidean TSP')
                        plt.xlabel('X-Coordinate')
                        plt.ylabel('Y-Coordinate')

                        plt.savefig(rf'{self.instPlotDir}\{name}.png')
                        plt.close()

                except Exception as e:
                    print(e)

                    if not self.runDir.is_dir():
                        print(f'Cannot locate {self.runDir}')
                        return



    def _drawFitCurve(self, ax, nArr, posArr, medians, fitPower, var):
        if fitPower == 'log-linear':
            mask = medians > 0
            if mask.sum() < 2:
                print('Skipping log-linear fit: need at least 2 positive medians.')
                return

            b, logC = np.polyfit(np.log(nArr[mask]), np.log(medians[mask]), 1)
            c = float(np.exp(logC))
            b = float(b)

            fit = lambda n: c * n ** b
            label = f'Fit: ${var} = {c:.3e} \\cdot n^{{{b:.3f}}}$ (log-linear)'

        else:
            p = float(fitPower)
            a = np.dot(medians, nArr ** p) / np.dot(nArr ** p, nArr ** p)
            fit = lambda n: a * n ** p
            label = f'Fit: ${var} = {a:.3e} \\cdot n^{{{p}}}$'

        deg = min(3, len(posArr) - 1)
        coefs = np.polyfit(posArr, np.log(nArr), deg)
        posFine = np.linspace(posArr[0], posArr[-1], 500)
        nFine = np.exp(np.polyval(coefs, posFine))
        ax.plot(posFine, fit(nFine), '--', color='red', linewidth=1.5, label=label, zorder=6)



    def _thinXTicks(self, ax, positions, sortedN, maxLabels=20):
        ax.set_xticks(positions)
        stride = max(1, -(-len(positions) // maxLabels))
        labels = [
            str(n) if i % stride == 0 else ''
            for i, n in enumerate(sortedN)
        ]
        ax.set_xticklabels(labels)



    def plotComputationTimeVsN(self):
        if not self.analysisDir.is_dir():
            print(f'WARNING: Cannot locate {self.analysisDir}, creating it...')
            os.makedirs(self.analysisDir, exist_ok=True)
        if not self.runDir.is_dir():
            print(f'ERROR: Cannot locate {self.runDir}')
            return

        dataByN = {}
        for instanceDir in self.runDir.iterdir():
            if not instanceDir.is_dir():
                continue

            for runFile in instanceDir.iterdir():
                if not runFile.is_file() or runFile.suffix != '.txt':
                    continue
                try:
                    n = None
                    compTime = None
                    with open(runFile, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('n:'):
                                n = int(line.split(':', 1)[1].strip())
                            elif line.startswith('computationTime:'):
                                compTime = float(line.split(':', 1)[1].strip().rstrip('s'))
                    if n is not None and compTime is not None:
                        dataByN.setdefault(n, []).append(compTime)

                except Exception as e:
                    print(e)

        if not dataByN:
            print('No data found.')
            return

        sortedN = sorted(dataByN.keys())
        timePerN = [dataByN[n] for n in sortedN]
        positions = list(range(1, len(sortedN) + 1))
        nArr = np.array(sortedN, dtype=float)
        posArr = np.array(positions, dtype=float)

        _, ax = plt.subplots(figsize=(10, 6))

        blue = (0.122, 0.467, 0.706)
        blueFill = (0.122, 0.467, 0.706, 0.2)

        bp = ax.boxplot(
            timePerN,
            positions=positions,
            widths=0.5,
            patch_artist=True,
            showfliers=True,
            medianprops=dict(linewidth=0),
        )

        for patch in bp['boxes']:
            patch.set_facecolor(blueFill)
            patch.set_edgecolor(blue)
            patch.set_linewidth(1.5)
        for whisker in bp['whiskers']:
            whisker.set_color(blue)
            whisker.set_linewidth(1.5)
        for cap in bp['caps']:
            cap.set_color(blue)
            cap.set_linewidth(1.5)
        for flier in bp['fliers']:
            flier.set(marker='o', color=blue, alpha=0.5, markersize=4)

        medians = np.array([np.median(t) for t in timePerN])
        ax.plot(positions, medians, 'o', color='#D4AC00', markersize=6, zorder=5, label='Median')
        ax.plot(positions, medians, '-', color='#D4AC00', linewidth=1.5, zorder=4)

        self._drawFitCurve(ax, nArr, posArr, medians, self.compTimeVsNFit, var='t')

        self._thinXTicks(ax, positions, sortedN)
        ax.set_xlabel('n')
        ax.set_ylabel('Computation Time (s)')
        ax.set_title('Computation Time vs n')
        ax.legend()
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

        plt.tight_layout()
        plt.savefig(rf'{self.analysisDir}\computation_time_vs_n.png')
        plt.close()



    def plotPercentErrorVsN(self):
        if not self.analysisDir.is_dir():
            print(f'WARNING: Cannot locate {self.analysisDir}, creating it...')
            os.makedirs(self.analysisDir, exist_ok=True)
        if not self.runDir.is_dir():
            print(f'WARNING: Cannot locate {self.runDir}, creating it...')
            os.makedirs(self.runDir, exist_ok=True)
            return

        dataByN = {}
        for instanceDir in self.runDir.iterdir():
            if not instanceDir.is_dir():
                continue

            for runFile in instanceDir.iterdir():
                if not runFile.is_file() or runFile.suffix != '.txt':
                    continue
                try:
                    n = None
                    percentError = None
                    with open(runFile, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('n:'):
                                n = int(line.split(':', 1)[1].strip())
                            elif line.startswith('percentError:'):
                                percentError = float(line.split(':', 1)[1].strip())

                    if n is not None and percentError is not None:
                        dataByN.setdefault(n, []).append(percentError)

                except Exception as e:
                    print(e)

        if not dataByN:
            print('No data found.')
            return

        sortedN = sorted(dataByN.keys())
        timePerN = [dataByN[n] for n in sortedN]
        positions = list(range(1, len(sortedN) + 1))
        nArr = np.array(sortedN, dtype=float)
        posArr = np.array(positions, dtype=float)

        _, ax = plt.subplots(figsize=(10, 6))

        blue = (0.122, 0.467, 0.706)
        blueFill = (0.122, 0.467, 0.706, 0.2)

        bp = ax.boxplot(
            timePerN,
            positions=positions,
            widths=0.5,
            patch_artist=True,
            showfliers=True,
            medianprops=dict(linewidth=0),
        )

        for patch in bp['boxes']:
            patch.set_facecolor(blueFill)
            patch.set_edgecolor(blue)
            patch.set_linewidth(1.5)
        for whisker in bp['whiskers']:
            whisker.set_color(blue)
            whisker.set_linewidth(1.5)
        for cap in bp['caps']:
            cap.set_color(blue)
            cap.set_linewidth(1.5)
        for flier in bp['fliers']:
            flier.set(marker='o', color=blue, alpha=0.5, markersize=4)

        medians = np.array([np.median(t) for t in timePerN])
        ax.plot(positions, medians, 'o', color='#D4AC00', markersize=6, zorder=5, label='Median')
        ax.plot(positions, medians, '-', color='#D4AC00', linewidth=1.5, zorder=4)

        self._drawFitCurve(ax, nArr, posArr, medians, self.errVsNFit, var='e')

        self._thinXTicks(ax, positions, sortedN)
        ax.set_xlabel('n')
        ax.set_ylabel('Percent Error (%)')
        ax.set_title('Percent Error vs n')
        ax.legend()
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

        plt.tight_layout()
        plt.savefig(rf'{self.analysisDir}\percent-error-vs-n.png')
        plt.close()



    def _parseTour(self, runFile):
        indices = []
        isInTour = False
        with open(runFile, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('tour:'):
                    isInTour = True
                    continue

                if not isInTour:
                    continue

                if not stripped:
                    if indices:
                        break
                    continue

                cleaned = stripped.replace('[', '').replace(']', '')
                for tok in cleaned.split():
                    try:
                        indices.append(int(tok))
                    except ValueError:
                        isInTour = False
                        break

                if stripped.endswith(']'):
                    break

        return np.array(indices, dtype=int)



    def plotTour(self, instanceName, runIdx=0):
        if not self.analysisDir.is_dir():
            print(f'WARNING: Cannot locate {self.analysisDir}, creating it...')
            os.makedirs(self.analysisDir, exist_ok=True)

        instanceFile = self.instanceDir / f'{instanceName}.tsp'
        runFile = self.runDir / instanceName / f'{instanceName}_{runIdx}.txt'

        if not instanceFile.is_file():
            print(f'Cannot locate {instanceFile}')
            return

        if not runFile.is_file():
            print(f'Cannot locate {runFile}')
            return

        try:
            instance = tsplib95.load(instanceFile)
            if instance.edge_weight_type != 'EUC_2D':
                print(f'{instanceName} is not EUC_2D')
                return

            coords = np.array(list(instance.node_coords.values()))
            tour = self._parseTour(runFile)
            if tour.size == 0:
                print(f'No tour found in {runFile}')
                return

            elite = None
            percent = None
            with open(runFile, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('eliteFit:'):
                        elite = float(line.split(':', 1)[1].strip())
                    elif line.startswith('percentError:'):
                        percent = float(line.split(':', 1)[1].strip())

            cycle = np.append(tour, tour[0])
            x = coords[cycle, 0]
            y = coords[cycle, 1]

            _, ax = plt.subplots(figsize=(8, 8))
            ax.plot(x, y, color=(0.894, 0.102, 0.110), linewidth=1.0, zorder=3)
            ax.scatter(coords[:, 0], coords[:, 1], color=(0.122, 0.467, 0.706), s=15, zorder=2, alpha=0.4)
            ax.axis('equal')

            title = f'{instanceName} tour, run {runIdx}, n = {coords.shape[0]}'
            if elite is not None and percent is not None:
                title += f'\nelite = {elite:.0f}, percent error = {percent:.3f}%'
            ax.set_title(title)
            ax.set_xlabel('X-Coordinate')
            ax.set_ylabel('Y-Coordinate')
            ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)

            plt.tight_layout()
            plt.savefig(rf'{self.analysisDir}\{instanceName}-tour-{runIdx}.png')
            plt.close()

        except Exception as e:
            print(e)



    def _parseConvergence(self, runFile):
        gens = []
        errors = []
        isInData = False
        with open(runFile, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('genTime, gen, eliteFit, percentError:'):
                    isInData = True
                    continue
                if not isInData:
                    continue
                if stripped.startswith('tour:'):
                    break
                if not stripped:
                    continue
                parts = stripped.split(',')
                if len(parts) < 4:
                    break
                try:
                    gen = int(parts[1].strip())
                    err = parts[3].strip()
                    if err == 'N/A':
                        continue
                    gens.append(gen)
                    errors.append(float(err))
                except ValueError:
                    break
        return np.array(gens, dtype=int), np.array(errors, dtype=float)



    def plotConvergence(self, instanceName, runIdx=0):
        if not self.analysisDir.is_dir():
            print(f'WARNING: Cannot locate {self.analysisDir}, creating it...')
            os.makedirs(self.analysisDir, exist_ok=True)

        runFile = self.runDir / instanceName / f'{instanceName}_{runIdx}.txt'
        if not runFile.is_file():
            print(f'Cannot locate {runFile}')
            return

        try:
            gens, errors = self._parseConvergence(runFile)
            mask = gens != 0
            gens, errors = gens[mask], errors[mask]
            if gens.size == 0:
                print(f'No convergence data found in {runFile}')
                return

            _, ax = plt.subplots(figsize=(10, 5))
            ax.plot(gens, errors, color=(0.122, 0.467, 0.706), linewidth=1.5)
            ax.set_xlabel('Generation')
            ax.set_ylabel('Percent Error (%)')
            ax.set_title(f'{instanceName} convergence, run {runIdx}')
            ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
            plt.tight_layout()
            plt.savefig(rf'{self.analysisDir}\{instanceName}-convergence-{runIdx}.png')
            plt.close()

        except Exception as e:
            print(e)



    def plotAggConvergence(self):
        if not self.analysisDir.is_dir():
            print(f'WARNING: Cannot locate {self.analysisDir}, creating it...')
            os.makedirs(self.analysisDir, exist_ok=True)

        if not self.runDir.is_dir():
            print(f'Cannot locate {self.runDir}')
            return

        try:
            allCurves = []
            for instanceDir in self.runDir.iterdir():
                if not instanceDir.is_dir():
                    continue
                for runFile in instanceDir.iterdir():
                    if not runFile.is_file() or runFile.suffix != '.txt':
                        continue
                    gens, errors = self._parseConvergence(runFile)
                    mask = gens != 0
                    gens, errors = gens[mask], errors[mask]
                    if gens.size == 0:
                        continue
                    allCurves.append((gens, errors))

            allCurves = [(g, e) for g, e in allCurves if len(e) >= 2]

            if not allCurves:
                print(f'No convergence data found in {self.runDir}')
                return

            xCommon = np.linspace(0, 1, 200)
            interpErrors = []
            for g, e in allCurves:
                xNorm = (g - g[0]) / (g[-1] - g[0])
                interpErrors.append(np.interp(xCommon, xNorm, e))
            gens = xCommon
            matrix = np.array(interpErrors)

            q1 = np.percentile(matrix, 25, axis=0)
            q3 = np.percentile(matrix, 75, axis=0)
            iqr = q3 - q1
            whiskerUpper = q3 + 1.5 * iqr
            whiskerLower = q1 - 1.5 * iqr

            outlierMask = np.any((matrix > whiskerUpper) | (matrix < whiskerLower), axis=1)
            outlierCurves = matrix[outlierMask]
            inlierCurves = matrix[~outlierMask]

            if inlierCurves.shape[0] >= 2:
                q1 = np.percentile(inlierCurves, 25, axis=0)
                q3 = np.percentile(inlierCurves, 75, axis=0)
                median = np.median(inlierCurves, axis=0)
            else:
                median = np.median(matrix, axis=0)

            _, ax = plt.subplots(figsize=(10, 5))

            if self.canShowAggConverge:
                for curve in outlierCurves:
                    ax.plot(gens, curve, color=(0.5, 0.5, 0.5), linewidth=0.8, alpha=0.15, zorder=1)
                for curve in inlierCurves:
                    ax.plot(gens, curve, color=(0.5, 0.5, 0.5), linewidth=0.8, alpha=0.15, zorder=1)

            if self.canShowAggConvergeStats:
                ax.plot(gens, q1, color='red', linewidth=1.0, linestyle='--', label='Q1 / Q3', zorder=3)
                ax.plot(gens, q3, color='red', linewidth=1.0, linestyle='--', zorder=3)
                ax.plot(gens, median, color='red', linewidth=1.5, label='Median', zorder=4)

            ax.set_xlabel('Normalized Generation')
            ax.set_ylabel('Percent Error (%)')
            ax.set_title(f'aggregate convergence ({matrix.shape[0]} runs)')
            if self.canShowAggConvergeStats:
                ax.legend()
            ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

            plt.tight_layout()
            plt.savefig(rf'{self.analysisDir}\convergence-aggregate.png')
            plt.close()

        except Exception as e:
            print(e)



    def plotHeatMap(self, instanceName):
        if not self.analysisDir.is_dir():
            print(f'WARNING: Cannot locate {self.analysisDir}, creating it...')
            os.makedirs(self.analysisDir, exist_ok=True)

        instanceFile = self.instanceDir / f'{instanceName}.tsp'
        runDir = self.runDir / instanceName

        if not instanceFile.is_file():
            print(f'WARNING: Cannot locate {instanceFile}, creating it...')
            return
        if not runDir.is_dir():
            print(f'WARNING: Cannot locate {runDir}, creating it...')
            os.makedirs(runDir, exist_ok=True)

        try:
            instance = tsplib95.load(instanceFile)
            if instance.edge_weight_type != 'EUC_2D':
                print(f'{instanceName} is not EUC_2D')
                return

            coords = np.array(list(instance.node_coords.values()))
            edgeCounts = {}
            numOfTours = 0

            for runFile in runDir.iterdir():
                if not runFile.is_file() or runFile.suffix != '.txt':
                    continue

                tour = self._parseTour(runFile)
                if tour.size == 0:
                    continue

                numOfTours += 1
                cycle = np.append(tour, tour[0])
                for i in range(len(tour)):
                    a, b = int(cycle[i]), int(cycle[i + 1])
                    key = (a, b) if a < b else (b, a)
                    edgeCounts[key] = edgeCounts.get(key, 0) + 1

            if numOfTours == 0:
                print(f'No tours found in {runDir}')
                return

            _, ax = plt.subplots(figsize=(10, 8))
            cmap = plt.get_cmap('YlOrRd')

            for (a, b), count in sorted(edgeCounts.items(), key=lambda kv: kv[1]):
                freq = count / numOfTours
                ax.plot(
                    [coords[a, 0], coords[b, 0]],
                    [coords[a, 1], coords[b, 1]],
                    color=cmap(freq),
                    linewidth=0.5 + 2.0 * freq,
                    alpha=0.3 + 0.7 * freq,
                    zorder=3,
                )

            ax.scatter(coords[:, 0], coords[:, 1], c='black', s=10, zorder=2)
            ax.axis('equal')
            ax.set_title(f'{instanceName} edge heat map across {numOfTours} trials, n = {coords.shape[0]}')
            ax.set_xlabel('X-Coordinate')
            ax.set_ylabel('Y-Coordinate')

            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=1))
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_label('Edge usage frequency')

            plt.tight_layout()
            plt.savefig(rf'{self.analysisDir}\{instanceName}_heatmap.png')
            plt.close()

        except Exception as e:
            print(e)