from typing import List
import math


def mean(numbers: List[float]) -> float:
    '''Vrať průměr čísel numbers.
    >>> round(mean([1, 2]), 6)
    1.5
    >>> round(mean([1, 2, 4]), 6)
    2.333333
    >>> round(mean([0.5, -10, 12.5, 9, 9.156, -3.2]), 6)
    2.992667
    >>> round(mean([]), 6)
    nan
    '''
    try:
        return sum(numbers) / len(numbers)
    except:
        return math.nan


# if __name__ == "__main__":
    #print(round(mean([1, 2]), 6))
    #print(round(mean([1, 2, 4]), 6))
    #print(round(mean([0.5, -10, 12.5, 9, 9.156, -3.2]), 6))
    #print(round(mean([]), 6))
