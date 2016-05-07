
inputA = input('Enter array 1\n')
inputB = input('Enter array 2\n')
arrayA = eval(inputA)
arrayB = eval(inputB)
# print('Your input A was: ', arrayA)
# print('Your input B was: ', arrayB)

# arrayA = ['s', 'f', 'f', 'f', 's', 's', 'f', 's', 's', 's', 's', 'r', 'r', 'r', 's', 's', 'r', 's', 's', 's', 's', 'f', 'f', 'f', 's', 'f', 'f', 'r', 's']
# arrayB = ['s', 'f', 'f', 'f', 'f', 's', 's', 'f', 'f', 's', 's', 's', 's', 'r', 'r', 'r', 's', 'r', 'r', 's', 's', 'f', 's', 'f', 'f', 's', 's', 'f', 'f', 'f', 's', 's']

if len(arrayA) > len(arrayB):
	longerArray = arrayA
	shorterArray = arrayB
else:
	longerArray = arrayB
	shorterArray = arrayA

bestFit = None
bestShorterFit = None
bestFitMatchCounter = 0

# Compare against regular shorter array
for i in range(0, len(longerArray) - len(shorterArray)):
	truncatedArray = longerArray[i : i + len(shorterArray)]
	totalCounter = len(truncatedArray)
	matchCounter = 0
	diffCounter = 0
	for i in range(0, len(truncatedArray)):
		if shorterArray[i] == truncatedArray[i]:
			# print('match @', i)
			matchCounter += 1
		else:
			# print('diff @', i)
			diffCounter += 1
	# print('Foward array, Confidence =', matchCounter / len(shorterArray))
	# print(shorterArray)
	# print(truncatedArray)
	# print('\n')
	if matchCounter > bestFitMatchCounter:
		bestFit = truncatedArray
		bestFitMatchCounter = matchCounter
		bestShorterFit = shorterArray

# Flip shorter array and compare again
reverseArray = [0 for x in range(len(shorterArray))]
for i in range(0, len(shorterArray)):
	if shorterArray[i] == 'f':
		reverseArray[i] = 'r'
	elif shorterArray[i] == 'r':
		reverseArray[i] = 'f'
	else:
		reverseArray[i] = shorterArray[i]

print(reverseArray)
print(shorterArray)

for i in range(0, len(longerArray) - len(reverseArray)):
	truncatedArray = longerArray[i : i + len(reverseArray)]
	totalCounter = len(truncatedArray)
	matchCounter = 0
	diffCounter = 0
	for i in range(0, len(truncatedArray)):
		if reverseArray[i] == truncatedArray[i]:
			matchCounter += 1
		else:
			diffCounter += 1
	# print('Reverse array, Confidence =', matchCounter / len(reverseArray))
	# print(reverseArray)
	# print(truncatedArray)
	# print('\n')
	if matchCounter > bestFitMatchCounter:
		bestFit = truncatedArray
		bestFitMatchCounter = matchCounter
		bestShorterFit = reverseArray

print('Best fit is as follows w/ confidence =', bestFitMatchCounter / len(shorterArray))
print(bestFit)
print(shorterArray)
