import numpy as np
from PIL import Image, ImageOps

def render_model(obj_path, texture_path, img_mat, z_buffer, shift, angles=(0,0,0), quaternion=None, scale=1.0):
    height, width, _ = img_mat.shape



    texture = Image.open(texture_path).convert("RGB")
    texture_array = np.array(texture)
    W_T, H_T = texture.size

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

    def draw_triangle(image, z_buffer, x0, y0, x1, y1, x2, y2, z0, z1, z2, a, v,
                      uvs, texture_array, W_T, H_T):
        xx0 = a * x0 / z0 + v / 2
        yy0 = a * y0 / z0 + v / 2
        xx1 = a * x1 / z1 + v / 2
        yy1 = a * y1 / z1 + v / 2
        xx2 = a * x2 / z2 + v / 2
        yy2 = a * y2 / z2 + v / 2

        xmin = max(0, int(min(xx0, xx1, xx2)))
        xmax = min(width - 1, int(max(xx0, xx1, xx2)))
        ymin = max(0, int(min(yy0, yy1, yy2)))
        ymax = min(height - 1, int(max(yy0, yy1, yy2)))

        if ((xx0 - xx2) * (yy1 - yy2) - (xx1 - xx2) * (yy0 - yy2)) == 0:
            return

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                l0, l1, l2 = barycentric_coords(x, y, xx0, yy0, xx1, yy1, xx2, yy2)
                if l0 >= 0 and l1 >= 0 and l2 >= 0:
                    z = l0 * z0 + l1 * z1 + l2 * z2
                    if z < z_buffer[y, x]:
                        ut = l0 * uvs[0][0] + l1 * uvs[1][0] + l2 * uvs[2][0]
                        vt = l0 * uvs[0][1] + l1 * uvs[1][1] + l2 * uvs[2][1]
                        tx = int(round(ut * (W_T - 1)))
                        ty = int(round((1 - vt) * (H_T - 1)))

                        r, g, b = texture_array[ty, tx]
                        image[y, x] = [r, g, b]
                        z_buffer[y, x] = z

    def quaternionx(q):
        w, x, y, z = q
        return np.array([
            [1 - 2 * (y**2 + z**2), 2 * (x*y - w*z), 2 * (x*z + w*y)],
            [2 * (x*y + w*z), 1 - 2 * (x**2 + z**2), 2 * (y*z - w*x)],
            [2 * (x*z - w*y), 2 * (y*z + w*x), 1 - 2 * (x**2 + y**2)]
        ])


    def rotation_and_shift(vert, angx=0, angy=0, angz=0, shift=(0, 0, 0), quaternion=None):
        vert = np.array(vert)*scale
        if quaternion is not None:
            R = quaternionx(quaternion)
        else:
            angx, angy, angz = map(np.radians, (angx, angy, angz))
            RX = np.array([[1,0,0],[0,np.cos(angx),np.sin(angx)],[0,-np.sin(angx),np.cos(angx)]])
            RY = np.array([[np.cos(angy),0,np.sin(angy)],[0,1,0],[-np.sin(angy),0,np.cos(angy)]])
            RZ = np.array([[np.cos(angz),np.sin(angz),0],[-np.sin(angz),np.cos(angz),0],[0,0,1]])
            R = RX @ RY @ RZ
        return R @ vert + np.array(shift)

    def quat_mult(q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return (
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        )

    def create_quaternion(angle_deg, axis):
        angle_rad = np.radians(angle_deg)
        sin_half = np.sin(angle_rad / 2)
        cos_half = np.cos(angle_rad / 2)
        return (
            cos_half,
            axis[0] * sin_half,
            axis[1] * sin_half,
            axis[2] * sin_half
        )

    v, vt, f, f1 = [], [], [], []
    with open(obj_path) as file:
        for line in file:
            parts = line.split()
            if not parts or parts[0].startswith('#'): continue
            if parts[0] == 'v':
                v.append([float(i) for i in parts[1:4]])
            elif parts[0] == 'vt':
                vt.append([float(i) for i in parts[1:3]])
            elif parts[0] == 'f':
                for i in range(2, len(parts)-1):
                    f.append([int(parts[1].split('/')[0])-1, int(parts[i].split('/')[0])-1, int(parts[i+1].split('/')[0])-1])
                    f1.append([int(parts[1].split('/')[1])-1, int(parts[i].split('/')[1])-1, int(parts[i+1].split('/')[1])-1])

    angle_deg_x = 180
    angle_deg_y = 360
    angle_deg_z = 180

    use_quaternion = True
    if use_quaternion:
        qx = create_quaternion(angle_deg_x, [1, 0, 0])
        qy = create_quaternion(angle_deg_y, [0, 1, 0])
        qz = create_quaternion(angle_deg_z, [0, 0, 1])

        q_combined = quat_mult(qz, quat_mult(qy, qx))
        quaternion = q_combined

        for i in range(len(v)):
            v[i] = rotation_and_shift(v[i], shift=shift, quaternion=quaternion)

    else:
        angx = 0
        angy = 225
        angz = 0

        for i in range(len(v)):
            v[i] = rotation_and_shift(v[i], angx, angy, angz, shift=shift)

    v_calc = np.zeros((len(v), 3))
    light_dir = np.array([0,0,1])

    for poly in f:
        n = normal(*v[poly[0]], *v[poly[1]], *v[poly[2]])
        for idx in poly:
            v_calc[idx] += n

    for i in range(len(v_calc)):
        norm = np.linalg.norm(v_calc[i])
        v_calc[i] = v_calc[i] / norm if norm > 1e-8 else np.array([0,0,1])

    for poly, tex in zip(f, f1):
        p0, p1, p2 = v[poly[0]], v[poly[1]], v[poly[2]]
        uv0, uv1, uv2 = vt[tex[0]], vt[tex[1]], vt[tex[2]]
        draw_triangle(img_mat, z_buffer,
                      p0[0], p0[1], p1[0], p1[1], p2[0], p2[1],
                      p0[2], p1[2], p2[2],
                      10000 * 0.2, width,
                      [uv0, uv1, uv2],
                      texture_array, W_T, H_T)


height, width = 2000, 2000
img_mat = np.zeros((height, width, 3), dtype=np.uint8)
z_buffer = np.full((height, width), np.inf)

render_model('model_1.obj', 'bunny-atlas.jpg', img_mat, z_buffer, shift=(1, -0.05, 7), scale =  10)
render_model('model.obj', 'model.jpg', img_mat, z_buffer, shift=(-2, -0.05, 7),scale =  1)

result_img = Image.fromarray(img_mat, mode='RGB')
result_img = ImageOps.flip(result_img)
result_img.save('final_scene.png')
