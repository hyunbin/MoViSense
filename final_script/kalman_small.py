import cv2
import numpy as np

kalman = None
kalman = cv2.KalmanFilter(1, 1)

kalman.measurementMatrix = np.array([[1]],np.float32)
kalman.transitionMatrix = np.array([[1]],np.float32)
kalman.processNoiseCov = np.array([[1]],np.float32) * 0.03

count = 0
while 1:
	result = kalman.predict()
	print(result)
	if count%10 == 0:
		kalman.correct(np.array((1.0), np.float32))
	count += 1