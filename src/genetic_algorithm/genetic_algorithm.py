from ..utils.log_util import Log

import numpy as np
import numba
import os
from pathlib import Path
from scipy.spatial.distance import cdist
from time import perf_counter



POP_SIZE = 200
MAX_GENS = 1000
SELECTION_SIZE = 7
OX_RATE = 0.85
SWAP_MUT_RATE = 0.03
MIN_CHANGE = 1e-3
CONVERGENCE_GEN = 50
TWO_OPT_PERCENTILE = 10

NO_GIL = True
CAN_PARALLEL = True
CAN_CACHE = True

ROOT_DIR = Path(__file__).resolve().parents[2]



@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def _createTour(n):
    tour = np.arange(n)
    np.random.shuffle(tour)
    return tour



@numba.njit(parallel=CAN_PARALLEL, nogil=NO_GIL, cache=CAN_CACHE)
def _createPop(popSize, n):
    pop = np.empty((popSize, n), dtype=np.int64)
    for i in numba.prange(popSize):
        pop[i] = _createTour(n)
    return pop



@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def _calcFit(n, tour, distMatrix):
    fit = 0.0
    for i in range(n - 1):
        fit += distMatrix[tour[i], tour[i + 1]]
    fit += distMatrix[tour[-1], tour[0]]
    return fit



@numba.njit(parallel=CAN_PARALLEL, nogil=NO_GIL, cache=CAN_CACHE)
def _calcFits(popSize, n, pop, distMatrix):
    fits = np.empty(popSize, dtype=np.float64)
    for i in numba.prange(popSize):
        fits[i] = _calcFit(n, pop[i], distMatrix)
    return fits



@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def _runSelection(fits, selectionSize):
    elite = np.random.randint(len(fits))
    eliteFit = fits[elite]
    for i in range(1, selectionSize):
        tour = np.random.randint(len(fits))
        if fits[tour] < eliteFit:
            eliteFit = fits[tour]
            elite = tour
    return elite



@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def _runOX(oxRate, parent1, parent2, n):
    if np.random.random() <= oxRate:
        a = np.random.randint(n)
        b = np.random.randint(n)
        while a == b:
            b = np.random.randint(n)
        if a > b:
            a, b = b, a

        child = np.full(n, -1, dtype=np.int64)
        child[a : b] = parent1[a : b]

        fill = []
        subset = set(parent1[a : b])
        for i in parent2:
            if i not in subset:
                fill.append(i)

        j = 0
        for i in range(n):
            if child[i] == -1:
                child[i] = fill[j]
                j += 1
        return child

    else:
        if np.random.random() < 0.5:
            return parent2.copy()
        return parent1.copy()



@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def _runSwapMut(swapMutRate, tour, n):
    if np.random.random() < swapMutRate:
        mutated = tour.copy()
        a = np.random.randint(n)
        b = np.random.randint(n)
        while a == b:
            b = np.random.randint(n)
        mutated[a], mutated[b] = mutated[b], mutated[a]
        return mutated
    return tour



@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def _getElite(fits, pop):
    elite = np.argmin(fits)
    eliteTour = pop[elite].copy()
    eliteFit = np.float64(fits[elite])
    return eliteTour, eliteFit



@numba.njit(parallel=CAN_PARALLEL, nogil=NO_GIL, cache=CAN_CACHE)
def _createPops(popSize, fits, selectionSize, pop, oxRate, swapMutRate, n):
    newPop = np.empty((popSize - 1, n), dtype=np.int64)

    for i in numba.prange(1, popSize):
        a = _runSelection(fits, selectionSize)
        b = _runSelection(fits, selectionSize)
        while b == a:
            b = _runSelection(fits, selectionSize)
        parent1 = pop[a]
        parent2 = pop[b]

        newPop[i - 1] = _runOX(oxRate, parent1, parent2, n)
        newPop[i - 1] = _runSwapMut(swapMutRate, newPop[i - 1], n)
    return newPop



