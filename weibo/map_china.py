import pandas as pd
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

im = np.array(Image.open('./res/map.jpg').convert('L'))
plt.figure()
plt.gray()
plt.imshow(im)
#plt.show()
file = open('./res/map_data','r')
x = []
y = []
for data in file:
    location_x = data.strip('\n').split(',')[-2]
    location_y = data.strip('\n').split(',')[-1]
    x.append(float(location_x))
    y.append(float(location_y))
file.close()

plt.plot(x,y,'r.')
plt.show()


