class Runner:
    def __init__(self, dims):
        self.width = dims[0]
        self.height = dims[1]
        import numpy as np
        from matplotlib import cm
        from itertools import cycle
        self.np = np

        color_maps = ['viridis',  'magma', 'inferno', 'plasma']
        cmap1 = cm.get_cmap(color_maps[3], 256)
        cmap2 = cm.get_cmap(color_maps[1], 256)
        cols1 = (cmap1.colors * 255)[0:, :3].astype(np.uint8)
        cols2 = (cmap2.colors * 255)[0:, :3].astype(np.uint8)
        self.cols = np.concatenate((cols1, cols1[::-1], cols2, cols2[::-1]))
        self.cols = np.concatenate((self.cols, self.cols[::-1]))
        self.step = 0
        print("Colors length:", len(self.cols))
        # denoms = (np.sin(np.linspace(0, 10, 50)) *2 )+ np.pi
        # print denoms
        # self.denom = cycle(np.concatenate((denoms,denoms[::-1])))
        self.denom = cycle([np.pi])
        self.up = True

    def run(self):
        np = self.np
        w = self.width
        h = self.height
        img = np.empty((self.width, self.height, 3), dtype=np.uint8)
        step = 5
        half_len = len(self.cols)/2.
        for y in xrange(0, self.height):
            for x in xrange(0, self.width):
                col = int(256 + (
                    256 * np.sin(np.sqrt((x - w / 2.0) * (x - w / 2.0) + (y - h / 2.0) * (y - h / 2.0)) / self.denom.next())))
                if col+self.step < len(self.cols):
                    img[x][y] = self.cols[(col+self.step)]
                else:
                    img[x][y] = self.cols[len(self.cols)-(col+self.step)]
        self.step += step
        self.step %= len(self.cols)
        # if self.up:
        #     if self.denom >= 2*np.pi:
        #         self.up = False
        #     else:
        #         self.denom += 0.1
        # else:
        #     if self.denom <= 1:
        #         self.up = True
        #     else:
        #         self.denom -= 0.1
        return img


if __name__ == "__main__":
    from demo import show

    show(Runner, fps=30, rows=17, cols=165, scale=8)
