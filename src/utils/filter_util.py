import tsplib95 as tl
from pathlib import Path



class Filter:
    def __init__(self):
        self.rootDir = Path(__file__).resolve().parents[2]
        self.instanceDir = self.rootDir / 'res' / 'tsplib' / 'tsp'
        self.infoDir = self.rootDir / 'res' / 'info'



    def filterEuc2D(self):
        if not self.infoDir.is_dir():
            print(f'ERROR: Cannot locate {self.infoDir} (info directory)')
            return

        if not self.instanceDir.is_dir():
            print(f'ERROR: Cannot locate {self.instanceDir} (instance directory)')
            return

        names = []
        for instanceFile in self.instanceDir.iterdir():
            if instanceFile.is_file() and (instanceFile.suffix == '.tsp'):
                try:
                    instance = tl.load(instanceFile)
                    if instance.edge_weight_type == 'EUC_2D':
                        names.append(instanceFile.stem)
                except Exception as e:
                    print(f'EXCEPTION: {e}')

        filterFile = self.infoDir / 'euc-2d-instances.txt'
        with open(filterFile, 'w', newline='') as a:
            for name in sorted(names):
                a.write(f'{name}\n')
