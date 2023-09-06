import numpy as np
import math as m


def moving_average_kernel(size: int) -> np.ndarray:
    """
    Generate a moving average kernel of a given size.

    Parameters:
        size (int): The size of the moving average kernel.

    Returns:
        np.ndarray: The moving average kernel as a 1-dimensional NumPy array.
    """
    kernel = np.ones(size) / size
    return kernel

def gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    """
    Generate a 1D Gaussian kernel.

    Parameters:
    - size (int): The size of the kernel (should be an odd number).
    - sigma (float): The standard deviation of the Gaussian distribution.

    Returns:
    - np.ndarray: The 1D Gaussian kernel as a NumPy array.
    """
    if size % 2 == 0:
        raise ValueError("Kernel size should be an odd number.")
    
    half = size // 2
    x = np.arange(-half, half + 1)
    gauss = np.vectorize(lambda x: (1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(-(x ** 2) / (2 * sigma**2)))
    kernel = gauss(x)
    
    kernel /= np.sum(kernel)

    return kernel

def sinc_kernel(size: int, spread: float) -> np.ndarray:
    """
    Generate a 1D sinc kernel.

    Parameters:
    - size (int): The size of the kernel. Should be an odd number.
    - spread (float): The spread (or width) of the sinc function.

    Returns:
    - np.ndarray: A 1D NumPy array containing the sinc kernel.

    Raises:
    - ValueError: If the input size is even or spread is zero.

    """
    if size % 2 == 0:
        raise ValueError("Kernel size should be an odd number.")

    if spread == 0:
        raise ValueError("Spread should be a non-zero float.")

    half = size // 2
    x = np.arange(-half, half + 1)
    sinc = np.vectorize(
        lambda x: 1 if x == 0 else np.sin(np.pi * x / spread) / (np.pi * x / spread)
    )

    kernel = sinc(x)

    kernel /= np.sum(kernel)

    return kernel

def exponential_moving_average_kernel(size: int, alpha: float) -> np.ndarray:
    """
    Generate a 1D Exponential Moving Average (EMA) kernel.

    Parameters:
    - size (int): The size of the kernel (should be an odd number).
    - alpha (float): The smoothing factor for EMA (should be a float between 0 and 1).

    Returns:
    - np.ndarray: The 1D EMA kernel as a NumPy array.
    
    The EMA kernel assigns exponentially decreasing weights to older data points and
    increasing weights to newer data points in a 1D signal. It is commonly used for
    smoothing time series data.
    """
    if size % 2 == 0:
        raise ValueError("Kernel size should be an odd number.")
    
    if not(0 < alpha <= 1):
        raise ValueError("Smoothing factor should be a float between 0 and 1")
    
    half = size // 2
    x = np.arange(-half, half + 1, dtype=float)
    kernel = alpha ** np.abs(x)

    kernel /= np.sum(kernel)

    return kernel

def savitzky_golay_kernel(size: int, order: int, deriv: int) -> np.ndarray:
    """
    Generate a Savitzky-Golay smoothing kernel for a given window size, polynomial order, and derivative order.

    Parameters:
        size (int): The size of the smoothing kernel. Must be an odd integer.
        order (int): The order of the polynomial used for smoothing. Should be less than size.
        deriv (int): The derivative order for which the smoothing kernel is generated.

    Returns:
        np.ndarray: The Savitzky-Golay smoothing kernel as a 1-dimensional NumPy array.
    """
    if size % 2 == 0:
        raise ValueError("Kernel size should be an odd number.")

    if size <= order:
        raise ValueError("Kernel size must be greater than polynomial order.")

    half = size // 2
    x = np.arange(-half, half + 1)
    X = np.vander(x, order + 1, increasing=True)

    X_t = X.T
    inv_Xt_X = np.linalg.inv(np.dot(X_t, X))
    H = np.dot(inv_Xt_X, X_t)

    sg_kernel = H[deriv] * m.factorial(deriv) * [(-1) ** deriv]

    return sg_kernel


def kernel_smoother(
    data: np.ndarray,
    kernel: np.ndarray,
) -> np.ndarray:
    """
    Smooth data using a given kernel.

    Parameters:
        data (np.ndarray): The input data to be smoothed.
        kernel (np.ndarray): The smoothing kernel to be applied to the data.

    Returns:
        np.ndarray: The smoothed data as a 1-dimensional NumPy array.
    """
    half = len(kernel) // 2
    padded_data = np.pad(data, (half, half), "edge")
    smoothed_data = np.convolve(padded_data, kernel, mode="valid")

    return smoothed_data
