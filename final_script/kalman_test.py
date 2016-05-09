import cv2
import numpy as np

kalman = None
kalman = cv2.KalmanFilter(4, 4)

kalman.measurementMatrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32)
kalman.transitionMatrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32)
kalman.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32) * 0.03

count = 0
while 1:
	result = kalman.predict()
	print(result)
	if count%10 == 0:
		kalman.correct(np.array((1.0, 0.5, 0.3, 0.4), np.float32))
	count += 1