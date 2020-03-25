import argparse
import scipy.io as scio
import sys
import os
from PIL import Image
import numpy as np

dep_cx = 636.674
dep_fx = 602.621
dep_cy = 365.427
dep_fy = 602.526


k = np.array([[dep_fx, 0, dep_cx],
              [0, dep_fy, dep_cy],
              [0, 0, 1]])
k_inv = np.linalg.pinv(k)

scalingFactor = 18000.0


def generate_pointcloud(rgb_file, depth_file, ply_file, mat_file):
    """
    Generate a colored point cloud in PLY format from a color and a depth image.

    Input:
    rgb_file -- filename of color image
    depth_file -- filename of depth image
    ply_file -- filename of ply file

    """
    rgba = Image.open(rgb_file)
    rgb = Image.new("RGB", rgba.size, (255, 255, 255))
    rgb.paste(rgba, mask=rgba.split()[3])
    depth = Image.open(depth_file)

    position_map = np.zeros((3, rgb.size[1]*rgb.size[0]), dtype=float)

    if rgb.size != depth.size:
        raise Exception("Color and depth image do not have the same resolution.")
    if rgb.mode != "RGB":
        raise Exception("Color image is not in RGB format")
    if depth.mode != "I":
        raise Exception("Depth image is not in intensity format")

    points = []
    i = 0
    for v in range(rgb.size[1]):
        for u in range(rgb.size[0]):
            color = rgb.getpixel((u, v))

            Z = depth.getpixel((u, v)) / scalingFactor
            dep = Z

            if Z == 0 or Z >= 0.05: continue
            k = dep / (u * k_inv[2][0] + v * k_inv[2][1] + k_inv[2][2])

            X = (u * k_inv[0][0] + v * k_inv[0][1] + k_inv[0][2]) * k
            Y = (u * k_inv[1][0] + v * k_inv[1][1] + k_inv[1][2]) * k
            position_map[0][i] = X
            position_map[1][i] = Y
            position_map[2][i] = Z
            i += 1

            points.append("%f %f %f %d %d %d 0\n" % (X, Y, Z, color[0], color[1], color[2]))
    file = open(ply_file, "w")
    file.write('''ply
format ascii 1.0
element vertex %d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
property uchar alpha
end_header
%s
''' % (len(points), "".join(points)))
    file.close()
    scio.savemat(mat_file, {'data': position_map})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
    This script reads a registered pair of color and depth images and generates a colored 3D point cloud in the
    PLY format. 
    ''')
    parser.add_argument('rgb_file', help='input color image (format: png)')
    parser.add_argument('depth_file', help='input depth image (format: png)')
    parser.add_argument('ply_file', help='output PLY file (format: ply)')
    parser.add_argument('mat_file', help='output position map file (format: mat)')
    args = parser.parse_args()

    generate_pointcloud(args.rgb_file, args.depth_file, args.ply_file, args.mat_file)
