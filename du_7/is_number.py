
def is_number(string: str) -> bool:
    '''Rozhodni jestli string reprezentuje číslo.
    >>> is_number('9')
    True
    >>> is_number('9.9')
    True
    >>> is_number('6.626e-34')
    True
    >>> is_number('0.0.00')
    False
    >>> is_number('three')
    False
    '''
    try:
        float(string)
        return True
    except:
        return False


# if __name__ == "__main__":
    # print(is_number('9'))
    # print(is_number('9.9'))
    # print(is_number('6.626e-34'))
    # print(is_number('0.0.00'))
    # print(is_number('three'))
