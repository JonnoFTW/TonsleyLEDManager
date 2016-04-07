#!/usr/bin/env python
# play the game of life
from collections import deque
def read_cells(string):
    out = []
    for row in string.splitlines():
        out.append([{'O':1, '.':0}[c] for c in row])
    return out
    
lwss = """.O..O
O....
O...O
OOOO."""
glider = """OOO
O..
.O."""
multum = """...OOO
..O..O
.O....
O....."""

class Runner:

    blue = [0, 0, 255]
    white = [255, 255, 255]
    black = [0, 0, 0]
    green = [0, 255, 0]
    red = [255, 0, 0]

    def __init__(self, board_dimensions):
        self.dims = board_dimensions
        import numpy as np
        self.np = np
        np.set_printoptions(threshold=np.nan)
        self.width = board_dimensions[0]
        self.height = board_dimensions[1]
        self.reset()
        


    def reset(self):
        self.last = deque([], 10)
        self.cells = self.np.zeros((self.height, self.width), dtype=self.np.uint8)
        # add a few gliders of random orientation
        things = map(lambda x: self.np.array(read_cells(x)), [lwss, glider, multum])
        for _ in xrange(10):
            thing = self.np.random.choice(things)
            x, y = self.np.random.randint(0, self.height - thing.shape[0]), self.np.random.randint(0, self.width- thing.shape[1])
            thing = self.np.rot90(thing, self.np.random.randint(0, 4))
            self.cells[x:x+thing.shape[0], y:y+thing.shape[1]] = thing

    def render_cells(self):
        out = self.np.empty((self.width, self.height, 3), dtype=self.np.uint8)
        for x, row in enumerate(self.cells):
            for y, cell in enumerate(row):
                if cell == 1:
                    out[y, x] = self.white
                else:
                    out[y, x] = self.black
        return out

    def step(self):
        width = self.width
        height = self.height
        total_sum = 0
        cells = self.np.zeros(self.cells.shape, dtype=self.np.uint8)
        for x in xrange(width):
            for y in xrange(height):
                yp = (((y+1)%height)+height)%height
                ym = (((y-1)%height)+height)%height
                xp = (((x+1)%width)+width)%width
                xm = (((x-1)%width)+width)%width
                # first selects by row, then column
                neighbours = [
                    self.cells[ym, xm],
                    self.cells[ym, x],
                    self.cells[ym, xp],
                    self.cells[y, xm],
                    self.cells[y, xp],
                    self.cells[yp, xm],
                    self.cells[yp, x],
                    self.cells[yp, xp]
                ]
                total = sum(neighbours)
                total_sum += total
                if (self.cells[y, x] == 1 and total == 2) or total == 3:
                    cells[y, x] = 1
                        
        if total_sum == 0 or any((cells == x).all() for x in self.last):
            self.reset()
        else:
            self.cells = cells
            self.last.append(cells)
        return self.render_cells()
                

    def run(self):
        return self.step()
        

if __name__ == "__main__":
    import pygame, sys
    FPS = 2
    fpsClock = pygame.time.Clock()
    rows = 17
    cols = 165
    board_dimensions = (cols, rows)

    disp_size = (cols * 8, rows * 8)
    pygame.init()
    size = width, height = board_dimensions
    screen = pygame.display.set_mode(disp_size)
    runner = Runner(board_dimensions)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
        screen.fill((0, 0, 0))
        # draw the pixels
        pixels = runner.run()
        temp_surface = pygame.Surface(board_dimensions)
        pygame.surfarray.blit_array(temp_surface, pixels)
        pygame.transform.scale(temp_surface, disp_size, screen)
        pygame.display.flip()
        fpsClock.tick(FPS)
