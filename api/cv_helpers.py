import copy
import itertools
import cv2
import json
import cv2
import time
import math
import numpy as np
from scipy import linalg

from RemoteCams import RemoteCams



# ----------------------------------------------DELETE-------------------------------------------------------------
distances = [ [65, 125, 150], 
              [130, 130, 260], 
              [100, 170, 280], 
              [200, 200, 200] ]

camera_poses = [{'R': np.array([[1., 0., 0.],
       [0., 1., 0.],
       [0., 0., 1.]]), 't': np.array([0., 0., 0.], dtype=float)}, {'R': np.array([[ 0.10266333, -0.5527108 ,  0.8270254 ],
       [ 0.47355936,  0.75831084,  0.44800246],
       [-0.87475812,  0.34565219,  0.33959209]]), 't': np.array([-1510.50267095, -1009.31665088,  1949.12206991])}, {'R': np.array([[-0.36526976, -0.54019337,  0.75813529],
       [ 0.62064545,  0.46567194,  0.63083189],
       [-0.69381354,  0.70095703,  0.16517268]]), 't': np.array([-2173.77075459, -1110.43637481,  2219.0067509 ])}]

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
    DeprecationWarning("Deprecated function! Use find_dot() instead.")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Use minMaxLoc to find the brightest point in the grayscale image
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

        # Draw a circle around the brightest point
    cv2.circle(image, maxLoc, 10, (0, 0, 255), 2)

    # Print the coordinates of the brightest point
    # print("Coordinates of the brightest point:", maxLoc)

    return maxLoc

