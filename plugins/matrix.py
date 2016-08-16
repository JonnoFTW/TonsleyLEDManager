class Runner:

    def __init__(self, dims):
        self.dims = dims
        import numpy as np
        self.np = np
        self.width = dims[0]
        self.height = dims[1]
        num_falling = 66
        self.fallers = []
        from matplotlib import cm
        self.cm = cm
        for i in xrange(num_falling):
            self.fallers.append(self.make_faller(True))

    def make_faller(self, start=False):
        if start:
            y = self.np.random.randint(0, self.height)
        else:
            y = 0
        f = dict(
            x=self.np.random.randint(0, self.width),
            y=y,
            dist=self.np.random.randint(5, 15),
            speed=max(0.2,self.np.random.normal(0.66, 0.4)),
            cmap=self.np.random.choice(['BuGn', 'Blues', 'Purples'])
        )
        f['cols'] = self.make_colors(f)
        return f

    def make_colors(self, faller):
        cmap = self.cm.get_cmap(faller['cmap'])
        return [map(lambda x: int(x * 255), list(cmap(1. * i / faller['dist']))[:-1]) for i in range(faller['dist'])]

    def run(self):

        cells = self.np.zeros((self.width, self.height, 3), dtype=self.np.uint8)
        # render the fallers on
        remove = []
        for f in self.fallers:
            f['y'] += f['speed']

            for i in xrange(f['dist']):
                try:
                    if int(f['y'])-i >= 0:
                        cells[f['x'], int(f['y']) - i] = f['cols'][i]
                except IndexError, e:
                    pass
            if f['y'] - f['dist'] > self.height:
                remove.append(f)
                self.fallers.append(self.make_faller())
        map(self.fallers.remove, remove)
        return cells

if __name__ == "__main__":
    from demo import show
    show(Runner, fps=24)
