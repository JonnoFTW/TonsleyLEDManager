import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
import pyopencl as cl

ctx = cl.Context([cl.get_platforms()[1].get_devices()[0]])


def mandelbrot_gpu(q, maxiter):

    queue = cl.CommandQueue(ctx)

    output = np.empty(q.shape, dtype=np.uint16)

    prg = cl.Program(ctx, """
    #pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable
    __kernel void mandelbrot(__global float2 *q,
                     __global ushort *output, ushort const maxiter)
    {
        int gid = get_global_id(0);
        float real = q[gid].x;
        float imag = q[gid].y;
        output[gid] = 0;
        for(int curiter = 0; curiter < maxiter; curiter++) {
            float real2 = real*real, imag2 = imag*imag;
            if (real*real + imag*imag > 4.0f){
                 output[gid] = curiter;
                 return;
            }
            imag = 2* real*imag + q[gid].y;
            real = real2 - imag2 + q[gid].x;

        }
    }
    """).build()

    mf = cl.mem_flags
    q_opencl = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=q)
    output_opencl = cl.Buffer(ctx, mf.WRITE_ONLY, output.nbytes)

    prg.mandelbrot(queue, output.shape, None, q_opencl,
                   output_opencl, np.uint16(maxiter))

    cl.enqueue_copy(queue, output, output_opencl).wait()

    return output


def mandelbrot_set3(xmin, xmax, ymin, ymax, width, height, maxiter):
    r1 = np.linspace(xmin, xmax, width, dtype=np.float32)
    r2 = np.linspace(ymin, ymax, height, dtype=np.float32)
    c = r1 + r2[:, None] * 1j
    c = np.ravel(c)
    n3 = mandelbrot_gpu(c, maxiter)
    n3 = n3.reshape((width, height))
    return r1, r2, n3.T


def mandelbrot_image(xmin, xmax, ymin, ymax, width=3, height=3, maxiter=80, cmap='hot'):
    dpi = 128
    img_width = dpi * width
    img_height = dpi * height
    x, y, z = mandelbrot_set3(xmin, xmax, ymin, ymax, img_width, img_height, maxiter)

    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    ticks = np.arange(0, img_width, 3 * dpi)
    x_ticks = xmin + (xmax - xmin) * ticks / img_width
    plt.xticks(ticks, x_ticks)
    y_ticks = ymin + (ymax - ymin) * ticks / img_height
    plt.yticks(ticks, y_ticks)

    norm = colors.PowerNorm(0.4)
    ax.imshow(z.T, cmap=cmap, origin='lower', norm=norm)


mandelbrot_set = mandelbrot_set3
mandelbrot_image(-2.0, 0.5, -1.25, 1.25, width=30, height=30,maxiter=4096, cmap='gnuplot')
plt.show()