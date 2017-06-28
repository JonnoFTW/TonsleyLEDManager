from PIL import Image
import numpy as np
import random
from collections import defaultdict, Counter


class Runner(object):
    def __init__(self, dimensions, bucket_size=10, four_neighbour=True):
        self.weights = defaultdict(Counter)
        self.bucket_size = bucket_size
        self.four_neighbour = four_neighbour
        self.width, self.height = dimensions

        self.np = np
        self.reset()

    def reset(self):
        self.state = 'TRAIN'
        fname = np.random.choice(
            ['http://i.imgur.com/XS5Qj0X.jpg', 'http://i.imgur.com/ql46UZL.png', 'http://i.imgur.com/rmT9j7f.jpg',
             'http://i.imgur.com/BDj1NGO.png'])
        if fname.startswith('http'):
            import requests, cStringIO
            self.train_img = Image.open(cStringIO.StringIO(requests.get(fname).content))

        else:
            self.train_img = Image.open(fname)
        self.train_it = self.train()
        self.gen_it = self.generate()

        self.train_it = self.train()
        self.gen_it = self.generate()

    def normalize(self, pixel):
        return pixel // self.bucket_size

    def denormalize(self, pixel):
        return pixel * self.bucket_size

    def get_neighbours(self, x, y):
        if self.four_neighbour:
            return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        else:
            return [(x + 1, y),
                    (x - 1, y),
                    (x, y + 1),
                    (x, y - 1),
                    (x + 1, y + 1),
                    (x - 1, y - 1),
                    (x - 1, y + 1),
                    (x + 1, y - 1)]

    def train(self):
        """
        Train on the input PIL image
        :param img:
        :return:
        """
        np = self.np
        img = self.train_img
        width, height = img.size
        img_out = img.resize((self.width, self.height), Image.ANTIALIAS)
        img_out = np.rot90(np.array(img_out)[:, :, :3])
        img = np.array(img)[:, :, :3]
        print ("img_out size:" + str(img_out.shape))
        num_pix = width * height
        # prog = pyprind.ProgBar(num_pix, width=64, stream=1)
        i = 0
        for x in range(height):
            for y in range(width):
                # get the left, right, top, bottom neighbour pixels
                pix = tuple(self.normalize(img[x, y]))
                # prog.update()
                # print("reading pixel"+str(x*height +y)+"/"+str(width*height))
                for neighbour in self.get_neighbours(x, y):
                    try:
                        self.weights[pix][tuple(self.normalize(img[neighbour]))] += 1
                    except IndexError:
                        continue
                # calculate the percentage of the way through the image we are and mark that pixel black
                pct = (x * height + y) / num_pix
                try:
                    img_out[np.int(float(y) / width * self.width), np.int(float(x) / height * self.height), ] = [0, 0, 0]
                except:
                    pass
                i += 1
                if i % 1000 == 0:
                    yield img_out
        self.state = 'RUN'

    def generate(self, initial_state=None):
        np = self.np
        width, height = self.width, self.height
        if initial_state is None:
            initial_state = random.choice(list(self.weights.keys()))
        if type(initial_state) is not tuple and len(initial_state) != 3:
            raise ValueError("Initial State must be a 3-tuple")
        img = Image.new('RGB', (width, height), 'black')
        img = np.array(img)
        img_out = np.array(img.copy())
        print("generating")
        # start filling out the image
        # start at a random point on the image, set the neighbours and then move into a random, unchecked neighbour,
        # only filling in unmarked pixels
        initial_position = (np.random.randint(0, height), np.random.randint(0, width))
        img[initial_position] = initial_state
        stack = [initial_position]
        coloured = set()
        while stack:
            x, y = stack.pop()
            if (x, y) in coloured:
                continue
            else:
                coloured.add((x, y))
            try:
                cpixel = img[x, y]
                node = self.weights[tuple(cpixel)]  # a counter of neighbours
                img_out[x, y] = self.denormalize(cpixel)
                yield np.rot90(img_out)
            except IndexError:
                continue

            keys = list(node.keys())
            neighbours = self.get_neighbours(x, y)
            counts = np.array(list(node.values()), dtype=np.float32)
            key_idxs = np.arange(len(keys))
            ps = counts / counts.sum()
            np.random.shuffle(neighbours)
            for neighbour in neighbours:
                try:
                    col_idx = np.random.choice(key_idxs, p=ps)
                    if neighbour not in coloured:
                        img[neighbour] = keys[col_idx]
                except IndexError:
                    pass
                except ValueError:
                    continue
                if 0 <= neighbour[0] < height and 0 <= neighbour[1] < width:
                    stack.append(neighbour)
        print("finished")
        self.state = 'DONE'

    def run(self):
        # resize the original image
        if self.state == 'TRAIN':
            try:
                return self.train_it.next()
            except StopIteration:
                pass
        if self.state == 'RUN':
            try:
                self.img = self.gen_it.next()
                return self.img
            except StopIteration:
                pass
        if self.state == 'DONE':
            self.reset()
            return self.img


if __name__ == "__main__":
    from demo import show

    show(Runner, fps=30, rows=17, cols=165, scale=8)
