def du_1():
    numbers = input().split()
    even_ = []
    odd_ = []

    for num in numbers:
        num = int(num)
        if (num % 2 == 0):
            even_.append(num)
        else:
            odd_.append(num)

    print("Lichá: ", end='')
    for oddNum in odd_:
        print(oddNum, end=' ')

    print()

    print("Sudá: ", end='')
    for evenNum in even_:
        print(evenNum, end=' ')


def du_2():
    import math
    words = input().split()
    max_ = -math.inf
    max_word = ''

    min_ = math.inf
    min_word = ''

    for word in words:
        if len(word) > max_:
            max_word = word
            max_ = len(word)
        elif len(word) < min_:
            min_word = word
            min_ = len(word)

    print(max_word)
    print(min_word)
