import cv2
from threading import Thread
import json
import numpy as np
from RemoteCam import RemoteCam

class RemoteCams:
    def __init__(self, ips : list, port : int=8005, names: list=None):
        self.cams : list[RemoteCam] = []
        self.connection_threads : list[Thread] = []

        for i, ip in enumerate(ips):
            name = names[i] if names else f"IPCAM{i}"
            
            cthread = Thread(target=self.initiate_connection, args=(ip, port, name, i))
            self.connection_threads.append(cthread)
            print("Appened thread", i)

            # rc = RemoteCam(ip, port, name)
            # self.cams.append(rc)
            # self.cams[i].cap_thread.start()

        for t in self.connection_threads:
            t.start()

        print("All cams started")

    def initiate_connection(self, ip, port, name, index ):
        '''Blocks action till connection is established'''
        rc = RemoteCam(ip, port, name)
        self.cams.append(rc)
        self.cams[index].cap_thread.start()


    def get_frames(self):
        frames = []
        for cam in self.cams:
            frames.append(cam.last_frame)
        return frames

    def kill_all(self):
        self.kill_all = True
        for cam in self.cams:
            cam.kill_cam()