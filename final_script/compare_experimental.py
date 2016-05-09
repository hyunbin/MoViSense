import numpy as np

def alphabet_to_numerical(data):
	for index, item in enumerate(data):
		if item == 'f':
			data[index] = 2
		elif item == 'ft':
			data[index] = 1
		elif item == 's':
			data[index] = 0
		elif item == 'rt':
			data[index]  = -1
		elif item == 'r':
			data[index] = -2
	return data

def numerical_to_alphabet(data):
	for index, item in enumerate(data):
		if item == 2:
			data[index] = 'f'
		elif item == 1:
			data[index] = 'ft'
		elif item == 0:
			data[index] = 's'
		elif item == -1:
			data[index]  = 'rt'
		elif item == -2:
			data[index] = 'r'
	return data

inputA = input('Enter alphabet from video data\n')
inputB = input('Enter alphabet from mobile data\n')
arrayA = eval(inputA)
arrayB = eval(inputB)

# arrayA = ['x', 'x' , 'f', 'ft', 's', 's', 'r', 'rt', 's', 's', 'f', 'f', 'f', 's', 's', 'rt', 'r', 'rt', 's', 's', 'r', 'rt', 'x', 'x']
# arrayB = ['s', 'f', 'f', 'f', 's', 's', 'r', 'r', 's', 'f', 's', 'f', 'f', 'f', 'f', 's', 'r', 'r', 's', 's', 's', 'r', 'r', 'r', 's', 's']

# Truncate 'x' data from video data
while 'x' in arrayA:
	arrayA.remove('x')

if len(arrayA) > len(arrayB):
	longerArray = arrayA
	shorterArray = arrayB
else:
	longerArray = arrayB
	shorterArray = arrayA

# Replace motion data in both videos
arrayA = alphabet_to_numerical(arrayA)
arrayB = alphabet_to_numerical(arrayB)

print(arrayA)
print(arrayB)
print('\n\n')

bestFit = None
bestShorterFit = None
bestFitPenaltyCounter = 4 * len(shorterArray)

# Compare against regular shorter array
for i in range(0, len(longerArray) - len(shorterArray)):
	truncatedArray = longerArray[i : i + len(shorterArray)]
	totalCounter = len(truncatedArray)
	penaltyCounter = 0
	print('Now comparing (forwards): ')
	print('', truncatedArray, '\n', shorterArray)
	# Calculate the difference in values for all possible combinations
	for i in range(0, len(truncatedArray)):
		penaltyCounter += abs(shorterArray[i] - truncatedArray[i])
	print(' Variance was:', penaltyCounter)
	# See if penalty counter was lower than the best so far
	if penaltyCounter < bestFitPenaltyCounter:
		print(' Replacing current best of:', bestFitPenaltyCounter)
		bestFit = truncatedArray
		bestFitPenaltyCounter = penaltyCounter
		bestShorterFit = shorterArray

# Flip shorter array and compare again
reverseArray = [0 for x in range(len(shorterArray))]
for i in range(0, len(shorterArray)):
	reverseArray[i] = -shorterArray[i]

# Compare against regular shorter array
for i in range(0, len(longerArray) - len(reverseArray)):
	truncatedArray = longerArray[i : i + len(reverseArray)]
	totalCounter = len(truncatedArray)
	penaltyCounter = 0
	print('Now comparing (backwards): ')
	print('', truncatedArray, '\n', shorterArray)
	# Calculate the difference in values for all possible combinations
	for i in range(0, len(truncatedArray)):
		penaltyCounter += abs(reverseArray[i] - truncatedArray[i])
	print(' Variance was:', penaltyCounter)
	# See if penalty counter was lower than the best so far
	if penaltyCounter < bestFitPenaltyCounter:
		print(' Replacing current best of:', bestFitPenaltyCounter)
		bestFit = truncatedArray
		bestFitPenaltyCounter = penaltyCounter
		bestShorterFit = reverseArray

bestFit = numerical_to_alphabet(bestFit)
shorterArray = numerical_to_alphabet(shorterArray)

bestConfidence = (4 * len(shorterArray) - bestFitPenaltyCounter) / (4 * len(shorterArray))
print('Best fit is as follows w/ confidence =', bestConfidence)
print(bestFit)
print(shorterArray)
