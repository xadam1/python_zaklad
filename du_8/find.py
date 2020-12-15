"""
$ python find.py Nemo data/CSFD/Hleda_se_Nemo.txt
>>> run('python find.py Nemo data/CSFD/Hleda_se_Nemo.txt')  # doctest: +NORMALIZE_WHITESPACE
   2   a odlehlém příbytku ze sasanek Marlin a jeho jediný syn Nemo. Marlin se s
   4   snaží svého syna před nástrahami okolí ochránit. Nemo je však, stejně jako
  23   postaviček. Scénáristou a režisérem filmu Hledá se Nemo je Andrew Stanton,
  27   Hledá se Nemo a jeho úžasný podmořský svět je zcela novým uměleckým a

$ python find.py Matrix data/CSFD/Harry_Potter.txt
>>> run('python find.py Matrix data/CSFD/Harry_Potter.txt')  # doctest: +NORMALIZE_WHITESPACE

$ python find.py slivovice data/CSFD/Dedictvi.txt
>>> run('python find.py slivovice data/CSFD/Dedictvi.txt')  # doctest: +NORMALIZE_WHITESPACE
   3   slivovice a zahálčivým povalováním v trávě. Jeho poklidný a vcelku spokojený
"""

import sys


def main() -> None:
    word = sys.argv[1]
    file_path = sys.argv[2]

    try:
        with open(file_path) as file:
            lines = file.readlines()
            count = 1
            for line in lines:
                if word in line:
                    print(f'{count : >4}   {line}')
                count += 1

    except:
        print(f'File [{file_path}] could not be loaded.')


def run(command: str) -> None:
    '''Pomocná funkce pro doctesty - neměňte!'''
    sys.argv = command.split()[1:]
    main()


if __name__ == '__main__':
    main()
