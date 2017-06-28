import numpy as np
import pygame

sharpen = np.array((
    [0, -1, 0],
    [-1, 5, -1],
    [0, -1, 0]), dtype="int")
laplacian = np.array((
    [0, 1, 0],
    [1, -4, 1],
    [0, 1, 0]), dtype="int")

# construct the Sobel x-axis kernel
sobelX = np.array((
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]), dtype="int")

# construct the Sobel y-axis kernel
sobelY = np.array((
    [-1, -2, -1],
    [0, 0, 0],
    [1, 2, 1]), dtype="int")
smallBlur = np.ones((3, 3), dtype="float") * (1.0 / (3 * 3))
largeBlur = np.ones((21, 21), dtype="float") * (1.0 / (21 * 21))

import cv2


def makeKernel(img_height, img_width, kernel_width):
    code = """
__kernel void onvolve(const __global float4* imgIn,
                       __constant float* filter,
                       __global float* imgOut,
                       const int filterWidth,
                       const int halfFilterWidth) {
    const int imgWidth = get_global_size(0);
    const int imgHeight = get_global_size(1);
    const int x = get_global_id(0);
    const int y = get_global_id(1);
    float sum = 0;
    const float4 facs = (0.299, 0.587, 0.114, 0);
    // center convolution around x,y
    for(int fx = x-halfFilterWidth; fx < x+halfFilterWidth; fx++) {
        for(int fy= y-halfFilterWidth; r < y+halfFilterWidth; fy++) {
            sum += dot(facs, imgIn[fx][fy]) ;//* filter[fx*filterWidth+x + fy-y];
        }
    }
    imgOut[y * imgHeight + x] = sum;
}
"""
    import pyopencl as cl
    ctx = cl.Context([cl.get_platforms()[0].get_devices()[0]])
    prg = cl.Program(ctx, code).build()
    queue = cl.CommandQueue(ctx)
    return ctx, prg, queue


def convolutionCL(img, filter, ctx, cl, prg, queue):
    # pad out the image
    # copy floor(imgWidth/2) pixels top+bottom
    # copy floor(imgHeight/2) pixels left+right
    width, height = img.shape
    filterWidth = filter.shape[0]
    imgExtra = np.floor(filterWidth / 2.)

    np.pad(img, imgExtra, 'edge')
    imgOut = np.empty((width, height), np.uint8)

    mf = cl.mem_flags
    imgOut_opencl = cl.Buffer(ctx, mf.WRITE_ONLY, imgOut.nbytes)
    imgIn_opencl = cl.Buffer(ctx.mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img)
    prg.convolve(queue, (height, width), None, imgIn_opencl, imgOut_opencl, np.int32(filterWidth), np.int32(imgExtra))

    cl.enqueue_copy(queue, imgOut, imgOut_opencl).wait()
    return img.reshape((width, height, 4))[:, :, :3]


