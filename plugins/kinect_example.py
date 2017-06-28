import pygame
import numpy as np
import pyopencl as cl
import sys
from freenect import sync_get_depth as get_depth


def make_gamma():
    """
    Create a gamma table
    """
    num_pix = 2048
    npf = float(num_pix)
    _gamma = np.empty((num_pix, 3), dtype=np.uint16)
    for i in xrange(num_pix):
        v = i / npf
        v = pow(v, 3) * 6
        pval = int(v * 6 * 256)
        lb = pval & 0xff
        pval >>= 8
        if pval == 0:
            a = np.array([255, 255 - lb, 255 - lb], dtype=np.uint8)
        elif pval == 1:
            a = np.array([255, lb, 0], dtype=np.uint8)
        elif pval == 2:
            a = np.array([255 - lb, lb, 0], dtype=np.uint8)
        elif pval == 3:
            a = np.array([255 - lb, 255, 0], dtype=np.uint8)
        elif pval == 4:
            a = np.array([0, 255 - lb, 255], dtype=np.uint8)
        elif pval == 5:
            a = np.array([0, 0, 255 - lb], dtype=np.uint8)
        else:
            a = np.array([0, 0, 0], dtype=np.uint8)

        _gamma[i] = a
    return _gamma


gamma = make_gamma()

ctx = cl.Context([cl.get_platforms()[1].get_devices()[0]])
queue = cl.CommandQueue(ctx)
prg = cl.Program(ctx, """
__kernel void depth2colour(
    __constant ushort* depth,
    __constant ushort* gamma,
     __global uchar4* depth_mid
 ) {
     const int x = get_global_id(0);
     const int y = get_global_id(1);
     const int height = get_global_size(0);
     const int i = y*height + x;
     const int pval = gamma[depth[i]];
     const int lb = pval & 0xff;
     switch (pval>>8) {
         case 0:
             depth_mid[i].x = 255;
             depth_mid[i].y = 255-lb;
             depth_mid[i].z = 255-lb;
             break;
         case 1:
             depth_mid[i].x = 255;
             depth_mid[i].y = lb;
             depth_mid[i].z = 0;
             break;
         case 2:
             depth_mid[i].x = 255-lb;
             depth_mid[i].y = 255;
             depth_mid[i].z = 0;
             break;
         case 3:
             depth_mid[i].x = 0;
             depth_mid[i].y = 255;
             depth_mid[i].z = lb;
             break;
         case 4:
             depth_mid[i].x = 0;
             depth_mid[i].y = 255-lb;
             depth_mid[i].z = 255;
             break;
         case 5:
             depth_mid[i].x = 0;
             depth_mid[i].y = 0;
             depth_mid[i].z = 255-lb;
             break;
         default:
             depth_mid[i].x = 0;
             depth_mid[i].y = 0;
             depth_mid[i].z = 0;
             break;
     }
 }
 """).build()
mf = cl.mem_flags
cl_gamma = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=gamma)


def depth_2_image_cl(depth):
    out = np.zeros((depth.shape[0] * depth.shape[1], 4), dtype=np.uint8)
    cl_out = cl.Buffer(ctx, mf.WRITE_ONLY, out.nbytes)
    cl_depth = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=depth)
    prg.depth2colour(queue, (depth.shape[0], depth.shape[1]), None, cl_depth, cl_gamma, cl_out).wait()

    cl.enqueue_copy(queue, out, cl_out).wait()
    out = out.reshape((depth.shape[0], depth.shape[1], 4))[:, :, :3]
    return out


if __name__ == "__main__":
    fpsClock = pygame.time.Clock()
    FPS = 120
    disp_size = (640, 480)
    pygame.init()
    screen = pygame.display.set_mode(disp_size)
    font = pygame.font.Font('slkscr.ttf', 32)
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit()
        fps_text = "FPS: {0:.2f}".format(fpsClock.get_fps())
        # draw the pixels

        depth = np.rot90(get_depth()[0])
        pixels = gamma[depth]
        # pixels = depth_2_image_cl(depth)
        temp_surface = pygame.Surface(disp_size)
        pygame.surfarray.blit_array(temp_surface, pixels)
        pygame.transform.scale(temp_surface, disp_size, screen)
        screen.blit(font.render(fps_text, 1, (255, 255, 255)), (30, 30))
        pygame.display.flip()
        fpsClock.tick(FPS)
