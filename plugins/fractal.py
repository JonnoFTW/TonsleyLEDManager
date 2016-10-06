class Runner:
    def __init__(self, dims):
        self.width = dims[0]
        self.height = dims[1]

        import pyopencl as cl
        from pyopencl import array
        import numpy as np
        from matplotlib import cm

        self.cm = cm
        self.np = np
        self.cl = cl

        platform = cl.get_platforms()
        my_gpu_devices = platform[0].get_devices(cl.device_type.GPU)
        self.ctx = cl.Context([my_gpu_devices[0]])
        self.queue = cl.CommandQueue(self.ctx)
        self.prg = cl.Program(self.ctx, """
            #pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable
            __kernel void mandelbrot(__global float2 *q, __constant uchar4 *lut,
                             __global uchar4 *output, ushort const maxiter)
            {
                int gid = get_global_id(0);
                float nreal, real = 0;
                float imag = 0;
                output[gid] = (uchar4)(0,0,0,0);
                for(int curiter = 0; curiter < maxiter; curiter++) {
                    nreal = real*real - imag*imag + q[gid].x;
                    imag = 2* real*imag + q[gid].y;
                    real = nreal;
                    if (real*real + imag*imag > 4.0f){
                        //output[gid] = curiter;
                        output[gid] = lut[curiter];
                        break;
                    }
                }
            }
        """).build()
        import time
        self.time = time
        self.centerx = -0.75
        self.centery = 0.1
        self.padding = 0.3
        self.maxiter = 512


        # self.xmin = -np.pi
        # self.xmax = np.pi
        # self.ymin = -np.pi
        # self.ymax = np.pi
        self.update_pos()

        cmap = self.cm.get_cmap('magma', self.maxiter + 1)
        cols = (cmap.colors * 255)[0:, :3].astype(np.uint8)
        self.lut = np.zeros((self.maxiter+1,), cl.array.vec.char3)
        for idx, i in enumerate(cols):
            self.lut[idx][0] = i[0]
            self.lut[idx][1] = i[1]
            self.lut[idx][2] = i[2]

    def update_pos(self):
        self.xmin = self.centerx - self.padding
        self.xmax = self.centerx + self.padding
        self.ymin = self.centery - self.padding
        self.ymax = self.centery + self.padding

        self.padding *= 0.99

    def mandelbrot_set3(self, xmin, xmax, ymin, ymax, width, height):
        r1 = self.np.linspace(xmin, xmax, width, dtype=self.np.float32)
        r2 = self.np.linspace(ymin, ymax, height, dtype=self.np.float32)
        c = r1 + r2[:, None] * 1j
        c = self.np.ravel(c)
        n3 = self.generate(c, self.maxiter)
        n3 = n3.reshape((width, height, 4))
        return n3[:,:,:3]
    
    def generate(self, q, maxiter):
        cl = self.cl
        mf = cl.mem_flags

        output = self.np.zeros((q.shape[0], 4), self.np.uint8)
        q_opencl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=q)
        lut_opencl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.lut)
        output_opencl = cl.Buffer(self.ctx, mf.WRITE_ONLY, output.nbytes)
        self.prg.mandelbrot(self.queue, output.shape, None, q_opencl, lut_opencl, output_opencl, self.np.uint16(maxiter))
        cl.enqueue_copy(self.queue, output, output_opencl).wait()
        return output


    def run(self):
        start = self.time.time()
        self.cells = self.mandelbrot_set3(self.xmin, self.xmax, self.ymin, self.ymax, width=self.width, height=self.height)
        # print "calculating", self.time.time() - start, self.cells.shape
        self.update_pos()

        return self.cells

if __name__ == "__main__":

    def show(Runner, arg=None, fps=24, rows=17, cols=165, scale=8):
        import pygame, sys
        FPS = fps
        fpsClock = pygame.time.Clock()

        board_dimensions = (cols, rows)

        disp_size = (cols * scale, rows * scale)
        pygame.init()
        size = width, height = board_dimensions
        screen = pygame.display.set_mode(disp_size)
        if arg is None:
            runner = Runner(board_dimensions)
        else:
            runner = Runner(board_dimensions, arg)
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
            fpsClock.tick(FPS)


    show(Runner, fps=30, rows=800, cols=800, scale=1)
