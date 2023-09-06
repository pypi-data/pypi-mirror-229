import numpy as np


def uniform_interpolate(x, y):
    """
    Interpolate a dataset to have uniformly distributed x coordinates using linear interpolation.

    Parameters:
    - x (np.ndarray): The original x coordinates.
    - y (np.ndarray): The corresponding y values.

    Returns:
    - tuple[np.ndarray, np.ndarray]: A tuple containing the uniformly spaced x coordinates
      and the interpolated y values.

    This function transforms a dataset by interpolating it to have uniformly distributed
    x coordinates. Linear interpolation is used to estimate y values at the uniformly
    spaced x coordinates.
    """
    uniform_x = np.linspace(min(x), max(x), len(x))
    interpolated_y = np.interp(uniform_x, x, y)

    return uniform_x, interpolated_y
