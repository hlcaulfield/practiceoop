import numpy as np
from PIL import Image, ImageOps

img_mat = np.zeros((2000, 2000), dtype=np.uint8)
z_buffer = np.full((2000,2000), np.inf)


def normal(x0, y0, z0, x1, y1, z1, x2, y2, z2):
    A = np.array([x1 - x2, y1 - y2, z1 - z2])
    B = np.array([x1 - x0, y1 - y0, z1 - z0])
    N = np.cross(A, B)
    return N / np.linalg.norm(N)

def barycentric_coords(x, y, x0, y0, x1, y1, x2, y2):
    denom = (x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2)
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / denom
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / denom
    lambda2 = 1.0 - lambda0 - lambda1
    return lambda0, lambda1, lambda2

def draw_triangle(image, z_buffer, x0, y0, x1, y1, x2, y2, z0, z1, z2, a, v, color):
    xx0=a*x0/z0 + v/2
    yy0=a*y0/z0 + v/2
    xx1=a*x1/z1 + v/2
    yy1=a*y1/z1 + v/2
    xx2=a*x2/z2 + v/2
    yy2=a*y2/z2 + v/2
    height, width = image.shape
    xmin = max(0, int(min(xx0, xx1, xx2)))
    xmax = min(width - 1, int(max(xx0, xx1, xx2)))
    ymin = max(0, int(min(yy0, yy1, yy2)))
    ymax = min(height - 1, int(max(yy0, yy1, yy2)))

    if ((xx0 - xx2) * (yy1 - yy2) - (xx1 - xx2) * (yy0 - yy2)==0): return
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            l0, l1, l2 = barycentric_coords(x, y, xx0, yy0, xx1, yy1, xx2, yy2)
            if l0 >= 0 and l1 >= 0 and l2 >= 0:
                z = l0*z0 + l1*z1 + l2*z2
                if z<z_buffer[y,x]:
                    image[y, x] = color
                    z_buffer[y,x]=z

def rotation_and_shift(vert, angx=0,angy=0,angz=0, shift = (0,0,0)):
    x,y,z = vert
    x1,y1,z1 = shift
    angx=np.radians(angx)
    angy=np.radians(angy)
    angz=np.radians(angz)

    RX = np.array([
        [1,0,0],
        [0, np.cos(angx),np.sin(angx)],
        [0, -np.sin(angx), np.cos(angx)]

    ])
    RY= np.array([
        [np.cos(angy), 0, np.sin(angy)],
        [0,1,0],
        [-np.sin(angy),0,np.cos(angy)]

    ])
    RZ = np.array([
        [np.cos(angz),np.sin(angz),0],
        [-np.sin(angz),np.cos(angz),0],
        [0,0,1]
    ])
    R=RX @ RY @ RZ

    rt_vert = R @ np.array([x,y,z]) + np.array([x1,y1,z1])

    return rt_vert







file = open('model_1.obj')
v = []
f = []



for str in file:
    splitted_str = str.split()
    if splitted_str[0] == 'v':
        v.append([float(splitted_str[1]), float(splitted_str[2]), float(splitted_str[3])])
    if splitted_str[0] == 'f':
        f.append([int(splitted_str[1].split('/')[0]), int(splitted_str[2].split('/')[0]), int(splitted_str[3].split('/')[0])])
angx = 0
angy =225
angz = 0

shift = (0,-0.04,0.2)

for i in range(len(v)):
    v[i]= rotation_and_shift(v[i],angx,angy,angz,shift)


color = np.random.choice(range(256))
light_dir = np.array([0, 0, 1])

for poly in f:
    v0 = v[poly[0] - 1]
    v1 = v[poly[1] - 1]
    v2 = v[poly[2] - 1]

    norm = normal(*v0, *v1, *v2)
    cos_t = np.dot(norm, light_dir)
    if cos_t < 0:
        color = int(-255 * cos_t)
        color = np.clip(color, 0, 255)
        x0 = v0[0]
        y0 = v0[1]
        x1 = v1[0]
        y1 = v1[1]
        x2 = v2[0]
        y2 = v2[1]






        draw_triangle(img_mat, z_buffer, x0, y0, x1, y1, x2, y2, v0[2], v1[2], v2[2], 10000*0.2, 2000, color)




img_mat = Image.fromarray(img_mat, mode='L')
img_mat = ImageOps.flip(img_mat)
img_mat.save('img15.png')
