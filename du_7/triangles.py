from typing import List, Tuple
import math


def check_inequality(a: float, b: float, c: float):
    if a+b <= c:
        raise ValueError("Violating triangle inequality")
    elif a+c <= b:
        raise ValueError("Violating triangle inequality")
    elif b+c <= a:
        raise ValueError("Violating triangle inequality")
    return


def triangle_area(a: float, b: float, c: float) -> float:
    '''Vrať povrch trojúhelníku se stranami a, b, c. Vyhoď ValueError pokud strany nesplňují trojúhelníkovou nerovnost.
    >>> round(triangle_area(3, 4, 5), 6)
    6.0
    >>> round(triangle_area(5.4, 5.2, 5.3), 6)
    12.154663
    >>> round(triangle_area(3, 4, 8), 6)
    Traceback (most recent call last):
        ...
    ValueError: Violating triangle inequality
    >>> round(triangle_area(3, 2, 1), 6)
    Traceback (most recent call last):
        ...
    ValueError: Violating triangle inequality
    >>> round(triangle_area(1.5, 2, 0.3), 6)
    Traceback (most recent call last):
        ...
    ValueError: Violating triangle inequality
    '''
    check_inequality(a, b, c)
    s = (a+b+c)/2
    return math.sqrt(s*(s-a)*(s-b)*(s-c))


def largest_triangle(triangles: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
    '''Vyber trojúhelník s největším obsahem.
    >>> largest_triangle([(3, 4, 5), (3, 4, 8), (6, 7, 6)])
    (6, 7, 6)
    >>> largest_triangle([(1, 2, 3)])
    Traceback (most recent call last):
        ...
    ValueError: No valid triangles
    '''
    ex_counter = 0
    max_area = 0
    max_triangle = 0

    for triangle in triangles:
        try:
            a, b, c = triangle
            area = triangle_area(a, b, c)
            if area > max_area:
                max_area = area
                max_triangle = triangle

        except ValueError:
            ex_counter += 1

    if ex_counter == len(triangles):
        raise ValueError("No valid triangles")
    return max_triangle


def largest_triangle_io(input_line: str) -> str:
    '''Zpracuj vstupní řetězec se zápisem trojúhelníků a vrať řetězec s hlášením o největším trojúhelníku.
    >>> largest_triangle_io('3.0 - 4.0 - 5.0 ; 3-4-8; 6-7-6')
    'Largest triangle is: 6.00 - 7.00 - 6.00'
    >>> largest_triangle_io('1-2-3; 4.5-8-16')  # Všechny trojúhelníku porušují troj. nerovnost
    'No valid triangles'
    >>> largest_triangle_io('3-4-5a; 8 - 7 - 10')  # 5a není správné číslo
    'Invalid input'
    >>> largest_triangle_io('3-4-5; 8-8; 42-42-42')  # Druhý trojúhelník má zadané pouze 2 strany
    'Invalid input'
    '''
    triangles = input_line.split(';')
    values = []
    for triangle in triangles:
        try:
            val = triangle.split('-')
            a = float(val[0])
            b = float(val[1])
            c = float(val[2])
            values.append((a, b, c))
        except:
            return 'Invalid input'

    try:
        max_triangle = largest_triangle(values)
        return f'Largest triangle is: {format_sites(max_triangle)}'
    except:
        return 'No valid triangles'


def main() -> None:
    '''Načti ze vstupu zápis trojúhelníku, a vypiš hlášení o největším trojúhelníku.'''
    inp = input(
        'Zadejte délky stran trojúhelníků (např. "3-4-5; 1.2 - 2 - 1.5"): ')
    out = largest_triangle_io(inp)
    print(out)


def format_sites(vals):
    a, b, c = vals
    return f"{a:.2f} - {b:.2f} - {c:.2f}"


if __name__ == '__main__':
    main()
