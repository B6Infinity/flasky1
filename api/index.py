from flask import Flask, url_for, jsonify
from flask_cors import CORS
from util_helpers import *
from cv_helpers import get_point, triangulate_points, load_camera_parameters, RemoteCams, time, cv2, math, np, camera_poses
from threading import Thread

# Custom Vars


CAMIP_1_SUFFIX = "253"
CAMIP_2_SUFFIX = "85"
CAMIP_3_SUFFIX = "41"

IP_PREFIX = "192.168.146."

CAMS = RemoteCams([IP_PREFIX+CAMIP_1_SUFFIX, IP_PREFIX+CAMIP_2_SUFFIX, IP_PREFIX+CAMIP_3_SUFFIX], 8005)
print("Waiting for cams to get hot...")
time.sleep(4)



class MasterApp():

    def __init__(self) -> None:
        # FLAGS
        self.IS_TRIANGULATING_POINTS = False
            
        # WebServer
        self.app = Flask(__name__, static_folder="../static")
        CORS(self.app) # Enable CORS for all routes

        # CV stuff
        self.c1_mtx, self.c1_dist = load_camera_parameters("IPCAM2", "data/")
        self.c2_mtx, self.c2_dist = load_camera_parameters("IPCAM2", "data/")

        self.cams = CAMS
        self.camera_poses = camera_poses
        self.point_coord = [0,0,0]

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

        @self.app.route('/get_point_location')
        def get_point_coords():
            return jsonify({"x": self.point_coord[0], "y": self.point_coord[1], "z": self.point_coord[2]})


        # Sequence initiators ---

        @self.app.route('/start_triangulation')
        def handle_start_triangulation():
            print("Starting triangulation")
            self.IS_TRIANGULATING_POINTS = True
            return jsonify({"status": "success"})

        @self.app.route('/stop_triangulation')
        def handle_stop_triangulation():
            print("Starting triangulation")
            self.IS_TRIANGULATING_POINTS = True
            return jsonify({"status": "success"})


    # LOOP(s) --------------------------------------------

    def start_triangulation(self):
        print("Starting triangulation thread...")
        while True:
            if not self.IS_TRIANGULATING_POINTS:
                continue

            imagePoints=list()
            img = self.cams.get_frames()
            for i in range(3):
                imagePoints.append(get_point(img[i]))
            
            # EDOT
            object_point = triangulate_points([imagePoints],camera_poses=camera_poses, c1_mtx=self.c1_mtx)
            x,y,z = object_point[0]
            self.point_coord = [x,y,z]

            # print(f"\r{x},{y},{z}",end= " ")
            
            # distance = math.sqrt(abs(object_point[0][0])**2+abs(object_point[0][1])**2+abs(object_point[0][2])**2)
            # print(f"\r{round(distance/10)}",end= " ")

            
            cv2.imshow("trigulation",np.hstack((img[0],img[1],img[2])))
            k = cv2.waitKey(5)
            if k==ord('q'):
                break


# Flask app --------------------------------------------





if __name__ == '__main__':

    master_app = MasterApp()

    # Fire up server
    master_app.app.run(debug=False)

    # master_app.cam.kill_all()


# Go Live

# run the index.py file

# http://127.0.0.1:5000/start_triangulation


