import numpy as np
import math as m


def ksmooth(
    data: np.ndarray,
    kernel: np.ndarray,
) -> np.ndarray:
    half = len(kernel) // 2
    padded_data = np.pad(data, (half, half), "edge")
    smoothed_data = np.convolve(padded_data, kernel, mode="valid")
    return smoothed_data


def average(data: np.ndarray, size: int) -> np.ndarray:
    kernel = np.ones(size) / size
    return kernel


def gaussian(data: np.ndarray, size: int, sigma: float) -> np.ndarray:
    if size % 2 == 0:
        raise ValueError("Kernel size should be an odd number.")

    half = size // 2
    x = np.arange(-half, half + 1)
    gauss = np.vectorize(
        lambda x: (1 / (np.sqrt(2 * np.pi) * sigma))
        * np.exp(-(x**2) / (2 * sigma**2))
    )
    kernel = gauss(x)
    kernel /= np.sum(kernel)
    return kernel


def sinc(data: np.ndarray, size: int, spread: float) -> np.ndarray:
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


def exponential(data: np.ndarray, size: int, fac: float) -> np.ndarray:
    if size % 2 == 0:
        raise ValueError("Kernel size should be an odd number.")
    if not (0 < fac <= 1):
        raise ValueError("Smoothing factor should be a float between 0 and 1")

    half = size // 2
    x = np.arange(-half, half + 1, dtype=float)
    kernel = fac ** np.abs(x)
    kernel /= np.sum(kernel)
    return kernel


def savgol(data: np.ndarray, size: int, order: int, deriv: int) -> np.ndarray:
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
    kernel = H[deriv] * m.factorial(deriv) * [(-1) ** deriv]
    return kernel
