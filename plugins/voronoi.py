from __future__ import absolute_import
import numpy as np
import math

REGIONS = 10

class Runner:

    def __init__(self, dims):

        self.dims = dims
        self.width = dims[0]
        self.height = dims[1]

    def rand_voronoi(self, regions):
        im = np.zeros((self.width, self.height, 3), dtype=np.uint8)
        nx = np.random.randint(0, self.width, size=regions, dtype=np.uint8)
        ny = np.random.randint(0, self.height, size=regions, dtype=np.uint8)
        nr = np.random.randint(0, 256, size=regions, dtype=np.uint8)
        ng = np.random.randint(0, 256, size=regions, dtype=np.uint8)
        nb = np.random.randint(0, 256, size=regions, dtype=np.uint8)
        for y in range(self.height):
            for x in range(self.width):
                dmin = math.hypot(self.width-1, self.height-1)
                h = -1
                for i in range(regions):
                    d = math.hypot(nx[i]-x, ny[i]-y)
                    if d < dmin:
                        dmin = d
                        h = i
                im[x][y] = np.array([nr[h], ng[h], nb[h]])
        return im


    def run(self):
        return self.rand_voronoi(REGIONS)

if __name__ == "__main__":
    from demo import show
    # fps is 1/3 so that we get 3 seconds to admire the output before changing
    show(Runner, fps=1/3, cols=192, rows=108)
