import numpy as np


def get_Gaussian_noise(noise_level: float, size: int, mean: float = 0.0):
    """
    Args:
        noise_level : Standard deviation (spread or "width") of the distribution. Must be
                non-negative.
    Returns:

    """
    return np.random.normal(loc=mean, scale=noise_level, size=size)

