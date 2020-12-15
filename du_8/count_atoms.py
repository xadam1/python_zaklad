"""
$ python count_atoms.py data/ibuprofen.pdb
>>> run('python count_atoms.py data/ibuprofen.pdb')  # doctest: +NORMALIZE_WHITESPACE
C: 13
H: 18
O: 2

$ python count_atoms.py data/1tqn.pdb
>>> run('python count_atoms.py data/1tqn.pdb')  # doctest: +NORMALIZE_WHITESPACE
C: 2479
FE: 1
N: 627
O: 868
S: 24
"""

import sys


def main() -> None:
    filePath = sys.argv[1]
    atomLines = []
    data = {}

    load_atoms(filePath, atomLines)
    count_atoms(atomLines, data)
    print_data(data)


def count_atoms(lines: [str], data: dict):
    for line in lines:
        atom = str.strip(line[76:78])
        increment_data(atom, data)


def load_atoms(filePath: str, atomLines: [str]):
    with open(filePath) as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                atomLines.append(line)


def increment_data(key: str, data: dict):
    if key in data:
        data[key] += 1
    else:
        data[key] = 1


def print_data(data: dict):
    for key in sorted(data):
        print(f'{key}: {data[key]}')


def run(command: str) -> None:
    """Pomocná funkce pro doctesty - neměňte!"""
    sys.argv = command.split()[1:]
    main()


if __name__ == '__main__':
    main()
