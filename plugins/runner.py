class Runner:

    def __init__(self, board_dimensions):
        self.board_dimensions = board_dimensions
        import numpy as np
        self.np = np
        self.pixels = self.np.random.normal(128, 128, (self.board_dimensions[0], self.board_dimensions[1], 3)).astype(self.np.uint8)

    def run(self):
        # shift everything to the left, put a new random column on the end
        
        self.pixels = self.np.roll(self.pixels, 1, 0)
        col = self.np.random.normal(128, 128, [17, 3]).astype(dtype=self.np.uint8)
        for idx, i in enumerate(col):
            self.pixels[0][idx] = i
        self.pixels.sort(1)
        return self.pixels