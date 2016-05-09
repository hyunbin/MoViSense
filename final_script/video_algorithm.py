# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2
import math
import numpy as np

class Object:
	def __init__(self, x, y, w, h, numFrames):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.numDataPoints = 0
		self.motionValues = [-1 for x in range(numFrames)]

	def appendMotion(self, time, val):
		self.motionValues[time] = val
		self.numDataPoints = self.numDataPoints + 1

def calculate_overlap(a, b):
	SA = a.w * a.h
	SB = b.w * b.h
	SI = max(0, min(a.x + a.w, b.x + b.w) - max(a.x, b.x)) * max(0, min(a.y + a.h, b.y + b.h) - max(a.y, b.y))
	S = SA + SB - SI
	return SI / S

def calculate_motion_alphabet(data, fps):
	alphabet = []
	count = 0
	for i in range(0, len(data), fps):
		# chunk is a subarray of the current slice of data
		chunk = data[i: i + fps - 1]
		print("For ", count, "to", count + 1)
		print(" > Start and end diff =", chunk[-1] - chunk[0])
		print(" > Var =", np.var(chunk))
		# If either start or end was in not in frame
		if chunk[-1] == -1 or chunk[0] == -1:
			alphabet.append('x') # means "I don't see you"
			continue
		if np.var(chunk) < 100: # TODO play around with this value
			alphabet.append('s') # means "stop"
		elif chunk[-1] - chunk[0] > 75:
			alphabet.append('f') # means "forward"
		elif chunk[-1] - chunk[0] < -75:
			alphabet.append('r') # means "reverse"
		elif chunk[-1] - chunk[0] > 10:
			alphabet.append('ft') # means "forward transition" aka forward for some part of the second
		elif chunk[-1] - chunk[0] < -10:
			alphabet.append('rt') # means "reverse transition" aka reverse for some part of the second
		else:
			alphabet.append('?')
		count = count + 1
	return alphabet

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=2000, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	camera = cv2.VideoCapture(0)
	time.sleep(0.25)
 
# otherwise, we are reading from a video file
else:
	camera = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None

# initialize the list of video objects
objects = []

# Frame rate
frameRate = round(camera.get(cv2.CAP_PROP_FPS))
totalNumFrames = round(camera.get(cv2.CAP_PROP_FRAME_COUNT))
print("FrameRate =", frameRate)

# loop over the frames of the video
while True:
	# Find next frame number to read
	frameNum = round(camera.get(cv2.CAP_PROP_POS_FRAMES))

	# grab the current frame and initialize the occupied/unoccupied text
	(grabbed, frame) = camera.read()
 
	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if not grabbed:
		break

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# corner case: if the first frame is None, initialize it and mov on
	if firstFrame is None:
		firstFrame = gray
		continue

	# compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 10, 255, cv2.THRESH_BINARY)[1]
 
	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	(_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, 
		cv2.CHAIN_APPROX_SIMPLE)

	# loop over the contours, pick the biggest one
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue
	
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

		# calculate the average x position of the box
		avgX = x + w/2
		newObject = Object(x, y, w, h, 0)

		# corner case: if first object then add to objects array
		if len(objects) is 0:
			newObject = Object(x, y, w, h, totalNumFrames)
			objects.append(newObject)
			continue

		# check overlap in box area between our object and existing objects
		maxOverlap = 0
		likelyObject = None
		for o in objects:
			percentage = calculate_overlap(newObject, o)
			if maxOverlap < percentage:
				maxOverlap = percentage
				likelyObject = o

		# if closest match was below threshold then append 
		# a new object to the list
		# TODO play around with this threshold?
		if maxOverlap < 0.2:
			newObject = Object(x, y, w, h, totalNumFrames)
			objects.append(newObject)
			newObject.appendMotion(frameNum, avgX)
			# print("Appending a new box, maxOverlap =", maxOverlap)
			continue
		# else overwrite old box's values
		else:
			likelyObject.x = x
			likelyObject.y = y
			likelyObject.w = w
			likelyObject.h = h
			likelyObject.appendMotion(frameNum, avgX)
			# print("Overwriting old box at", likelyObject)

	# draw the text and timestamp on the frame
	# cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
	#		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	# cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
	#		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
 
	# show the frame and record if the user presses a key
	cv2.imshow("Video", frame)
	# cv2.imshow("Thresh", thresh)
	# cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key is pressed, break from the loop
	if key == ord("q"):
		break

# Now calculate motion data for each object
for o in objects:
	# Skip calculation for insignificant blips of data
	if o.numDataPoints < totalNumFrames / 10:
		continue
	alphabet = calculate_motion_alphabet(o.motionValues, frameRate)
	print("Object's motion alphabet is as follows:", alphabet)

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()