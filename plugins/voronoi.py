# import pyopencl as cl

REGIONS = 13

class Runner:

    def __init__(self, dims):
        import numpy as np
        self.np = np
        self.dims = dims
        self.width = dims[0]
        self.height = dims[1]
        self.regions = REGIONS
        nx = np.random.randint(0, self.width, size=self.regions, dtype=np.int16)
        ny = np.random.randint(0, self.height, size=self.regions, dtype=np.int16)
        self.points = np.dstack((nx, ny))[0]
        self.cols = np.random.randint(0, 256, size=(self.regions, 3), dtype=np.uint8)
        self.init_gpu()

    def init_gpu(self):
        pass
        # self.ctx = cl.Context([cl.get_platforms()[0].get_devices()[0]])
        # self.queue = cl.CommandQueue(self.ctx)
        # self.prg = cl.Program(self.ctx, """
        #        #pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable
        #        __kernel void voronoi(__global uchar4 *img, __constant ushort2 points, __constant uchar4 *lut,
        #                                  ushort const height, ushort const width, ushort const regions)
        #        {
        #            int gid = get_global_id(0);
        #            int x = gid/width;
        #            int y = gid/height;
        #            int h = -1;
        #            int dmin = hypot(width -1, height -1);
        #            for(int i; i < regions; i++) {
        #               int d = hypot(points[i].x -x, points[i].y - y);
        #               if (d < dmin) {
        #                 dmin = d;
        #                 h = i;
        #               }
        #            }
        #            img[gid] = lut[h];
        #        }
        #    """).build()

    def voronoi_gpu(self):
        mf = cl.mem_flags
        output = self.np.zeros((self.width, self.height), self.np.uint8)
        output_opencl = cl.Buffer(self.ctx, mf.WRITE_ONLY, output.nbytes)

        self.prg.voronoi(self.queue, output.shape, None, q_opencl, lut_opencl, output_opencl)

        cl.enqueue_copy(self.queue, output, output_opencl).wait()
        return output
    def rand_voronoi(self):
        np = self.np
        im = np.zeros((self.width, self.height, 3), dtype=np.uint8)
        for y in xrange(self.height):
            for x in xrange(self.width):
                dmin = np.hypot(self.width-1, self.height-1)
                h = -1
                for i in xrange(self.regions):
                    d = np.hypot(self.points[i][0]-x, self.points[i][1]-y)
                    if d < dmin:
                        dmin = d
                        h = i
                im[x][y] = self.cols[h]
        return im

    def run(self):
        np = self.np
        jitter = np.random.randint(0, 3, size=self.points.shape, dtype=np.int16) - 1

        self.points += jitter
        self.points[:, 0] %= self.width
        self.points[:, 1] %= self.height
        # return self.voronoi_gpu()
        return self.rand_voronoi()


if __name__ == "__main__":

    from demo import show
    # fps is 1/3 so that we get 3 seconds to admire the output before changing
    show(Runner, fps=25, cols=165, rows=17, scale=10)