"""
$ python recursive_find.py Dory data/CSFD
>>> run('python recursive_find.py Dory data/CSFD')  # doctest: +NORMALIZE_WHITESPACE
data/CSFD/Hleda_se_Dory.txt
data/CSFD/Hleda_se_Nemo.txt

$ python recursive_find.py slivovice data
>>> run('python recursive_find.py slivovice data')  # doctest: +NORMALIZE_WHITESPACE
data/CSFD/Dedictvi.txt

$ python recursive_find.py isoprenylace data
>>> run('python recursive_find.py isoprenylace data')  # doctest: +NORMALIZE_WHITESPACE
"""

import sys
from contextlib import redirect_stdout
from typing import TextIO
import glob
import os


def main() -> None:
    word = sys.argv[1]
    dir_path = sys.argv[2]

    matching_files = []

    sniff_subdir(dir_path, word, matching_files)

    for file_path in matching_files:
        print(file_path)


def sniff_subdir(subdirPath: str, word: str, matching_files: [str]):
    paths = sorted(glob.glob(subdirPath + '/*'))
    for path in paths:
        if os.path.isfile(path):
            sniff_file(path, word, matching_files)
        else:
            sniff_subdir(path, word, matching_files)


def sniff_file(path: str, word: str, matching_files: [str]):
    with open(path) as file:
        lines = file.readlines()
        for line in lines:
            if word in line:
                matching_files.append(path)
                return


def run(command: str) -> None:
    '''Pomocná funkce pro doctesty - neměňte!'''
    sys.argv = command.split()[1:]
    with redirect_stdout(SlashyWriter(sys.stdout)):
        main()


class SlashyWriter(TextIO):
    '''Pomocná třída pro doctesty - neměňte!'''

    def __init__(self, inner: TextIO) -> None: self.inner = inner

    def write(self, s: str): return self.inner.write(s.replace('\\', '/'))

    def writelines(self, lines): list(map(self.write, lines))

    def flush(self): return self.inner.flush()


if __name__ == '__main__':
    main()
