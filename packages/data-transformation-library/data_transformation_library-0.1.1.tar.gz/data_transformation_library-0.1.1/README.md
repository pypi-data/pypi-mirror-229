# Sprint 5:  Data Transformation Library

The Data Transformation Library is a Python library that provides a set of functions for common data transformation tasks. 
It is designed to simplify the process of handling and processing data, making it easier for developers to work with various types of data structures.

# Installation

You can install the library using pip:

<i>pip install data-transformation-library</i>

# Features
## transpose2d

The transpose2d function switches the axes of a 2D tensor, making it easy to transform rows into columns and vice versa.

<i>import data_transformation_library   

input_matrix = [[1, 2, 3], [4, 5, 6]]   
transposed_matrix = data_transformation_library.transpose2d(input_matrix)</i>

## window1d

The window1d function creates overlapping or non-overlapping 1D windows from an input array. This is useful for tasks like time series analysis and data segmentation.

<i>import data_transformation_library  
import numpy as np  

input_array = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])  
windows = data_transformation_library.window1d(input_array, size=3, shift=2, stride=1)</i>

## concolution2d

The convolution2d function performs 2D convolution between an input matrix and a kernel. This is a fundamental operation in image processing and feature extraction.

<i>import data_transformation_library  
import numpy as np  

input_matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])  
kernel = np.array([[0, 1], [2, 3]])  
stride = 1  
result = data_transformation_library.convolution2d(input_matrix, kernel, stride=stride)</i>

## Link to the pip package 

https://pypi.org/project/data-transformation-library/




