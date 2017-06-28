from matplotlib import cm
from PIL import Image
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

color_maps = [ 'inferno', 'gnuplot', 'magma', 'viridis', 'plasma','cubehelix', 'gnuplot2', 'ocean', 'terrain', 'CMRmap', 'nipy_spectral']
maps = [np.array(map(lambda i: (np.array(cm.get_cmap(x, 256)(i)[:-1])* 255).astype(np.uint8), np.arange(0, 256))) for x in color_maps]
tup = []
# for idx, m in enumerate(maps):
#     if idx % 2 == 0:
#         tup.extend([m, m[::-1]])
#     else:
#         tup.extend([m[::-1], m])
# print len(tup)
tup = (maps[0], maps[0][::-1],maps[1], maps[1][::-1], maps[2], maps[2][::-1],maps[5],maps[5][::-1], maps[3], maps[4][::-1], maps[6],maps[7][::-1],maps[8],maps[9][::-1], maps[10],maps[10][::-1] )
cols = np.concatenate(tup)
cols = np.concatenate((cols, cols[::-1]))
l = cols.shape[0]
width = 500
plt.imshow(np.rot90(np.tile(cols, width).reshape(l, width, 3)))
plt.show()
