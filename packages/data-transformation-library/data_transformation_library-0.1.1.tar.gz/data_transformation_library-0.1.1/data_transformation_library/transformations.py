import numpy as np


def transpose2d(input_matrix: list[list[float]]) -> list:
    """
    Switches the axes of a tensor.
    :param input_matrix: is a list of lists of real numbers.
    :return:
    """
    if not input_matrix:
        return []
    transposed_matrix = [[input_matrix[j][i] for j in range(len(input_matrix))] for i in range(len(input_matrix[0]))]
    return transposed_matrix


def window1d(input_array: list | np.ndarray, size: int, shift: int = 1, stride: int = 1) -> list[list | np.ndarray]:
    """
    Creates an overlapping or non-overlapping 1D windows from an input array.
    :param input_array: a list or 1D Numpy array of real numbers
    :param size: is a positive integer that determines the size (length) of the window
    :param shift: is a positive integer that determines the shift (step size) between different windows
    :param stride: is a positive integer that determines the stride (step size) within each window.
    :return: a list of lists or 1D Numpy arrays of real numbers.
    """
    if size <= 0:
        raise ValueError("size must be a positive integer")
    if shift <= 0:
        raise ValueError("shift must be a positive integer")
    if stride <= 0:
        raise ValueError("stride must be a positive integer")

    if isinstance(input_array, list):
        input_array = np.array(input_array)
    windows = []
    for item in range(0, len(input_array) - size + 1, shift):
        window = input_array[item:item + size:stride]
        windows.append(window)

    return windows


def convolution2d(input_matrix: np.ndarray, kernel: np.ndarray, stride: int = 1) -> np.ndarray:
    """
    Performs 2D convolution between an input matrix and a kernel.
    :param input_matrix: s a 2D Numpy array of real numbers
    :param kernel: is a 2D Numpy array of real numbers
    :param stride: is an integer that is greater than 0
    :return: a 2D Numpy array of real numbers
    """
    if not isinstance(stride, int) or stride <= 0:
        raise ValueError("Stride must be a positive integer.")

    kernel_h, kernel_w = kernel.shape
    input_h, input_w = input_matrix.shape

    if kernel_h > input_h or kernel_w > input_w:
        raise ValueError("Kernel dimensions are incompatible with input_matrix.")

    output_h = (input_h - kernel_h) // stride + 1
    output_w = (input_w - kernel_w) // stride + 1
    output = np.zeros((output_h, output_w))

    for i in range(0, output_h, stride):
        for j in range(0, output_w, stride):
            output[i // stride, j // stride] = (input_matrix[i:i + kernel_h, j:j + kernel_w] * kernel).sum()

    return output
