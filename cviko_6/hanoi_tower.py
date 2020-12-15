import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

MIN_LEVEL = 1
MAX_LEVEL = 20


class InvalidOperationError(Exception):
    pass


class Keyboard:
    ESC = chr(27)
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = KeyboardWindows()
        except ImportError:
            self.impl = KeyboardUnix()

    def _get_char(self): return self.impl._get_char()

    def get_key(self): return self.impl._get_key()

class KeyboardUnix:
    def __init__(self):
        import tty, sys

    def _get_char(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def _get_key(self) -> str:
        ESC = chr(27)
        BRACKET = chr(91)
        c1 = self._get_char()
        if c1 == ESC:
            c2 = self._get_char()
            if c2 == BRACKET:
                c3 = self._get_char()
                if c3 == 'A':
                    return 'Up'
                elif c3 == 'B':
                    return 'Down'
                elif c3 == 'C':
                    return 'Right'
                elif c3 == 'D':
                    return 'Left'
                else:
                    return c3
            elif c2 == ESC:
                return ESC
            else:
                return c2
        else:
            return c1

class KeyboardWindows:
    def __init__(self):
        import msvcrt

    def _get_char(self):
        import msvcrt
        return msvcrt.getch()

    def _get_key(self) -> str:
        c1 = self._get_char()
        if ord(c1) == 0:
            c2 = self._get_char()
            if ord(c2) == ord('H'):
                return 'Up'
            elif ord(c2) == ord('P'):
                return 'Down'
            elif ord(c2) == ord('M'):
                return 'Right'
            elif ord(c2) == ord('K'):
                return 'Left'
            else:
                return chr(ord(c2))
        else:
            return chr(ord(c1))


class Grid(object):
    DEFAULT_CHAR: str = ' '
    width: int
    height: int
    chars: List[str]

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.chars = [self.DEFAULT_CHAR for i in range(width*height)]

    def __getitem__(self, xy: Tuple[int, int]) -> str:
        x, y = xy
        return self.chars[y*self.width + x]

    def __setitem__(self, xy: Tuple[int, int], value: str) -> None:
        assert len(value) == 1
        x, y = xy
        self.chars[y*self.width + x] = value

    def __str__(self) -> str:
        result = []
        for y in reversed(range(self.height)):
            for x in range(self.width):
                result.append(self[x, y])
            result.append('\n')
        return ''.join(result)


class Playground(object):
    towers: List[List[int]]
    holder_position: int
    holder_content: Optional[int]
    holder_content_origin: int
    n_moves: int

    def __init__(self, n_levels, n_towers=3) -> None:
        self.n_levels = n_levels
        self.n_towers = n_towers
        self.towers = [[] for i in range(n_towers)]
        self.towers[0].extend(reversed(range(n_levels)))
        self.holder_position = 0
        self.holder_content = None
        self.holder_content_origin = 0
        self.n_moves = 0

    def take(self) -> None:
        if self.holder_content is not None: 
            raise InvalidOperationError()
        tower = self.towers[self.holder_position]
        if len(tower) == 0:
            raise InvalidOperationError()
        self.holder_content = tower.pop()
        self.holder_content_origin = self.holder_position
    
    def drop(self) -> None:
        if self.holder_content is None:
            raise InvalidOperationError()
        tower = self.towers[self.holder_position]
        if len(tower) > 0 and tower[-1] < self.holder_content:
            raise InvalidOperationError()
        tower.append(self.holder_content)
        self.holder_content = None
        if self.holder_content_origin != self.holder_position:
            self.n_moves += 1

    def move_right(self) -> None:
        if self.holder_position == self.n_towers-1:
            raise InvalidOperationError()
        self.holder_position += 1

    def move_left(self) -> None:
        if self.holder_position == 0:
            raise InvalidOperationError()
        self.holder_position -= 1
    
    def has_won(self) -> bool:
        return len(self.towers[-1]) == self.n_levels

    def draw(self) -> None:
        MARGIN = 2
        height = self.n_levels + 3
        tower_width = 2 * self.n_levels + 3
        gap = 5
        width = self.n_towers * tower_width + (self.n_towers - 1) * gap + 2*MARGIN
        grid = Grid(width, height)
        for i_tower, tower in enumerate(self.towers):
            middle = MARGIN + 1 + self.n_levels + (tower_width + gap) * i_tower
            # ground
            for i in range(-self.n_levels-1, self.n_levels+2):
                grid[middle+i, 0] = '━'
            # pieces
            for y, piece in enumerate(tower, start=1):
                grid[middle-piece-1, y] = '┏'
                grid[middle+piece+1, y] = '┓'
                grid[middle-piece-1, y-1] = '┻'
                grid[middle+piece+1, y-1] = '┻'
                for i in range(-piece, piece+1):
                    grid[middle+i, y] = '━'
            # holder
            if i_tower == self.holder_position:
                grid[middle, -1] = 'V'
                # holded piece
                piece = self.holder_content
                if self.holder_content is not None:
                    grid[middle-piece-1, -2] = '┏'
                    grid[middle+piece+1, -2] = '┓'
                    grid[middle-piece-1, -3] = '┗'
                    grid[middle+piece+1, -3] = '┛'
                    for i in range(-piece, piece+1):
                        grid[middle+i, -2] = '━'
                        grid[middle+i, -3] = '━'
        print(grid)


def n_optimal_moves(n_levels: int) -> int:
    return 2**n_levels - 1

def clear_screen() -> None:
    if os.name=='nt':
        os.system('cls')
    else:
        os.system('clear')

def draw_screen(playground: Playground) -> None:
    clear_screen()
    print("Your task is to move the whole tower to the right. You can lift only one box at a time. Larger box can't be dropped on a smaller box.")
    print('Use arrow keys to move and lift/drop boxes. Press Q to quit.')
    print()
    playground.draw()

def main() -> None:
    print('Welcome to the Tower of Hanoi.')
    response = input(f'Select difficulty ({MIN_LEVEL}-{MAX_LEVEL}): ')
    try:
        levels = int(response)
        if not MIN_LEVEL <= levels <= MAX_LEVEL:
            raise ValueError()
    except ValueError:
        print(f'{response} is not a number between {MIN_LEVEL} and {MAX_LEVEL}')
        return
    playground = Playground(levels)
    keyboard = Keyboard()
    won = False
    t0 = datetime.now()
    while True:
        draw_screen(playground)
        key = keyboard.get_key()
        if key in ['q', 'Q', keyboard.ESC]:
            break
        try:
            if key == 'Up' or key == 'Down':
                try:
                    playground.take()
                except InvalidOperationError:
                    playground.drop()
            elif key == 'Left':
                playground.move_left()
            elif key == 'Right':
                playground.move_right()
        except InvalidOperationError:
            ...
        if playground.has_won():
            won = True
            break
    if won:
        draw_screen(playground)
        print('CONGRATULATIONS!')
        print(f'Moves: {playground.n_moves} (best possible is {n_optimal_moves(levels) })')
        t1 = datetime.now()
        time = str(t1 - t0)[:-3]
        print(f'Time: {time}')
        print()


if __name__ == '__main__':
    main()
