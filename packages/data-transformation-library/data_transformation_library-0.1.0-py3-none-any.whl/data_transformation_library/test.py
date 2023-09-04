from transformations import convolution2d
import numpy as np


input_matrix = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])

kernel = np.array([
    [0, 1],
    [2, 3]
])

stride = 1

# Call the convolution2d function
result = convolution2d(input_matrix, kernel, stride=stride)

# Print the result of the convolution
print("Result of 2D Convolution:")
print(result)


