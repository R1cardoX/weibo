import pandas as pd
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
im = np.array(Image.open('./res/map.jpg').convert('L'))

plt.figure()
plt.gray()
plt.imshow(im)
file1 = open('./res/city','r')
locations = []
city_data = []
for city in file1.readlines():
    city_name = city.strip('\n')
    print("click the city",city_name)
    location = plt.ginput(3)
    print(location)
    location_x = (location[0][0] + location[1][0] + location[2][0])/3
    location_y = (location[0][1] + location[1][1] + location[2][1])/3
    print("get the city:",city_name,"\tlocation x:",location_x,"location y",location_y)
    location = city_name + ',' + str(location_x) + ',' + str(location_y) + '\n'
    print("\n",location)
    locations.append(location)
file1.close()
#plt.show()
file2 = open('./res/map_data','a')
for location in locations:
    file2.write(location)
file2.close()


