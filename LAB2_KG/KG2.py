

import numpy as np
from PIL import Image, ImageOps

img_mat = np.zeros((2000, 2000), dtype=np.uint8)
z_buffer = np.full((2000,2000), np.inf)

def normal(x0, y0, z0, x1, y1, z1, x2, y2, z2): #Функция для вычисления нормали
    A = np.array([x1 - x2, y1 - y2, z1 - z2])
    B = np.array([x1 - x0, y1 - y0, z1 - z0])
    N = np.cross(A, B)
    return N / np.linalg.norm(N)


def barycentric_coords(x, y, x0, y0, x1, y1, x2, y2): #Функция для вычисления барицентрических координат
    denom = (x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2)


    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / denom
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / denom
    lambda2 = 1.0 - lambda0 - lambda1

    return lambda0, lambda1, lambda2

def draw_triangle(image, z_buffer, x0, y0, x1, y1, x2, y2, z0, z1, z2, color):  #Функция отрисовки треугольника
    height, width = image.shape

    xmin = max(0, int(min(x0, x1, x2)))
    xmax = min(width - 1, int(max(x0, x1, x2)))
    ymin = max(0, int(min(y0, y1, y2)))
    ymax = min(height - 1, int(max(y0, y1, y2)))

    if ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2)==0): return
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            l0, l1, l2 = barycentric_coords(x, y, x0, y0, x1, y1, x2, y2)
            if l0 >= 0 and l1 >= 0 and l2 >= 0:
                z = l0*z0 + l1*z1 + l2*z2
                if z<z_buffer[y,x]:
                    image[y, x] = color
                    z_buffer[y,x]=z



file = open('model_1.obj')
v = []
f = []
for str in file:
    splitted_str = str.split()
    if splitted_str[0] == 'v':
        v.append([float(splitted_str[1]), float(splitted_str[2]), float(splitted_str[3])])
    if splitted_str[0] == 'f':
        f.append([int(splitted_str[1].split('/')[0]), int(splitted_str[2].split('/')[0]), int(splitted_str[3].split('/')[0])])
color = np.random.choice(range(256))
light_dir = np.array([0, 0, 1])
for poly in f:
    v0 = v[poly[0] - 1]
    v1 = v[poly[1] - 1]
    v2 = v[poly[2] - 1]

    norm = normal(*v0, *v1, *v2)
    cos_t = np.dot(norm, light_dir)
    if cos_t < 0:                                       #Необходимое условие
        color = int(-255 * cos_t)
        color = np.clip(color, 0, 255)
        x0 = int(v0[0] * 10000 + 1000)
        y0 = int(v0[1] * 10000 + 1000)
        x1 = int(v1[0] * 10000 + 1000)
        y1 = int(v1[1] * 10000 + 1000)
        x2 = int(v2[0] * 10000 + 1000)
        y2 = int(v2[1] * 10000 + 1000)

        draw_triangle(img_mat, z_buffer, x0, y0, x1, y1, x2, y2, v0[2], v1[2], v2[2], color)



img_mat = Image.fromarray(img_mat, mode='L')
img_mat = ImageOps.flip(img_mat)
img_mat.save('img10.png')
