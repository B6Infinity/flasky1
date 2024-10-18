from RemoteCamsTH import RemoteCams
import time
import cv2
import numpy as np


font = cv2.FONT_HERSHEY_SIMPLEX

prev_frame_time = 0
# used to record the time at which we processed current frame
new_frame_time = 0

IPS = ["192.168.232.253","192.168.232.85","192.168.232.41"]

cam = RemoteCams(IPS, 8005)

time.sleep(5)

while True:
    imgs = cam.get_frames()
    
    if len(imgs) != len(IPS):
        continue


    for i in imgs:
        if i == None:
            continue
        '''Traceback (most recent call last):
        File "/home/bravo6/Desktop/active_projects/Swarm/flasky1/scripts/test2.py", line 27, in <module>
            if i == None:
        ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()'''
        print(i.shape)

    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time) 
    prev_frame_time = new_frame_time 
  
    fps = str(int(fps))

    cv2.putText(imgs[0], fps, (7, 70), font , 3, (100, 255, 0), 3, cv2.LINE_AA)
    
    cv2.imshow("test",np.hstack(((imgs[0],imgs[1],imgs[2]))))
    
    k = cv2.waitKey(5)
    if k ==ord('q'):
        break
    
cam.kill_all()


[{'R': array([[1., 0., 0.],
       [0., 1., 0.],
       [0., 0., 1.]]), 't': array([0., 0., 0.], dtype=float32)}, {'R': array([[ 0.35992333, -0.38365025,  0.85045146],
       [ 0.29022823,  0.91235553,  0.28874724],
       [-0.88669204,  0.14289815,  0.43972417]]), 't': array([-1887.59083233,  -592.76263696,  1853.96280811])}, {'R': array([[-0.30109701, -0.40285337,  0.8643204 ],
       [ 0.55102509,  0.66624182,  0.502487  ],
       [-0.77827498,  0.62755956,  0.0213789 ]]), 't': array([-2106.76395937,  -946.51826108,  2398.70349817])}]