@numba.njit(parallel=CAN_PARALLEL, nogil=NO_GIL, cache=CAN_CACHE)
def _runTwoOptTopK(count, pop, fits, distMatrix, n, threshold):
    for i in numba.prange(count):
        if fits[i] <= threshold:
            pop[i] = _runTwoOpt(n, pop[i], distMatrix)
            fits[i] = _calcFit(n, pop[i], distMatrix)
    return pop, fits



@numba.njit(nogil=NO_GIL, cache=CAN_CACHE)
def _runTwoOpt(n, tour, distMatrix):
    isImproved = True
    while isImproved:
        isImproved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n):
                a = tour[i - 1]
                b = tour[i]
                c = tour[j]
                d = tour[(j + 1) % n]
                if distMatrix[a, b] + distMatrix[c, d] > distMatrix[a, c] + distMatrix[b, d]:
                    tour[i : j + 1] = tour[i : j + 1][: : -1]
                    isImproved = True
    return tour



def runGA(instance, runNum):
    runDir = ROOT_DIR / 'stdout' / 'runs' / instance.instanceName
    if not runDir.is_dir():
        print(f'WARNING: Cannot locate {runDir}, creating it...')
        os.makedirs(runDir, exist_ok=True)

    runFile = runDir / f'{instance.instanceName}_{runNum}.txt'
    log = Log(runFile)

    optFit = instance.optFit
    n = instance.getN()
    nodes = instance.getNodes()
    distMatrix = np.round(cdist(nodes, nodes, 'euclidean')).astype(np.int64)

    startTime = perf_counter()
    log.logStart(instance)

    genStart = perf_counter()

    pop = _createPop(POP_SIZE, n)
    fits = _calcFits(POP_SIZE, n, pop, distMatrix)
    eliteTour, eliteFit = _getElite(fits, pop)

    percentError = (eliteFit - optFit) / optFit * 100 if optFit is not None else None
    genTime = perf_counter() - genStart
    log.logGen(genTime, 0, eliteFit, percentError)

    stagnantGens = 0
    for gen in range(1, MAX_GENS + 1):
        genStart = perf_counter()

        newPopRest = _createPops(POP_SIZE, fits, SELECTION_SIZE, pop, OX_RATE, SWAP_MUT_RATE, n)
        newFitsRest = _calcFits(POP_SIZE - 1, n, newPopRest, distMatrix)
        threshold = np.percentile(newFitsRest, TWO_OPT_PERCENTILE)
        newPopRest, newFitsRest = _runTwoOptTopK(POP_SIZE - 1, newPopRest, newFitsRest, distMatrix, n, threshold)

        newPop = np.empty((POP_SIZE, n), dtype=np.int64)
        newFits = np.empty(POP_SIZE, dtype=np.float64)
        newPop[0] = eliteTour.copy()
        newFits[0] = eliteFit
        newPop[1 :] = newPopRest
        newFits[1 :] = newFitsRest

        pop, fits = newPop, newFits
        tempEliteTour, tempEliteFit = _getElite(fits, pop)
        if tempEliteFit < eliteFit - MIN_CHANGE:
            eliteTour = tempEliteTour.copy()
            eliteFit = tempEliteFit
            stagnantGens = 0
        else:
            stagnantGens += 1
        eliteTour = _runTwoOpt(n, eliteTour.copy(), distMatrix)
        eliteFit = _calcFit(n, eliteTour, distMatrix)

        percentError = (eliteFit - optFit) / optFit * 100 if optFit is not None else None
        genTime = perf_counter() - genStart
        log.logGen(genTime, gen, eliteFit, percentError)

        if (stagnantGens >= CONVERGENCE_GEN) or (gen >= MAX_GENS) or (optFit is not None and eliteFit == optFit):
            endTime = perf_counter()
            log.logEnd(eliteFit, optFit, percentError, endTime, startTime, eliteTour)
            return eliteFit