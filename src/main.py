from .utils.instance_util import Euc2D
from .genetic_algorithm import runGA
from pathlib import Path



EXCLUSIONS = set()
INSTANCE_TYPE = 'euc_2d'
NUM_RUNS = 10
START_RUN = 0



class Run:
    def __init__(self, instanceName, instanceType):
        self.instanceName = instanceName
        self.instanceType = instanceType

    def runGa(self, numRuns, instance, startRun):
        for i in range(numRuns):
            runGA(instance, i + startRun)



def getInstanceNames(instancesFile):
    instanceNames = []
    for line in open(instancesFile, 'r'):
        line = line.strip()
        if line and line not in EXCLUSIONS:
            instanceNames.append(line)
    return instanceNames



if __name__ == '__main__':
    rootDir = Path(__file__).resolve().parents[1]
    instancesFile = rootDir / 'res' / 'info' / 'euc-2d-instances.txt'
    instanceNames = getInstanceNames(instancesFile)

    for instanceName in instanceNames:
        run = Run(instanceName, INSTANCE_TYPE)
        if INSTANCE_TYPE == 'euc_2d':
            instance = Euc2D(instanceName)
        run.runGa(NUM_RUNS, instance, START_RUN)