def find_dot(img):
    # img = cv.GaussianBlur(img,(5,5),0)
    grey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    grey = cv2.threshold(grey, 200, 255, cv2.THRESH_BINARY)[1]
    contours,_ = cv2.findContours(grey, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.drawContours(img, contours, -1, (0,255,0), 1)

    image_points = []
    for contour in contours:
        moments = cv2.moments(contour)
        if moments["m00"] != 0:
            center_x = int(moments["m10"] / moments["m00"])
            center_y = int(moments["m01"] / moments["m00"])
            cv2.putText(img, f'({center_x}, {center_y})', (center_x,center_y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (100,255,100), 1)
            cv2.circle(img, (center_x,center_y), 1, (100,255,100), -1)
            image_points.append([center_x, center_y])

    if len(image_points) == 0:
        image_points = [[None, None]]

    return image_points

def load_camera_parameters(camname:str, prepath:str=""):
    '''Include trailing / in the `prepath` variable'''
    with open(f'{prepath}calibration_data/{camname}.json') as f:
        data = json.load(f)
    return np.array(data["mtx"]), np.array(data["dist"])



def find_point_correspondance_and_object_points(image_points, frames, c1_mtx):
    for image_points_i in image_points:
        try:
            image_points_i.remove([None, None])
        except:
            pass
    # print(image_points)
    # [object_points, possible image_point groups, image_point from camera]
    correspondances = [[[i]] for i in image_points[0]]

    Ps = [] # projection matricies
    for i, camera_pose in enumerate(camera_poses):
        RT = np.c_[camera_pose["R"], camera_pose["t"]]
        P = c1_mtx @ RT
        Ps.append(P)

    root_image_points = [{"camera": 0, "point": point} for point in image_points[0]]
    # print(root_image_points)
    
    for i in range(1, len(camera_poses)):
        
        epipolar_lines = []
        for root_image_point in root_image_points:
            # print(root_image_point)
            F = cv2.sfm.fundamentalFromProjections(Ps[root_image_point["camera"]], Ps[i])
            line = cv2.computeCorrespondEpilines(np.array([root_image_point["point"]], dtype=np.float32), 1, F)
            epipolar_lines.append(line[0,0].tolist())
            frames[i] = drawlines(frames[i], line[0])
            # print(num)
            # num+=1
        not_closest_match_image_points = np.array(image_points[i])
        points = np.array(image_points[i])

        for j, [a, b, c] in enumerate(epipolar_lines):
            distances_to_line = np.array([])
            if len(points) != 0:
                distances_to_line = np.abs(a*points[:,0] + b*points[:,1] + c) / np.sqrt(a**2 + b**2)

            possible_matches = points[distances_to_line < 5].copy()

            distances_to_line = distances_to_line[distances_to_line < 5]
            possible_matches_sorter = distances_to_line.argsort()
            possible_matches = possible_matches[possible_matches_sorter]
    
            if len(possible_matches) == 0:
                for possible_group in correspondances[j]:
                    possible_group.append([None, None])
            else:
                not_closest_match_image_points = [row for row in not_closest_match_image_points.tolist() if row != possible_matches.tolist()[0]]
                not_closest_match_image_points = np.array(not_closest_match_image_points)

                new_correspondances_j = []
                for possible_match in possible_matches:
                    temp = copy.deepcopy(correspondances[j])
                    for possible_group in temp:
                        possible_group.append(possible_match.tolist())
                    new_correspondances_j += temp
                correspondances[j] = new_correspondances_j

        for not_closest_match_image_point in not_closest_match_image_points:
            root_image_points.append({"camera": i, "point": not_closest_match_image_point})
            temp = [[[None, None]] * i]
            temp[0].append(not_closest_match_image_point.tolist())
            correspondances.append(temp)

    object_points = []
    errors = []
    
    for image_points in correspondances:
        object_points_i = triangulate_points(image_points, camera_poses, c1_mtx)

        if np.all(object_points_i == None):
            continue

        errors_i = calculate_reprojection_errors(image_points, object_points_i, camera_poses, c1_mtx)

        object_points.append(object_points_i[np.argmin(errors_i)])
        errors.append(np.min(errors_i))

    return  np.array(errors), np.array(object_points)

def distance_matrix(object_points: list[list[int]]) -> dict:
    dist_n = dict()
    for items in object_points:
        for i in range(len(object_points)):
            
            d = round(math.sqrt((items[0] - object_points[i][0])**2+(items[1] - object_points[i][1])**2+(items[2] - object_points[i][2])**2),4)
            try:
                dist_n[i].append(d)
            except:
                dist_n[i] = [d]
        
    return dist_n

def create_objects(results,object_points,errors):
    objects = []
    for i in results:
       for j in results[i]:
        #    print(j)
           pos = [(object_points[j[0]][0]+object_points[j[1]][0]+object_points[j[2]][0])/3,(object_points[j[0]][1]+object_points[j[1]][1]+object_points[j[2]][1])/3,(object_points[j[0]][2]+object_points[j[1]][2]+object_points[j[2]][2])/3]
           
           heading = np.pi
           
           error = np.mean([errors[j[0]], errors[j[1]], errors[j[2]]])
           
           objects.append({
               "pos": np.array(pos),
               "heading": heading,
               "error" : error,
               "droneIndex": i 
           }) 
    return objects

def possible_pairs(object_points,dist_n: dict) -> tuple[dict, dict]:
            new_dist_dict_x = dict()
            new_dist_dict_y = dict()

            distances_x = [i[0] for i in distances]
            distances_y = [i[1] for i in distances]
            distances_z = [i[2] for i in distances]
            for key,values in dist_n.items():
                new_dist_dict_x[key] = dict() 
                new_dist_dict_y[key] = dict() 
                for i in range(len(values)):
                    for j in range(len(distances_x)):
                        if abs(distances_x[j] - values[i]) < 35:
                          try:
                            new_dist_dict_x[key][j].append(i)
                          except KeyError:
                            new_dist_dict_x[key][j] = [i]
            
                    for k in range(len(distances_y)):
                        if abs(distances_y[k] - values[i]) < 35:
                          try:
                           new_dist_dict_y[key][k].append(i)
                          except KeyError:
                           new_dist_dict_y[key][k] = [i]
                result_x, result_y = new_dist_dict_x, new_dist_dict_y
            drone_indexes = dict()
            for (key1,value1), (key2,value2) in zip(new_dist_dict_x.items(), new_dist_dict_y.items()):
                for (keys1,data1), (keys2,data2) in zip(value1.items(), value2.items()):
                    if keys1 == keys2:
                        l = list(itertools.combinations(set(data1 + data2), 2))
                        for pairs in l:
                            x, y = pairs
                            dist_3 = round(math.sqrt((object_points[x][0] - object_points[y][0])**2+(object_points[x][1] - object_points[y][1])**2+(object_points[x][2] - object_points[y][2])**2),4)
                    
                            if abs(dist_3 - distances_z[keys1]) < 35:
                                try:
                                    drone_indexes[keys1].append([x,y,key1])
                                except:
                                    drone_indexes[keys1] = ([[x,y,key1]])
            return drone_indexes


       
def drawlines(img1,lines):
    r,c,_ = img1.shape
    for r in lines:
        color = tuple(np.random.randint(0,255,3).tolist())
        x0,y0 = map(int, [0, -r[2]/r[1] ])
        x1,y1 = map(int, [c, -(r[2]+r[0]*c)/r[1] ])
        img1 = cv2.line(img1, (x0,y0), (x1,y1), color,1)
    return img1

def calculate_reprojection_errors(image_points, object_points, camera_poses, c1_mtx):
    errors = np.array([])
    for image_points_i, object_point in zip(image_points, object_points):
        error = calculate_reprojection_error(image_points_i, object_point, camera_poses, c1_mtx)
        if error is None:
            continue
        errors = np.concatenate([errors, [error]])

    return errors


def calculate_reprojection_error(image_points, object_point, camera_poses, c1_mtx):

    image_points = np.array(image_points)
    none_indicies = np.where(np.all(image_points == None, axis=1))[0]
    image_points = np.delete(image_points, none_indicies, axis=0)
    camera_poses = np.delete(camera_poses, none_indicies, axis=0)

    if len(image_points) <= 1:
        return None
    
    image_points_t = image_points.transpose((0,1))

    errors = np.array([])
    for i, camera_pose in enumerate(camera_poses):
        if np.all(image_points[i] == None, axis=0):
            continue
        projected_img_points, _ = cv2.projectPoints(
            np.expand_dims(object_point, axis=0).astype(np.float32), 
            np.array(camera_pose["R"], dtype=np.float64), 
            np.array(camera_pose["t"], dtype=np.float64), 
            c1_mtx, 
            np.array([])
        )
        projected_img_point = projected_img_points[:,0,:][0]
        errors = np.concatenate([errors, (image_points_t[i]-projected_img_point).flatten() ** 2])
    
    return errors.mean()
