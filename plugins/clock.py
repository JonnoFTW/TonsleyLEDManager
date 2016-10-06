
class Runner:
    def __init__(self, dims):
        self.width = dims[0]
        self.height = dims[1]
        try:
            from plugins.fonts import Font
        except ImportError:
            from fonts import Font
        import numpy as np
        from matplotlib import cm
        from datetime import datetime
        self.dt = datetime
        self.np = np
        cmap = cm.get_cmap('magma', 256)

        self.cols = (cmap.colors * 255)[0:, :3].astype(np.uint8)
        self.minute = datetime.now().minute
        self.order = np.arange(0, 3)
        try:
            self.fnt = Font('slkscr.ttf', 16)
        except:
            import urllib
            print("Downloading font")
            urllib.urlretrieve('https://www.dropbox.com/s/adt959l9bx0ojlj/slkscr.ttf?dl=1', 'slkscr.ttf')
            self.fnt = Font('slkscr.ttf', 16)

    def run(self):
        np = self.np
        now = self.dt.now()
        if now.minute != self.minute:
            self.np.random.shuffle(self.order)
            self.minute = now.minute
        message = now.strftime("%H:%M:%S")

        render = self.fnt.render_text(message)
        message = str(render).splitlines()
        pixels = np.zeros((self.height, max(self.width, render.width), 3), dtype=np.uint8)
        numcols = self.cols.shape[0]
        color = [(now.hour/24.*255, now.minute/60.*255, now.second/60. * 255)[i] for i in self.order]
        # color = [255,255,255]
        pad = 45 #self.width/2 - len(message[0])/2
        for y in range(render.height):
            for x in range(render.width):
                if message[y][x] == '#':
                    pixels[y+3, x+pad] = color
        return np.flipud(np.rot90(pixels, 1))


if __name__ == "__main__":
    from demo import show
    show(Runner, fps=30, rows=17, cols=165, scale=8)