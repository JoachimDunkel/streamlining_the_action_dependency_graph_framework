from typing import Tuple

import numpy as np


def lerp_a_to_b(a: Tuple[int, int], b: Tuple[int, int], steps: int) -> np.ndarray:
    try:
        x_values = np.linspace(a[0], b[0], steps)
        y_values = np.linspace(a[1], b[1], steps)
        return np.vstack((x_values, y_values)).T
    except ValueError as e:
        print(f"Error: {e}")
    

