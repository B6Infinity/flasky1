from threading import Thread
from flask import Flask, url_for, jsonify
from flask_cors import CORS

from util_helpers import *
from cv_helpers import create_objects, distance_matrix, find_dot, find_point_correspondance_and_object_points, possible_pairs, triangulate_points, load_camera_parameters, RemoteCams, time, cv2, math, np, camera_poses
from KalmanFilter import KalmanFilter

# Custom Vars


CAMIP_2_SUFFIX = "253"
CAMIP_3_SUFFIX = "85"
CAMIP_1_SUFFIX = "41"

_IP_PREFIX = "192.168.107."
CAM_IPS : list = [_IP_PREFIX+CAMIP_1_SUFFIX, _IP_PREFIX+CAMIP_2_SUFFIX, _IP_PREFIX+CAMIP_3_SUFFIX]

CAMS = RemoteCams(CAM_IPS, 8005)
print("Waiting for cams to get hot...")
time.sleep(4)



class MasterApp():

    def __init__(self) -> None:
        # FLAGS
        self.IS_TRIANGULATING_POINTS = False

        # WebServer
        self.app = Flask(__name__, static_folder="../static")
        CORS(self.app) # Enable CORS for all routes

        self.kalman_filter = KalmanFilter(1)

        # CV stuff
        self.c1_mtx, self.c1_dist = load_camera_parameters("IPCAM2", "data/")
        self.c2_mtx, self.c2_dist = load_camera_parameters("IPCAM2", "data/")

        # self.cams : RemoteCams = None
        self.cams : RemoteCams = CAMS
        self.camera_poses = camera_poses
        
        self.point_coord = [0,0,0]
        self.ang_x = 0

        self.drones = [] # [{"pos": [0,0,0], "heading": 3.14}, {"pos": []...}, ...]


        # Managing Threads
        triangulation_thread = Thread(target=self.start_triangulation)
        triangulation_thread.start()


        @self.app.route('/')
        def home():
            print("Homin")
            return jsonify({"boltahaiki":"real id se aao"})
            # return f"Serving static file from {url_for('static', filename='index.html')}"


        # Value getters ---

        @self.app.route('/camera_poses')
        def get_camera_poses():
            cam_poses = []

            # Read camera poses from JSON file
            JD = read_json_data("data/STATE.json")



            for camera in JD["cameras"]:
                cam_poses.append(
                    JD["cameras"][camera]["pose"]
                )


            return jsonify({"camera_poses": cam_poses})

        @self.app.route('/get_point_location') # DEPRECATED
        def get_point_coords():
            return jsonify({"x": self.point_coord[0], "y": self.point_coord[1], "z": self.point_coord[2]})
        @self.app.route('/get_drone_location') # DEPRECATED
        def get_drone_coords():
            # print(self.point_coord)
            return jsonify({
                "pos":{
                    "x": float(self.point_coord[0]),
                    "y": float(self.point_coord[1]),
                    "z": float(self.point_coord[2])
                },"heading": self.ang_x
            })
        
        @self.app.route('/get_drones')
        def get_drones():
            
            print(self.drones)
            return jsonify({
                "drones": self.drones + [{"pos": [20, 27, 30], "heading":1.48}] # Fake Data
            })


        # Sequence initiators ---

        @self.app.route('/start_triangulation')
        def handle_start_triangulation():
            print("Starting triangulation")
            self.IS_TRIANGULATING_POINTS = True
            return jsonify({"status": "success"})

        @self.app.route('/stop_triangulation')
        def handle_stop_triangulation():
            print("Stopping triangulation")
            self.IS_TRIANGULATING_POINTS = True
            return jsonify({"status": "success"})

        # @self.app.route('/fire_up_cameras')
        # def handle_fire_up_cameras():
        #     print("Connecting to cameras...")
        #     self.cams = RemoteCams(CAM_IPS, 8005)
        #     print("Waiting for cams to get hot...")
        #     time.sleep(4)

        #     return jsonify({"status": "success"})


    # LOOP(s) --------------------------------------------
    
    '''
    # def start_triangulation(self):
    #     print("Starting triangulation thread...")
    #     while True:
    #         if self.cams == None:
    #             print("Fire up cams first!") ; time.sleep(2)
    #         if not self.IS_TRIANGULATING_POINTS:
    #             continue
            
    #         imagePoints=list()
    #         img = self.cams.get_frames()
    #         for i in range(3):
    #             imagePoints.append(find_dot(img[i]))
            
    #         object_point = triangulate_points([imagePoints],camera_poses=camera_poses, c1_mtx=self.c1_mtx)
    #         x,y,z = object_point[0]
    #         self.point_coord = [x,y,z]

            
    #         cv2.imshow("trigulation",np.hstack((img[0],img[1],img[2])))
    #         k = cv2.waitKey(5)
    #         if k==ord('q'):
    #             break
    '''
            
    def start_triangulation(self):
        print("Starting triangulation thread...")
        
        
        while True:
            if self.cams == None:
                print("Fire up cams first!") ; time.sleep(2)
            if not self.IS_TRIANGULATING_POINTS:
                continue
            
            
            try:
            
                imagePoints=list()
                img = self.cams.get_frames()
                for i in range(3):
                    imagePoints.append(find_dot(img[i]))
                
                
                errors, object_points = find_point_correspondance_and_object_points(image_points=imagePoints,frames=img, c1_mtx=self.c1_mtx)
                dist_n = distance_matrix(object_points)
                
                print("IN ∆ LOOP!", len(object_points))
                if len(object_points)>2:
                    # print("Im inside")
                    result = possible_pairs(object_points=object_points, dist_n = dist_n)
                    objects = create_objects(result,object_points=object_points,errors=errors)
                    # print(objects)
                    # print(" ")
                    filtered_objects = self.kalman_filter.predict_location(objects=objects)
                    print(filtered_objects)
                    # [{'pos': array([-245.89326,  409.1753 , 2020.0155 ], dtype=float32), 'vel': array([-302.70688 ,  136.49464 ,   91.674286], dtype=float32), 'heading': 3.141592653589793, 'droneIndex': 0}]
                    # print(" ")
                    # object_point = triangulate_points([imagePoints],camera_poses=camera_poses, c1_mtx=self.c1_mtx)

                    # x,y,z = filtered_objects[0]["pos"]
                    # ang_x = filtered_objects[0]["heading"]
                    # self.point_coord = [x,y,z]
                    # self.ang_x = ang_x
                    # print(self.point_coord)
                    self.drones = []
                    for obj in filtered_objects:
                        x,y,z = obj["pos"]
                        ang_x = obj["heading"]
                        # 
                        self.drones.append({
                            # "pos":{
                            #     "x": float(x),
                            #     "y": float(y),
                            #     "z": float(z)
                            # },
                            "pos": [float(x), float(y), float(z)],
                            "heading": ang_x
                        })


                
                cv2.imshow("trigulation",np.hstack((img[0],img[1],img[2])))
                k = cv2.waitKey(5)
                if k==ord('q'):
                    break
            
            except IndexError:
                pass
            except Exception as e:
                print(e.with_traceback())
                quit()

# Flask app --------------------------------------------





if __name__ == '__main__':

    master_app = MasterApp()

    # Fire up server
    master_app.app.run(debug=False)

    # master_app.cam.kill_all()


# Go Live

# run the index.py file

# http://127.0.0.1:5000/start_triangulation


