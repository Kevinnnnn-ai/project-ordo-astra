import numpy as np
import tsplib95 as tl
from pathlib import Path

def _getOptFits(optFitsFile):
    optFits = {}
    if not optFitsFile.exists():
        return optFits

    with open(optFitsFile, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' not in line:
                continue

            key, value = line.split(':', 1)
            try:
                optFits[key.strip()] = int(value.strip())
            except ValueError:
                continue

    return optFits

class Euc2D:
    def __init__(self, instanceName):
        self.INSTANCE_TYPE = 'Euclidean 2D TSP'
        self.ROOT_DIR = Path(__file__).resolve().parents[2]
        self.OPT_FITS_FILE = self.ROOT_DIR / 'res' / 'info' / 'opt-fits.txt'

        self.instanceName = instanceName
        self.instanceFile = self.ROOT_DIR / 'res' / 'tsplib95' / 'tsp' / f'{instanceName}.tsp'
        self.instance = tl.load(self.instanceFile)

        self.edgeWeightType = self.instance.edge_weight_type
        nodes = self.instance.node_coords.values()
        self.nodes = np.array(list(nodes))
        self.optFit = _getOptFits(self.OPT_FITS_FILE).get(self.instanceName)
        self.n = self.nodes.shape[0]

    def getNodes(self):
        return self.nodes

    def getN(self):
        return self.n

    def getOptFit(self):
        return self.optFit