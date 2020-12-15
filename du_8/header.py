'''
$ python header.py data/generator_vet.txt
>>> run('python header.py data/generator_vet.txt')  # doctest: +NORMALIZE_WHITESPACE
Na svých stránkách mají podle soudu nepřišlo na to, že ne všechny politické strany a 
v roce 2004 je uvedeno, že do mě nedonutí se na parkovišti pod hradem žampach z 
potštejna, které mají na lidské společnosti, pro něž nebylo schválení vydáno, a 
neprodleně úřad informuje o jakémkoliv malou nápovědu jsou zadarmo, jsme měli 
od našich zákazníků.
Zdroj: https://corpora.fi.muni.cz/cblm/generate.cgi?language=czech

$ python header.py data/1tqn.pdb
>>> run('python header.py data/1tqn.pdb')  # doctest: +NORMALIZE_WHITESPACE
HEADER    OXIDOREDUCTASE                          17-JUN-04   1TQN              
TITLE     CRYSTAL STRUCTURE OF HUMAN MICROSOMAL P450 3A4                        
COMPND    MOL_ID: 1;                                                            
COMPND   2 MOLECULE: CYTOCHROME P450 3A4;                                       
COMPND   3 CHAIN: A;                                                            
COMPND   4 EC: 1.14.14.1;                                                       
COMPND   5 ENGINEERED: YES                                                      
SOURCE    MOL_ID: 1;                                                            
SOURCE   2 ORGANISM_SCIENTIFIC: HOMO SAPIENS;                                   
SOURCE   3 ORGANISM_COMMON: HUMAN;                                              

$ python header.py meaning_of_life
>>> run('python header.py meaning_of_life')  # doctest: +NORMALIZE_WHITESPACE
meaning_of_life not found
'''


import sys


def main() -> None:
    file_path = sys.argv[1]
    try:
        with open(file_path) as file:
            lines = file.readlines()
            count = 0
            for line in lines:
                if count >= 10:
                    return
                print(line)
                count += 1
    except:
        print(f'{file_path} not found')


def run(command: str) -> None:
    '''Pomocná funkce pro doctesty - neměňte!'''
    sys.argv = command.split()[1:]
    main()


if __name__ == '__main__':
    main()
