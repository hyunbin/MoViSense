import csv
import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
import argparse
import math

# "source activate root" in terminal to begin conda
def butter_lowpass(cutoff, fs, order=5):
	nyq = 0.5 * fs
	normal_cutoff = cutoff / nyq
	b, a = butter(order, normal_cutoff, btype='low', analog=False)
	return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
	b, a = butter_lowpass(cutoff, fs, order=order)
	y = lfilter(b, a, data)
	return y

def num_steps(data):
	# Count zero crossings
	zeroCrossing = 0;
	prev = 0.0;
	for value in data:
		if (prev > 0 and value < 0) or (prev < 0 and value > 0):
			zeroCrossing += 1
		prev = value
	steps = int(zeroCrossing / 2);
	return steps

def calculate_average_interval(data):
	average = 0;
	for i in range(0, len(data) - 1):
		average += int(data[i + 1]) - int(data[i])
	average /= len(data) - 1
	return round(average)

def integrate_gyro_data(x, dT):
	sum = 0.0
	for num in x:
		sum += num * dT
	if abs(sum) >= 10.0:
		return sum
	return 0.0

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", help="path to the raw csv file")
args = vars(ap.parse_args())

# if the file argument is None, then exit
if args.get("file", None) is None:
	print("Please specify a filename")
	exit()

fileName = args.get("file", None)

csvfile = open(fileName, 'rt') # current example uses 25 steps
csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
accelTimeList = []
accelZList = []
gyroTimeList = []
gyroYList = []

# Skips first line of iteration (column name strings)
itercsvreader = iter(csvreader)
next(itercsvreader)
for row in itercsvreader:
	if row[1] != '': # check that we're looking at accelerometer
		accelTimeList.append(row[0]) 
		accelZList.append(float(row[3]) - 9.81)
	elif row[4] != '':
		gyroTimeList.append(row[0])
		gyroYList.append(math.degrees(float(row[6])))

# Calculate average period for both accelerometer and gyroscope measurements
accelInterval = calculate_average_interval(accelTimeList)
gyroInterval = calculate_average_interval(gyroTimeList)
print("accelInterval =", accelInterval, "ms")
print("gyroInterval =", gyroInterval, "ms")

# Plot raw accelerometer data
plt.figure(1)
plt.plot(accelTimeList, accelZList)
plt.title("Accel_z Raw Data")
plt.xlabel("Time [ms]")
plt.ylabel("Accel [m/s^2]")
plt.grid()

# Filter requirements
order = 5
fs = 1000 / accelInterval
cutoff = 2.00   # desired cutoff frequency of the filter, Hz

# Get the filter coefficients so we can check its frequency response.
b, a = butter_lowpass(cutoff, fs, order)

# Plot the frequency response.
w, h = freqz(b, a, worN=8000)

plt.figure(1)
plt.subplot(2, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
plt.axvline(cutoff, color='k')
plt.xlim(0, 0.5*fs)
plt.title("Lowpass Filter Frequency Response")
plt.xlabel('Frequency [Hz]')
plt.grid()

# Filter the data
accelZFiltered = butter_lowpass_filter(accelZList, cutoff, fs, order)

# Count zero crossings
numSteps = num_steps(accelZFiltered)
print("I counted:", numSteps, "steps")

# Plot both the original and filtered signals.
plt.subplot(2, 1, 2)
plt.plot(accelTimeList, accelZList, 'b-', label='data')
plt.plot(accelTimeList, accelZFiltered, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [s]')
plt.grid(True)

# xticks shows subgrids for presentation
maxTime = int(int(accelTimeList[-1]) / 1000) + 1
plt.xticks([1000*w for w in range(maxTime)], ['%i'%w for w in range(maxTime)])
plt.legend()
plt.subplots_adjust(hspace=0.5)

# And now we calculate the motion alphabet for the filtered data...

# Integrate the gyro values to find the orientation at each time period
orientation = []

# We split sample for gyro based on frequency value
gyroFrequency = round(1000 / gyroInterval)
gyroTotal = 0.0
for i in range(0, len(gyroYList), gyroFrequency):
	# chunk is a subarray of the current slice of data
	chunk = gyroYList[i: i + gyroFrequency - 1]
	gyroTotal += integrate_gyro_data(chunk, gyroInterval / 1000)
	orientation.append(gyroTotal)

print(orientation)

# Declare the motion alphabet array!
motionAlphabet = []

# We split samples for accelerometer based on frequency value (fs) 
batchValue = round(fs)
count = 0
for i in range(0, len(accelZFiltered), batchValue):
	# chunk is a subarray of the current slice of data
	chunk = accelZFiltered[i: i + batchValue - 1]
	chunkStepCount = num_steps(chunk)
	print("There were", chunkStepCount, "steps", "for range =", count, "-", count + 1)
	if chunkStepCount > 0:
		if abs(orientation[count]) >= 120 and abs(orientation[count]) <= 240:
			motionAlphabet.append('r')
		else:
			motionAlphabet.append('f')
	else:
		motionAlphabet.append('s')
	count = count + 1

print("Final motion alphabet:")
print(motionAlphabet)

# Show all plots
plt.show()