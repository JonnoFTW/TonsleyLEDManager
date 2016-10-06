class Runner:
    def __init__(self, board_dimensions):
        self.board_dimensions = board_dimensions
        import numpy as np
        self.np = np
        def rbool():
            return np.random.choice([True, False])
        self.sorted = rbool()
        self.facing = rbool()
        self.face_in = rbool()
        try:
            from matplotlib import cm
            numcolors = 9012
            color_maps = ['rainbow', 'flag', 'terrain', 'ocean', 'gist_earth', 'viridis', 'gnuplot', 'brg', 'cubehelix', 'CMRmap']
            cmap = cm.get_cmap(np.random.choice(color_maps))
            self.colors = np.array(
                [map(lambda x: int(x * 255), list(cmap(1. * i / numcolors))[:-1]) for i in range(numcolors)])
        except ImportError:
            self.colors = np.random.randint(0, 255, [9012, 3])
        self.pixels = self.np.zeros((self.board_dimensions[0], self.board_dimensions[1], 3)).astype(self.np.uint8)

    def run(self):
        # shift everything to the left, put a new random column on the end

        self.pixels = self.np.roll(self.pixels, 1, 1)
        if self.facing:
            col1, col2 = [self.colors[self.np.random.choice(self.colors.shape[0], self.board_dimensions[0]/2, replace=False)] for _ in [1,2]]
            col1.sort(0)
            col2.sort(0)
            if self.face_in:
                col = self.np.concatenate([col1[::-1],col2])
            else:
                col = self.np.concatenate([col1,col2[::-1]])

        else:
            col = self.colors[self.np.random.choice(self.colors.shape[0], self.board_dimensions[0], replace=False)]
        for idx, i in enumerate(col):
            self.pixels[idx][0] = i
        if not self.facing and self.sorted:
            self.pixels.sort(0)

        return self.pixels


if __name__ == "__main__":
    from demo import show

    show(Runner)