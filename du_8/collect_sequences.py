"""
$ python collect_sequences.py data/seqs data/collected_seqs.fasta
>>> run('python collect_sequences.py data/seqs data/collected_seqs.fasta')  # doctest: +NORMALIZE_WHITESPACE

Srovnání s očekávaným výstupním souborem:
>>> diff('data/collected_seqs-expected.fasta', 'data/collected_seqs.fasta')
True
"""

import sys
import glob
from pathlib import Path


def main() -> None:
    folder = sys.argv[1]
    output_file = sys.argv[2]

    files = sorted(glob.glob(f'{folder}/*.txt'))

    with open(output_file, 'w') as out:
        for file in files:
            inputFileName = Path(file).stem
            out.writelines(f'>{inputFileName}\n')
            with open(file) as f:
                out.writelines(f.readlines())
            out.writelines('\n')


def run(command: str) -> None:
    '''Pomocná funkce pro doctesty - neměňte!'''
    sys.argv = command.split()[1:]
    main()


def diff(file1: str, file2: str) -> bool:
    '''Pomocná funkce pro doctesty - neměňte!'''
    import difflib
    with open(file1, encoding='utf8') as f:
        lines1 = [line.rstrip() for line in f if line.rstrip() != '']
    with open(file2, encoding='utf8') as f:
        lines2 = [line.rstrip() for line in f if line.rstrip() != '']
    d = list(difflib.ndiff(lines1, lines2))
    success = all(line.startswith(' ') for line in d)
    if not success:
        print('Files are different:')
        print('\n'.join(d))
    return success


if __name__ == '__main__':
    main()
