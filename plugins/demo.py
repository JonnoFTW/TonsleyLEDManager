def show(Runner, arg=None, fps=24, rows=17, cols=165, scale=8):
    import pygame, sys
    FPS = fps
    fpsClock = pygame.time.Clock()

    board_dimensions = (cols, rows)

    disp_size = (cols * scale, rows * scale)
    pygame.init()
    screen = pygame.display.set_mode(disp_size)
    if arg is None:
        runner = Runner(board_dimensions)
    else:
        runner = Runner(board_dimensions, arg)
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