class Runner:
    def __init__(self, board_dimensions):
        self.board_dimensions = board_dimensions
        self.width = board_dimensions[0]
        self.height = board_dimensions[1]
        import numpy as np

        self.cv2 = cv2
        self.np = np
        self.kernelBank = dict([
            ("small_blur", smallBlur),
            ("large_blur", largeBlur),
            ("sharpen", sharpen),
            ("laplacian", laplacian),
            ("sobel_x", sobelX),
            ("sobel_y", sobelY)])
        # self.isKinect = False
        # from freenect import sync_get_video as get_video, sync_get_depth as get_depth
        self.gv = None # get_video
        # self.gd = get_depth

        # if self.gv() is None:
        #     print("no kinect camera")
        self.camera = cv2.VideoCapture(0)
        if self.camera.isOpened():
                self.gv = self.get_camera
                print("Using regular camera")
        else:
            raise EnvironmentError("No camera available")
        self.isKinect = False
        # else:
        #     self.isKinect = True
        num_pix = 2048
        npf = float(num_pix)
        self.gamma = np.empty((num_pix,), dtype=np.uint16)
        for i in xrange(num_pix):
            v = i / npf
            v = pow(v, 3) * 6
            self.gamma[i] = v * 6 * 256
        self.kernels = self.kernelBank.keys()
        self.next_kernel()
        self.avg = None
        self.prepared = False


    def get_camera(self):
        collected, frame = self.camera.read()
        self.gd = lambda: [None]
        return [frame]

    def next_kernel(self):
        name = self.kernels.pop(0)
        self.kernel = self.kernelBank[name]
        self.kernels.append(name)

    def depth2colour(self, depth):
        if not self.prepared:
            self.prepared = True
            import pyopencl as cl
            import pyopencl.array
            self.cl = cl
            self.ctx = cl.Context([cl.get_platforms()[0].get_devices()[1]])


            self.queue = cl.CommandQueue(self.ctx)
            self.prg = cl.Program(self.ctx, """__kernel void depth2colour(__constant ushort* depth, __constant ushort* gamma, __global uchar4* depth_mid) {
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
            self.cl_gamma = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.gamma)
        cl = self.cl
        np = self.np
        mf = cl.mem_flags
        out = np.zeros((depth.shape[0] * depth.shape[1], 4), dtype=self.np.uint8)
        cl_out = cl.Buffer(self.ctx, mf.WRITE_ONLY, out.nbytes)
        cl_depth = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=depth)
        self.prg.depth2colour(self.queue, (depth.shape[0], depth.shape[1]), None, cl_depth, self.cl_gamma, cl_out)

        self.cl.enqueue_copy(self.queue, out, cl_out).wait()
        out = out.reshape((depth.shape[0], depth.shape[1], 4))[:,:,:3]
        return out

    def run(self, events=None):
        np = self.np
        cv2 = self.cv2
        # if events is not None:
        #     for event in events:
        #         if event.type == pygame.KEYUP:
        #             if event.key == pygame.K_UP:
        #                 self.kernel = np.rot90(self.kernel)
        #             elif event.key == pygame.K_RIGHT:
        #                 self.next_kernel()
        #             elif event.key == pygame.K_DOWN:
        #                 self.kernel = np.roll(self.kernel, 1, axis=0)

        frame = (np.flipud(np.rot90(self.gv()[0])))

        if self.isKinect:
            depth = cv2.resize(np.rot90(self.gd()[0]), (self.height, self.width), interpolation=cv2.INTER_CUBIC)
            frame = self.depth2colour(depth)

            return frame, ''
        img = np.zeros((self.width, self.height, 3), dtype=np.uint8)
        # return frame, ''
        frame = cv2.UMat(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # gray = cv2.filter2D(gray, 0,
        # self.kernel)
        #
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        # framecopy = frame.copy()
        # self.frame_count += 1
        # if self.frame_count > 1000:
        #
        #     self.frame_count = 0
        #     self.firstFrame = gray

        if self.avg is None:
            self.avg = gray.get().copy().astype('float')
            out = np.zeros((self.width, self.height, 3), dtype=np.uint8)
            self.last_frame = out
            return out, 'fst'

        cv2.accumulateWeighted(gray, self.avg, 0.6)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))
        # frameDelta = cv2.absdiff(self.firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=3)
        outFrame = cv2.cvtColor(cv2.resize(thresh, (self.height, self.width), interpolation=cv2.INTER_CUBIC),
                                cv2.COLOR_GRAY2RGB)
        toOut = outFrame | self.last_frame
        self.last_frame = outFrame
        return toOut, ''

        # res = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # contours, heirarchy = res[0], res[1]
        # for cnt in heirarchy:
        #     if cv2.contourArea(cnt) > 400:
        #         [x, y, w, h] = cv2.boundingRect(cnt)
        #         cv2.rectangle(framecopy, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #         # rect = cv2.minAreaRect(cnt)
        #         # box = cv2.boxPoints(rect)
        #         # box = np.int0(box)
        #         # cv2.drawContours(framecopy, [box], -1, (0, 255, 0), 2)
        #
        # # framecopy = cv2.resize(framecopy, (self.height, self.width), interpolation=cv2.INTER_LANCZOS4)
        # return framecopy, str(self.kernel)


# from flask import Flask, render_template, Response
#
# app = Flask('KinectStream')
#
#
# @app.route('/')
# def index():
#     return """
# <html>
#   <head>
#     <title>Video Streaming Demonstration</title>
#   </head>
#   <body>
#     <h1>Video Streaming Demonstration</h1>
#     <img id="bg" src="/video_feed">
#   </body>
# </html>
#     """
#
#
# def gen(camera):
#     while 1:
#         frame = camera.run(None)[0]
#         frame = cv2.cvtColor(np.flipud(np.rot90(frame)), cv2.COLOR_RGB2BGR)
#
#         jpeg = cv2.imencode('.jpg', frame)[1]
#         # print jpeg
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
#
#
# @app.route('/video_feed')
# def video_feed():
#     return Response(gen(Runner([480, 640])),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')
#

if __name__ == "__main__":
    # app.run(host='0.0.0.0', debug=True)
    from demo import show

    show(Runner, fps=30, rows=480, cols=640, scale=2, withArgs=True)
    # show(Runner, fps=30, rows=17, cols=165, scale=9, withArgs=True)
