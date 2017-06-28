from matplotlib import pyplot as plt
from matplotlib import colors
class Runner:
    def __init__(self, dims):
        self.width = dims[0]
        self.height = dims[1]

        import pyopencl as cl
        from pyopencl import cltypes
        import numpy as np
        from matplotlib import cm

        self.cm = cm
        self.np = np
        self.cl = cl

        self.ctx = cl.Context([cl.get_platforms()[1].get_devices()[0]])
        self.queue = cl.CommandQueue(self.ctx)
        self.prg = cl.Program(self.ctx, """
            #pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable
            __kernel void mandelbrot(__global float2 *q, __constant uchar4 *lut,
                             __global uchar4 *output, __global uint* output2, uint const maxiter)
            {
                const int gid = get_global_id(0);
                float real = q[gid].x;
                float imag = q[gid].y;
                output[gid] = (uchar4)(0,0,0,0);
                output2[gid] = 0;
                for(uint curiter = 0; curiter < maxiter; curiter++) {
                    float real2 = real*real, imag2 = imag*imag;
                    if (real2 + imag2 > 4.0f) {
                        output[gid] = lut[curiter];
                        output2[gid] = curiter;
                        return;
                    }
                    imag = 2 * real*imag + q[gid].y;
                    real = real2 - imag2 + q[gid].x;
                }
            }
        """).build()
        import time
        self.time = time
        self.centerx = (-0.74877 + -0.74872) / 2
        self.centery = (0.06505 + 0.06510) / 2
        self.padding = 2
        self.maxiter = cltypes.uint(64)

        # self.xmin = -np.pi
        # self.xmax = np.pi
        # self.ymin = -np.pi
        # self.ymax = np.pi
        self.update_pos()

        cmap = self.cm.get_cmap('gnuplot2', self.maxiter)
        cols = [(np.array(cmap(i)[:-1]) * 255).astype(cl.cltypes.uchar) for i in range(self.maxiter)]
        self.lut = np.zeros((self.maxiter,), cl.cltypes.uchar4)
        for idx, i in enumerate(cols):
            self.lut[idx][0] = i[0]
            self.lut[idx][1] = i[1]
            self.lut[idx][2] = i[2]
        self.lut_opencl = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.lut)

    def update_pos(self):
        self.xmin = self.centerx - self.padding
        self.xmax = self.centerx + self.padding
        self.ymin = self.centery - self.padding
        self.ymax = self.centery + self.padding

        self.padding *= 0.99

    def mandelbrot_set3(self, xmin, xmax, ymin, ymax, width, height):
        r1 = self.np.linspace(xmin, xmax, width, dtype=self.cl.cltypes.float)
        r2 = self.np.linspace(ymin, ymax, height, dtype=self.cl.cltypes.float)
        c = r1 + r2[:, None] * 1j
        c = self.np.ravel(c)
        n3, out2 = self.generate(c, self.maxiter)
        out2 = out2.reshape(width, height)
        # return n3
        # self.show_mandle(self.xmin,self.xmax,self.ymin,self.ymax,r1,r2,out2)
        n3 = n3.reshape((width, height, 4))
        return n3[:,:,:3]

    def show_mandle(self, xmin,xmax,ymin,ymax,x,y,z,width=3,height=3,maxiter=80,cmap='hot'):
        dpi = 2
        img_width = dpi * width
        img_height = dpi * height

        np = self.np
        # x, y, z = mandelbrot_set(xmin, xmax, ymin, ymax, img_width, img_height, maxiter)
        fig, ax = plt.subplots(figsize=(width, height), dpi=72)
        ticks = np.arange(0, img_width, 3 * dpi)
        x_ticks = xmin + (xmax - xmin) * ticks / img_width
        plt.xticks(ticks, x_ticks)
        y_ticks = ymin + (ymax - ymin) * ticks / img_height
        plt.yticks(ticks, y_ticks)

        norm = colors.PowerNorm(0.3)
        ax.imshow(z, cmap=cmap, origin='lower', norm=norm)
        raw_input()

    def generate(self, q, maxiter):
        cl = self.cl
        mf = cl.mem_flags

        output = self.np.zeros((q.shape[0], 4), cl.cltypes.uchar)
        output2 = self.np.zeros(q.shape[0], cl.cltypes.uint)
        q_opencl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=q)
        output2_opencl = cl.Buffer(self.ctx, mf.WRITE_ONLY, output2.nbytes)
        output_opencl = cl.Buffer(self.ctx, mf.WRITE_ONLY, output.nbytes)
        self.prg.mandelbrot(self.queue, output.shape, None, q_opencl,
                            self.lut_opencl,
                            output_opencl,
                            output2_opencl,
                            maxiter).wait()
        cl.enqueue_copy(self.queue, output2, output2_opencl)
        # return self.lut[output2]

        cl.enqueue_copy(self.queue, output, output_opencl).wait()
        return output, output2

    def run(self):
        start = self.time.time()
        self.cells = self.mandelbrot_set3(self.xmin, self.xmax, self.ymin, self.ymax, width=self.width,
                                          height=self.height)
        # print "calculating", self.time.time() - start, self.cells.shape
        self.update_pos()

        return self.cells, "{:.2f} - {:.2f}\n{:.2f} - {:.2f}".format(self.xmin, self.xmax, self.ymin, self.ymax)


if __name__ == "__main__":
    from demo import show

    show(Runner, fps=90, rows=900, cols=900, scale=1)
