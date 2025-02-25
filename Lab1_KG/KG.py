import math

import numpy as np
from PIL import Image, ImageOps

img_mat = np.zeros((2000, 2000), dtype=np.uint8)


def x_loop_line( image, x0, y0, x1, y1, color):
    xchange = False
    if (abs(x0 - x1) < abs(y0 - y1)):
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        xchange = True
    if (x0 > x1):
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    y = y0
    dy =2 * abs(y1 - y0)
    derror = 0.0
    y_update = 1 if y1 > y0 else -1

    for x in range (x0, x1):
        t = (x-x0)/(x1 -x0)
        y = round ((1.0-t)*y0 + t*y1)
        if (xchange):
            image[x, y] = color
        else:
            image[y, x] = color
        derror+= dy
        if (derror >2*(x1-x0)*0.5):
            derror-= 2 * (x1-x0)*1
            y += y_update


file = open('model_1.obj')
v=[]
f=[]
for str in file:
    splitted_str=str.split()
    if (splitted_str[0]=='v'):
        v.append([float(splitted_str[1]),float(splitted_str[2]),float(splitted_str[3])])
    if (splitted_str[0]=='f'):
        f.append([int(splitted_str[1].split('/')[0]),\
                  int(splitted_str[2].split('/')[0]),\
                  int(splitted_str[3].split('/')[0])])




print(f)
color=255
for poly in f:

    v0=v[poly[0]-1]
    v1=v[poly[1]-1]
    v2=v[poly[2]-1]
    x0=int(v0[0]*10000+1000)
    y0=int(v0[1]*10000+1000)
    x1=int(v1[0]*10000+1000)
    y1=int(v1[1]*10000+1000)
    x2=int(v2[0]*10000+1000)
    y2=int(v2[1]*10000+1000)
    x_loop_line(img_mat, x0, y0, x1, y1, color)
    x_loop_line(img_mat, x1, y1, x2, y2, color)
    x_loop_line(img_mat, x2, y2, x0, y0, color)






img = Image.fromarray(img_mat, mode='L')
img=ImageOps.flip(img)
img.save('img9.png')