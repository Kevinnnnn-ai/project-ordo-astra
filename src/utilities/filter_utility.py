import tsplib95 as tl
from pathlib import Path

class Filter:
    def __init__(self):
        self.root_directory = Path(__file__).resolve().parents[2]
        self.instance_directory = self.root_directory / 'res' / 'tsplib' / 'tsp'
        self.information_directory = self.root_directory / 'res' / 'info'

    def FilterEuclidean2DInstances(self):
        if not self.information_directory.is_dir():
            print(f'ERROR: Cannot locate {self.information_directory} (info directory)')
            return

        if not self.instance_directory.is_dir():
            print(f'ERROR: Cannot locate {self.instance_directory} (instance directory)')
            return

        names = []
        for instance_file in self.instance_directory.iterdir():
            if instance_file.is_file() and (instance_file.suffix == '.tsp'):
                try:
                    instance = tl.load(instance_file)
                    if instance.edge_weight_type == 'EUC_2D':
                        names.append(instance_file.stem)
                except Exception as e:
                    print(f'EXCEPTION: {e}')

        filter_file = self.information_directory / 'euc-2d-instances.txt'
        with open(filter_file, 'w', newline='') as a:
            for name in sorted(names):
                a.write(f'{name}\n')