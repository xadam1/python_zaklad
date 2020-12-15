'''
$ python sum_paper.py data/paper.txt
>>> run('python sum_paper.py data/paper.txt')  # doctest: +NORMALIZE_WHITESPACE 
Alice: 15.0
Bob: 28.0
Cyril: 19.5
Dana: 20.0
Emil: 7.5
Filip: 8.0
Gertruda: 24.0
Hanka: 27.5
Ivan: 20.0
John: 22.0

$ python sum_paper.py data/paper2.txt
>>> run('python sum_paper.py data/paper2.txt')  # doctest: +NORMALIZE_WHITESPACE 
Filip: 3.5
Gertruda: 11.0
John: 22.0
'''

import sys


def main() -> None:
    file_path = sys.argv[1]

    data = {}

    with open(file_path) as file:
        lines = file.readlines()[1:]
        for line in lines:
            tmp = line.split(',')
            insert_data(tmp[1], float(tmp[2]), data)

    print_data(data)


def insert_data(key: str, value: float, data: dict):
    if key in data:
        data[key] = data[key] + value
    else:
        data[key] = value


def print_data(data: dict):
    for key in sorted(data):
        print(f'{key}: {data[key]}')


def run(command: str) -> None:
    '''Pomocná funkce pro doctesty - neměňte!'''
    sys.argv = command.split()[1:]
    main()


if __name__ == '__main__':
    main()
