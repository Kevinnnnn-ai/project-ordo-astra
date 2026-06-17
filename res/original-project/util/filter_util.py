import os
import tsplib95 as tl
from pathlib import Path

class Filter:
    def __init__(self):
        self.ROOT_DIR = Path(__file__).resolve().parents[2]
        self.INSTANCE_DIR = self.ROOT_DIR / 'res' / 'tsplib95' / 'tsp'
        self.INFO_DIR = self.ROOT_DIR / 'res' / 'info'

    def filterEuc2D(self):
        if not self.INFO_DIR.is_dir():
            print(f'ERROR: Cannot locate {self.INFO_DIR} (info directory)')
            return
            
        if not self.INSTANCE_DIR.is_dir():
            print(f'ERROR: Cannot locate {self.INSTANCE_DIR} (instance directory)')
            return

        names = []
        for instanceFile in self.INSTANCE_DIR.iterdir():
            if instanceFile.is_file() and (instanceFile.suffix == '.tsp'):
                try:
                    instance = tl.load(instanceFile)
                    if instance.edge_weight_type == 'EUC_2D':
                        names.append(instanceFile.stem)
                except Exception as e:
                    print(f'EXCEPTION: {e}')

        filterFile = self.INFO_DIR / 'euc-2d-instances.txt'
        with open(filterFile, 'w', newline='') as f:
            for name in sorted(names):
                f.write(f'{name}\n')