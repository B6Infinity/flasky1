import cv2
import json
import cv2
import time
import math
import numpy as np
from scipy import linalg

from RemoteCams import RemoteCams



# ----------------------------------------------DELETE-------------------------------------------------------------
camera_poses = [{'R': np.array([[1., 0., 0.],
       [0., 1., 0.],
       [0., 0., 1.]]), 't': np.array([0., 0., 0.], dtype=float)}, {'R': np.array([[ 0.39423839, -0.17425675,  0.90233623],
       [ 0.16256264,  0.97959859,  0.11815244],
       [-0.90451616,  0.10010594,  0.41452301]]), 't': np.array([[-1718.94189507],
       [ -215.14729273],
       [ 1244.22151395]])}, {'R': np.array([[-0.62194453, -0.10753441,  0.77564254],
       [ 0.16243507,  0.95126374,  0.26213001],
       [-0.76602862,  0.28902188, -0.57416592]]), 't': np.array([[-1663.26348112],
       [ -464.87276861],
       [ 2885.91189765]])}]
# -----------------------------------------------------------------------------------------------------------

# MATHY STUFF


def triangulate_point(image_points, camera_poses, c1_mtx):
    image_points = np.array(image_points)
    # print(image_points)
    none_indicies = np.where(np.all(image_points == None, axis=1))[0]
    image_points = np.delete(image_points, none_indicies, axis=0)
    camera_poses = np.delete(camera_poses, none_indicies, axis=0)

    if len(image_points) <= 1:
        return [None, None, None]

    Ps = [] # projection matricies

    for i, camera_pose in enumerate(camera_poses):
        RT = np.c_[camera_pose["R"], camera_pose["t"]]
        P = c1_mtx @ RT
        Ps.append(P)

    # https://temugeb.github.io/computer_vision/2021/02/06/direct-linear-transorms.html
    def DLT(Ps, image_points):
        A = []

        for P, image_point in zip(Ps, image_points):
            A.append(image_point[1]*P[2,:] - P[1,:])
            A.append(P[0,:] - image_point[0]*P[2,:])
            
        A = np.array(A).reshape((len(Ps)*2,4))
        B = A.transpose() @ A
        U, s, Vh = linalg.svd(B, full_matrices = False)
        object_point = Vh[3,0:3]/Vh[3,3]

        return object_point

    object_point = DLT(Ps, image_points)

    return object_point


# SIMPLE STUFF


def triangulate_points(image_points, camera_poses, c1_mtx):
    object_points = []
    for image_points_i in image_points:
        object_point = triangulate_point(image_points_i, camera_poses, c1_mtx)
        object_points.append(object_point)
    
    return np.array(object_points)

def get_point(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Use minMaxLoc to find the brightest point in the grayscale image
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

        # Draw a circle around the brightest point
    cv2.circle(image, maxLoc, 10, (0, 0, 255), 2)

    # Print the coordinates of the brightest point
    # print("Coordinates of the brightest point:", maxLoc)

    return maxLoc

def load_camera_parameters(camname:str, prepath:str=""):
    '''Include trailing / in the `prepath` variable'''
    with open(f'{prepath}calibration_data/{camname}.json') as f:
        data = json.load(f)
    return np.array(data["mtx"]), np.array(data["dist"])


