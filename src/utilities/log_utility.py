import numpy as np
import sys



class Log:
    def __init__(self, logFile):
        self.logFile = logFile

    def logStart(self, instance):
        print(
            f'\nInstance ({instance.edgeWeightType}): {instance.instanceName}'
            f'\nNumber of nodes (n): {instance.n}'
            f'\nOptimal tour distance (fitness): {instance.optFit}'
            '\nCompiling and initializing GA...'
            '\n'
        )

        with open(self.logFile, 'w', newline='') as a:
            a.write(
                f'instanceName: {instance.instanceName}'
                f'\nn: {instance.n}'
                f'\noptFit: {instance.optFit}'
                '\n'
                '\ngenTime, gen, eliteFit, percentError:'
            )



    def logGen(self, genTime, gen, eliteFit, percentError):
        errorStr = f'{percentError:.3f}%' if percentError is not None else 'N/A'
        print(
            f'Gen. Time: {genTime:.3f}s, '
            f'Gen.: {gen}, '
            f'Elite: {eliteFit}, '
            f'% Error: {errorStr}'
        )

        errorVal = f'{percentError:.3f}' if percentError is not None else 'N/A'
        with open(self.logFile, 'a', newline='') as a:
            a.write(f'\n{genTime}, {gen}, {eliteFit}, {errorVal}')



    def logEnd(self, eliteFit, optFit, percentError, endTime, startTime, tour):
        errorStr = f'{percentError:.3f}%' if percentError is not None else 'N/A'
        print(
            f'\nElite tour distance (fitness): {eliteFit}'
            f'\nOptimal tour distance (fitness): {optFit}'
            f'\nPercent Error (%): {errorStr}'
            f'\nComputation Time (seconds): {endTime - startTime:.3f}s'
            '\n'
        )

        fullTour = np.array2string(tour, threshold=sys.maxsize)
        with open(self.logFile, 'a', newline='') as a:
            a.write(
                '\n'
                f'\ntour:\n{fullTour}'
                '\n'
                f'\neliteFit: {eliteFit}'
                f'\npercentError: {percentError}'
                f'\ncomputationTime: {endTime - startTime:.3f}s'
            )