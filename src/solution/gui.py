

import matplotlib.pyplot as plt
import numpy as np
from math import trunc

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


