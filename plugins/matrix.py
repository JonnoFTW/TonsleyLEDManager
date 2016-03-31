# -*- coding: utf-8 -*-
import numpy as np

class Runner:
    def __init__(self, dims):
        self.dims = dims
        # import numpy as np
        self.np = np
        self.width = board_dimensions[0]
        self.height = board_dimensions[1]
        self.cells = self.np.zeros((self.height, self.width), dtype=self.np.uint8)
    def run(self):
        # run the code, generating
        return self.cells

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