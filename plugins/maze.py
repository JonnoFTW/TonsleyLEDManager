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
        self.width = board_dimensions[1]
        self.height = board_dimensions[0]
        self.reset()

        # blue for the runner position
        # white for path
        # red for frontier
        # black for walls

    def reset(self):
        self.maze = self.np.zeros((self.height, self.width), dtype=self.np.uint8)
        for x in range(self.maze.shape[0]):
            if x % 2 == 0:
                self.maze[x].fill(1)
        for y in range(self.maze.shape[1]):
            if y % 2 == 0:
                self.maze[:, y].fill(1)


        self.generated = False
        # both need to be odd numbers
        self.C = [(self.np.random.choice(range(3, self.height-3, 2)),
                   self.np.random.choice(range(3, self.width-3, 2)), 'W')]
        t = self.C[0]
        self.maze[t[0], t[1]] = 0
        self.maze[t[0]-1, t[1]] = 0
        self.maze[t[0]+1, t[1]] = 0
        self.maze[t[0], t[1]+1] = 0
        self.maze[t[0], t[1]-1] = 0
        self.maze_generator = self.step()
        self.maze[0].fill(1)
        self.maze[-1].fill(1)

    def render_maze(self):
        out = self.np.empty((self.height, self.width, 3), dtype=self.np.uint8)
        for x, row in enumerate(self.maze):
            for y, cell in enumerate(row):
                if cell <= 0 or cell == 4:
                    out[x, y] = self.white
                elif cell == 1:
                    out[x, y] = self.black
                elif cell == 2:
                    out[x, y] = self.red
                elif cell == 3 or cell == -2:
                    out[x, y] = self.green
                elif cell == 5:
                    out[x, y] = self.blue
        return out

    def step(self):
        while self.C:
            target = self.C[self.np.random.randint(0, len(self.C))]
            n = self.neighbours(target[0], target[1])
            self.np.random.shuffle(n)
            if not n:
                self.maze[target[0], target[1]] = 4
                if target[2] == 'S':
                    self.maze[target[0], target[1]-1] = 4
                elif target[2] == 'N':
                    self.maze[target[0], target[1]+1] = 4
                elif target[2] == 'E':
                    self.maze[target[0]-1, target[1]] = 4
                elif target[2] == 'W':
                    self.maze[target[0]+1, target[1]] = 4
                self.C.remove(target)
            else:
                # mark visited cells as 2
                new_cell = n.pop()
                self.maze[new_cell[0], new_cell[1]] = 2
                if new_cell[2] == 'S':
                    self.maze[new_cell[0], new_cell[1]-1] = 2
                elif new_cell[2] == 'N':
                    self.maze[new_cell[0], new_cell[1]+1] = 2
                elif new_cell[2] == 'E':
                    self.maze[new_cell[0]-1, new_cell[1]] = 2
                elif new_cell[2] == 'W':
                    self.maze[new_cell[0]+1, new_cell[1]] = 2

                self.C.append(new_cell)
            yield self.render_maze()

    def neighbours(self, x, y, v=2):
        return [(nx, ny, d) for nx, ny, d in [(x, y+v, 'S'), (x, y-v, 'N'), (x+v, y, 'E'), (x-v, y, 'W')]
                if 1 <= nx < self.maze.shape[0] and 0 <= ny < self.maze.shape[1] and self.maze[nx, ny] <= 0]

    def solve(self):
        #run the next step in maze

        # update runner position
        # get the random neighbours and move into one of them
        while self.stack:
            # get the neighbours of the current cell
            x, y, d = self.runner
            self.maze[x, y] = 5
            n = self.neighbours(x, y, 1)
            if x >= self.height - 2:
                print "Solved"
                break
            if not n:
                self.runner = self.stack.pop()
                self.maze[self.runner[0], self.runner[1]] = 2
                yield
            else:

                self.stack.extend(n)
                new_cell = n[0]
                self.runner = new_cell
                self.maze[new_cell[0], new_cell[1]] = 0
                yield


    def run(self):
        if not self.generated:
            # do the next step in the maze generator
            try:
                return self.maze_generator.next()
            except StopIteration:
                self.generated = True
                for x in range(self.maze.shape[0]):
                    for y in range(self.maze.shape[1]):
                        if self.maze[x, y] != 1:
                            self.maze[x, y] = 0
                starts = list(self.np.where(self.maze[1] == 0)[0])# firsts white cell in the first column
                self.runner = [0, starts.pop(), 'E']
                self.maze_solver = self.solve()
                self.stack = [self.runner]
                return self.render_maze()
        else:
            try:
                self.maze_solver.next()
            except StopIteration:
                # we hit the end of the maze or it's unsolvable!
                self.reset()
            return self.render_maze()

if __name__ == "__main__":
    import pygame, sys
    FPS = 60
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