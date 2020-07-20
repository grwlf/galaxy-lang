

import matplotlib.pyplot as plt
import numpy as np
from math import trunc
from ipdb import set_trace

def test_gui():
  try:
    data = np.random.random(size=(10, 10))
    plt.xticks(np.arange(0.0, 2.5, 1), np.arange(0.5, 2, 0.5))
    plt.yticks(np.arange(2, -0.5, -1), np.arange(0.5, 2, 0.5))
    plt.imshow(data)
    inps=plt.ginput(n=4, timeout=10)
    print(inps)
    for inp in inps:
      print([round(x) for x in inp])
  finally:
    plt.close()


def showimg(img):
  maxx=max([x for x,_ in img])
  maxy=max([x for x,_ in img])
  minx=min([x for x,_ in img])
  miny=min([x for x,_ in img])
  data = np.zeros([maxx-minx+1,maxy-miny+1])
  for (x,y) in img:
    data[x-minx,y-miny]=1
  try:
    # plt.xticks(np.arange(0.0, 2.5, 1), np.arange(0.5, 2, 0.5))
    # plt.yticks(np.arange(2, -0.5, -1), np.arange(0.5, 2, 0.5))
    plt.imshow(data)
    inps=plt.ginput(n=1, timeout=0)
    print('User input:\n', inps)
    for inp in inps:
      print([round(x) for x in inp])
  finally:
    plt.close()
