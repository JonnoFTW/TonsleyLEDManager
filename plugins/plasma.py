class Runner:
    def __init__(self, dims):
        self.width = dims[0]
        self.height = dims[1]
        import numpy as np
        from matplotlib import cm
        from itertools import cycle
        self.np = np

        color_maps = ['inferno', 'gnuplot', 'magma', 'viridis', 'plasma', 'cubehelix', 'gnuplot2', 'ocean', 'terrain',
                      'CMRmap', 'nipy_spectral']
        maps = [
            np.array(map(lambda i: (np.array(cm.get_cmap(x, 256)(i)[:-1]) * 255).astype(np.uint8), np.arange(0, 256)))
            for x in color_maps]

        # tup = []
        # for m in maps:
        #     tup.extend([m, m[::-1]])
        tup = (
            maps[0], maps[0][::-1], maps[1], maps[1][::-1], maps[2], maps[2][::-1], maps[5], maps[5][::-1], maps[3],
            maps[4][::-1], maps[6], maps[7][::-1], maps[8], maps[9][::-1], maps[10], maps[10][::-1])
        self.cols = np.concatenate(tup)
        self.cols = np.concatenate((self.cols, self.cols[::-1]))
        self.step = 0
        # print("Colors length:", len(self.cols))
        denoms = np.cos(np.arange(0, 3 * np.pi, 0.01)) + (2*np.pi)
        self.denom = cycle(denoms)
        self.up = True
        self.half_len = len(self.cols) / 64.
        # print("Half length", self.half_len)
        self.init_gpu()

    def init_gpu(self):
        self.use_cl = False
        try:
            import pyopencl as cl
            from pyopencl import array
        except Exception, e:
            import traceback
            traceback.print_exc()
            return
        self.use_cl = True
        self.cl = cl
        self.ctx = cl.Context([cl.get_platforms()[1].get_devices()[0]])
        self.queue = cl.CommandQueue(self.ctx)
        self.lut = self.np.empty(len(self.cols), cl.array.vec.char3)
        for idx, i in enumerate(self.cols):
            self.lut[idx][0] = i[0]
            self.lut[idx][1] = i[1]
            self.lut[idx][2] = i[2]
        mf = cl.mem_flags
        self.lut_opencl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.lut)

        self.prg = cl.Program(self.ctx, """
               __kernel void plasma(__global uchar4 *img, __constant uchar4 *lut, float const denom, uint step,
                                         uint const height, uint const width, uint const colours) {{
                   const int x = get_global_id(0);
                   const int y = get_global_id(1);
                   const int index = y * height + x;
                   const float half_len = {0};
                   const int h = step + half_len + (half_len * {1}sin((float){1}sqrt(pow(x - width / 2.,2)+ pow(y - height / 2.,2)) / denom));
                   if( h  < colours) {{
                       img[index] = lut[h];
                   }} else {{
                       img[index] = lut[colours - h];
                   }}
               }}
           """.format(self.half_len, 'native_')).build()

    def plasma_gpu(self):
        np = self.np
        cl = self.cl
        # print "doing gpu"
        mf = cl.mem_flags
        img = np.zeros((self.width * self.height, 4), self.np.uint8)
        img_opencl = cl.Buffer(self.ctx, mf.WRITE_ONLY, img.nbytes)

        self.prg.plasma(self.queue, (self.height, self.width), None, img_opencl, self.lut_opencl,
                        np.float32(self.denom.next()),
                        np.uint32(self.step), np.uint32(self.height), np.uint32(self.width), np.uint32(len(self.cols)))

        cl.enqueue_copy(self.queue, img, img_opencl).wait()
        return img.reshape((self.width, self.height, 4))[:, :, :3]

    def run(self):
        # return self.plasma_gpu()
        np = self.np
        w = self.width
        h = self.height
        step = 5
        if not self.use_cl:
            half_len = self.half_len
            img = np.empty((self.width, self.height, 3), dtype=np.uint8)
            denom = self.denom.next()
            for y in xrange(0, self.height):
                for x in xrange(0, self.width):
                    col = int(half_len + (
                        half_len * np.sin(np.sqrt((x - w / 2.0) **2 + (y - h / 2.0) **2) / denom)))
                    if col + self.step < len(self.cols):
                        img[x][y] = self.cols[(col + self.step)]
                    else:
                        img[x][y] = self.cols[len(self.cols) - (col + self.step)]
        else:
            img = self.plasma_gpu()
        self.step += step
        self.step %= len(self.cols)

        return img


if __name__ == "__main__":
    from demo import show

    show(Runner, fps=90, rows=1000, cols=2000, scale=1)
