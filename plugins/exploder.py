class Runner:
    def __init__(self, dims):
        self.width = dims[0]
        self.height = dims[1]

        import numpy as np
        from matplotlib import cm
        from plugins.fonts import Font
        from datetime import datetime
        self.dt = datetime
        self.Font = Font
        self.np = np
        cmap = cm.get_cmap('magma', 256)
        self.clock = True
        self.cols = (cmap.colors * 255)[0:, :3].astype(np.uint8)
        self.minute = datetime.now().minute
        self.order = np.arange(0, 3)
        self.started = datetime.now()

    def run(self):
        np = self.np
        now = self.dt.now()
        if now.minute != self.minute:
            self.np.random.shuffle(self.order)
            self.minute = now.minute
        if (now - self.started).seconds:

            self.clock = False
        if self.clock:
            message = now.strftime("%H:%M:%S")
            fnt = self.Font('open_sans.ttf', 16)
            render = fnt.render_text(message)
            message = str(render).splitlines()
            pixels = np.zeros((self.height, max(self.width, render.width), 3), dtype=np.uint8)
            numcols = self.cols.shape[0]
            color = [(now.hour/24.*255, now.minute/60.*255, now.second/60. *255)[i] for i in self.order]
            # color = [255,255,255]
            pad = self.width/2 - len(message[0])/2
            for y in range(render.height):
                for x in range(render.width):
                    if message[y][x] == '#':
                        pixels[y+2, x+pad] = color

            return np.flipud(np.rot90(pixels, 1))
        else:
            # the clock is exploding
            pass



if __name__ == "__main__":
    from demo import show
    show(Runner, fps=30, rows=17, cols=165, scale=8)
