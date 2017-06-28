REGIONS = 128


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
        self.use_cl = False
        self.init_gpu()

    def init_gpu(self):
        try:
            import pyopencl as cl
            # print cl
            from pyopencl import array
        except Exception, e:
            import os
            print os.getenv('LD_LIBRARY_PATH')
            print e.message
            return
        self.use_cl = True
        self.cl = cl
        device = cl.get_platforms()[0].get_devices()[0]
        self.ctx = cl.Context([device])
        self.queue = cl.CommandQueue(self.ctx)
        print(device)
        self.lut = self.np.zeros(self.regions + 1, cl.array.vec.char3)
        for idx, i in enumerate(self.cols):
            self.lut[idx][0] = i[0]
            self.lut[idx][1] = i[1]
            self.lut[idx][2] = i[2]
        # self.lut[-1][0] = 0
        # self.lut[-1][1] = 0
        # self.lut[-1][2] = 0
        self.lut_opencl = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.lut)

        self.prg = cl.Program(self.ctx, """

               __kernel void voronoi(__global uchar4 *img,
                                     const __global ushort2 *points,
                                     __constant uchar4 *lut,
                                     ushort const height,
                                     ushort const width,
                                     ushort const regions)
               {
                   int x = get_global_id(0);
                   int y = get_global_id(1);
                   // int grid_width = get_num_groups(0) * get_local_size(0);
                    int index = y * height + x;
                   int h = -1;
                   float dmin = hypot((float)width -1, (float)height -1);
                   for(int i = 0; i < regions; i++) {
                      float d = hypot((float)points[i].x - y, (float)points[i].y - x);
                      if (d < dmin) {
                        dmin = d;
                        h = i;
                      }
                   }
                   img[index] = lut[h];
               }
           """).build()

    def voronoi_gpu(self):
        np = self.np
        cl = self.cl
        mf = cl.mem_flags
        img = self.np.zeros((self.width * self.height, 4), self.np.uint8)
        img_opencl = cl.Buffer(self.ctx, mf.WRITE_ONLY, img.nbytes)
        points_opencl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.points)
        self.prg.voronoi(self.queue, (self.height, self.width), None, img_opencl, points_opencl, self.lut_opencl,
                         np.uint16(self.height), np.uint16(self.width), np.uint16(self.regions))

        cl.enqueue_copy(self.queue, img, img_opencl).wait()
        return img.reshape((self.width, self.height, 4))[:, :, :3]

    def rand_voronoi(self):
        np = self.np
        im = np.zeros((self.width, self.height, 3), dtype=np.uint8)
        for y in xrange(self.height):
            for x in xrange(self.width):
                dmin = np.hypot(self.width - 1, self.height - 1)
                h = -1
                for i in xrange(self.regions):
                    d = np.hypot(self.points[i][0] - x, self.points[i][1] - y)
                    if d < dmin:
                        dmin = d
                        h = i
                im[x][y] = self.cols[h]
        return im

    def run(self):
        np = self.np
        # jitter = np.random.randint(0, 3, size=self.points.shape, dtype=np.int16) - 1
        xjitter = np.random.normal(1, 2, size=self.points.shape[0]).astype(dtype=np.int16)
        yjitter = np.random.normal(0, 1, size=self.points.shape[0]).astype(dtype=np.int16)
        self.points[:, 0] += xjitter
        self.points[:, 1] += yjitter
        self.points[:, 0] %= self.width
        self.points[:, 1] %= self.height
        if self.use_cl:
            out = self.voronoi_gpu()
            for p in self.points:
                out[p[0], p[1]] = self.lut[-1]
            return out
        return self.rand_voronoi()


if __name__ == "__main__":
    from demo import show

    # fps is 1/3 so that we get 3 seconds to admire the output before changing
    show(Runner, fps=60, cols=900, rows=900, scale=1)
