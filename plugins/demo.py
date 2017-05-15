def show(Runner, arg=None, fps=24, rows=17, cols=165, scale=8, withArgs=False):
    import pygame, sys
    FPS = fps
    fpsClock = pygame.time.Clock()

    board_dimensions = (cols, rows)

    disp_size = (cols * scale, rows * scale)
    pygame.init()
    screen_opts =  pygame.RESIZABLE | pygame.DOUBLEBUF
    screen = pygame.display.set_mode(disp_size, screen_opts)
    changed = False
    if arg is None:
        runner = Runner(board_dimensions)
    else:
        runner = Runner(board_dimensions, arg)
    font = pygame.font.Font('slkscr.ttf', 32)
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.VIDEORESIZE:
                disp_size = e.dict['size']
                screen = pygame.display.set_mode(disp_size, screen_opts)
        screen.fill((0, 0, 0))
        # draw the pixels
        txts = ["FPS: {0:.2f}".format(fpsClock.get_fps())]
        if withArgs:
            pixels, txt = runner.run(events)
            txts.append(txt)
        else:
            pixels = runner.run()

        temp_surface = pygame.Surface(board_dimensions)
        pygame.surfarray.blit_array(temp_surface, pixels)
        pygame.transform.scale(temp_surface, disp_size, screen)
        i = 1
        for txt in txts:
            for line in txt.splitlines():
                screen.blit(font.render(line.replace('[', '').replace(']', '').strip(), 1, (255, 255, 255)),
                            (30, 30 * i))
                i += 1

        pygame.display.flip()
        fpsClock.tick(FPS)
