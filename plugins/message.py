# -*- coding: utf-8 -*-
from plugins.fonts import Font
import numpy as np

class Runner:
    def __init__(self, dims, message="Hello World"):
        self.dims = dims

        fnt = Font('open_sans.ttf', 16)
        # import numpy as np
        self.np = np
        render = fnt.render_text(message)
        message = str(render).splitlines()
        self.pixels = np.zeros((dims[1], max(dims[0], render.width), 3), dtype=np.uint8)
        white = [255, 255, 255]
        for y in range(render.height):
            for x in range(render.width):
                if message[y][x] == '#':
                    self.pixels[y, x] = white
        self.pixels = np.flipud(np.rot90(self.pixels, 1))

    def run(self):
        self.pixels = self.np.roll(self.pixels, -1, 0)
        out = self.pixels[0: self.dims[0]]
        return out

if __name__ == "__main__":
    import pygame, sys
    FPS = 24
    fpsClock = pygame.time.Clock()
    rows = 17
    cols = 165
    board_dimensions = (cols, rows)

    disp_size = (cols * 8, rows * 8)
    pygame.init()
    size = width, height = board_dimensions
    screen = pygame.display.set_mode(disp_size)
    runner = Runner(board_dimensions, "༼ຈل͜ຈ༽ﾉ")
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