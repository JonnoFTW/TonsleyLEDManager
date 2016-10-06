class Runner:
    def __init__(self, dims):
        self.width = dims[0]
        self.height = dims[1]
        import numpy as np
        from matplotlib import cm
        from itertools import cycle
        self.np = np

        color_maps = ['viridis',  'magma', 'inferno', 'plasma']
        cmap1 = cm.get_cmap(color_maps[0], 256)
        cmap2 = cm.get_cmap(color_maps[1], 256)
        maps = [(cm.get_cmap(x, 256).colors * 255)[0:, :3].astype(np.uint8) for x in color_maps]

        cols1 = (cmap1.colors * 255)[0:, :3].astype(np.uint8)
        cols2 = (cmap2.colors * 255)[0:, :3].astype(np.uint8)
        self.cols = np.concatenate((cols1, cols1[::-1], cols2, cols2[::-1]))
        self.cols = np.concatenate((self.cols, self.cols[::-1]))
        tup = []
        for m in maps:
            tup.extend([m, m[::-1]])
        self.cols = np.concatenate(tup)
        self.cols = np.concatenate((self.cols, self.cols[::-1]))
        self.step = 0
        print("Colors length:", len(self.cols))
        denoms = np.sin(np.arange(0, 2*np.pi, 0.01))+(3)
        self.denom = cycle(denoms)
        self.up = True
        self.half_len = len(self.cols)/32.
        print("Half length", self.half_len)

    def run(self):
        np = self.np
        w = self.width
        h = self.height
        img = np.empty((self.width, self.height, 3), dtype=np.uint8)
        step = 5
        half_len = self.half_len
        denom = self.denom.next()
        for y in xrange(0, self.height):
            for x in xrange(0, self.width):
                col = int(half_len + (
                    half_len * np.sin(np.sqrt((x - w / 2.0) * (x - w / 2.0) + (y - h / 2.0) * (y - h / 2.0)) / denom)))
                if col+self.step < len(self.cols):
                    img[x][y] = self.cols[(col+self.step)]
                else:
                    img[x][y] = self.cols[len(self.cols)-(col+self.step)]
        self.step += step
        self.step %= len(self.cols)

        return img


if __name__ == "__main__":
    from demo import show

    show(Runner, fps=30, rows=17, cols=165, scale=8)
