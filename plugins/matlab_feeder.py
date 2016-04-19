import SocketServer
from threading import Thread


class SocketThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(SocketThread, self).__init__(group=group, target=target,
                                       name=name, verbose=verbose)
        self.args = args
        self.kwargs = kwargs
        connection = ('localhost', 7891)
        print "Listening on {}".format(connection)
        self.server = SocketServer.TCPServer(connection, args[0])

    def run(self):
        self.server.serve_forever()

    def join(self, timeout=None):
        self.server.shutdown()
        self.server.server_close()
        super(SocketThread, self).join(timeout)

import struct

class Runner:

    def __init__(self, board_dimensions):
        self.board_dimensions = board_dimensions
        import numpy as np
        self.np = np
        self.pixels = self.np.zeros((self.board_dimensions[1], self.board_dimensions[0], 3), dtype=self.np.uint8)
        self.buffer = self.np.zeros((self.board_dimensions[1], self.board_dimensions[0], 3), dtype=self.np.uint8)
        def chunks(l, n):
            n = max(1, n)
            return [l[i:i + n] for i in range(0, len(l), n)]

        class MyTCPHandler(SocketServer.BaseRequestHandler):
            def handle(cls):
                # self.request is the TCP socket connected to the client
                header = cls.request.recv(4)
                header = struct.unpack('BBH', header)
                data = struct.unpack('B'*(165*3), cls.request.recv(165*3))

                self.buffer[header[0]-1] = np.array(chunks(data, 3), dtype=np.uint8)
                if header[0] == 17:
                    np.copyto(self.pixels, self.buffer)

        self.socket_thread = SocketThread(args=(MyTCPHandler,))
        self.socket_thread.start()



    def finish(self):
        # shut that whole thing down
        self.socket_thread.join()

    def run(self):
        # read all the pixels currently in the buffer the buffer and send them
        return self.np.flipud(self.np.rot90(self.pixels))

if __name__ == "__main__":
    import pygame, sys, atexit
    FPS = 60
    fpsClock = pygame.time.Clock()
    rows = 17
    cols = 165
    board_dimensions = (cols, rows)

    disp_size = (cols * 8, rows * 8)
    pygame.init()
    size = width, height = board_dimensions
    screen = pygame.display.set_mode(disp_size)
    runner = Runner(board_dimensions)
    def onexit():
        runner.finish()
    atexit.register(onexit)
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
