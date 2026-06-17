from util.instance_util import Euc2D
from util.plot_util import Plot
from genetic_algorithm import runGA

class Run:
    def __init__(self, instanceName, instanceType):
        self.instanceName = instanceName
        self.instanceType = instanceType

    def runGA(self, numRuns, instance, startRun):
        for i in range(numRuns):
            tourFit = runGA(instance, i + startRun)

# if __name__ == '__main__':
#     instanceNames = []
#
#     for line in open('res/info/euc-2d-instances.txt', 'r'):
#         line = line.strip()
#         if line and line not in tempExclusion:
#             instanceNames.append(line)
#
#     instanceType = 'euc_2d'
#     numRuns = 10
#     startRun = 0
#
#     for instanceName in tempExclusion:
#         run = Run(instanceName, instanceType)
#         if instanceType == 'euc_2d':
#             instance = Euc2D(instanceName)
#         run.runGA(numRuns, instance, startRun)

if __name__ == '__main__':
    temp = [
        'rl5934', # need 6 more runs
    ]

    instanceType = 'euc_2d'
    for instanceName in temp:
        run = Run(instanceName, instanceType)
        if instanceType == 'euc_2d':
            instance = Euc2D(instanceName)
            run.runGA(6, instance, 4)