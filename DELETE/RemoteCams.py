import cv2
from threading import Thread
import json
import numpy as np
from RemoteCam import RemoteCam

class RemoteCams:
    def __init__(self, ips : list, port : int=8005, names: list=None):
        self.cams : list[RemoteCam] = []
        for i, ip in enumerate(ips):
            name = names[i] if names else f"IPCAM{i}"
            self.cams.append(RemoteCam(ip, port, name))
            self.cams[i].cap_thread.start()

        print("All cams started")

    def get_frames(self):
        frames = []
        for cam in self.cams:
            frames.append(cam.last_frame)
        return frames

    def kill_all(self):
        self.kill_all = True
        for cam in self.cams:
            cam.kill_cam()