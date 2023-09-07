import numpy as np

from _points2grid import _points2grid
from enum import Enum
from typing import List, Tuple, Union

__version__ = "0.1.5"


class GridData(Enum):
    IDW = 1 << 0
    MIN = 1 << 1
    MAX = 1 << 2
    MEAN = 1 << 3
    STD = 1 << 4


def points2grid(
    pts: np.ndarray,
    cell_size: float,
    bounds: Union[Tuple[float, float, float, float], None] = None,
    radius: float = 0,
    window_size: int = 3,
    grid_data: List[str] = ["idw"],
    verbose: bool = False,
) -> np.ndarray:
    """
    Interpolates a set of 3D points onto a regular grid.

    Args:
        pts (numpy.ndarray): An array of shape (N, 3) containing the input points.
        cell_size (float): The size of each grid cell.
        bounds (tuple[float, float, float, float], optional): A tuple of (xmin, ymin, xmax, ymax) defining the bounds of the grid. If not provided, the bounds are automatically computed from the input points.
        radius (float, optional): The search radius for each point. If 0, a default radius is computed based on the cell size. Defaults to 0.
        window_size (int, optional): The size of the interpolation window. Must be an odd integer.
        grid_data (List[str], optional): A list of strings specifying the data interpolations to return. Valid values are 'idw', 'min', 'max', 'mean', 'std' Defaults to ['idw'].
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        numpy.ndarray: An (n,m) or (n, m, k) dimensional numpy array containing the interpolated data, where k is the number of data interpolations requested.

    Raises:
        ValueError: If the input points are not a 2D array of shape (N, 3)."""

    if type(pts) is not np.ndarray:
        pts = np.array(pts)
    if len(pts.shape) != 2 or pts.shape[1] != 3:
        raise ValueError(f"points has dimension {pts.shape}. Must be (N,3)")

    check_bounds = True
    if bounds is None:
        x_min, y_min, z_min = pts.min(axis=0)
        x_max, y_max, z_max = pts.max(axis=0)
        check_bounds = False
    else:
        x_min, y_min, x_max, y_max = bounds

    if len(grid_data) == 0:
        grid_data = ["idw"]
    grid_data = [GridData[x.upper()].value for x in grid_data]
    grid_data_enum = sum(grid_data)

    result = _points2grid(
        pts,
        cell_size,
        x_min,
        y_min,
        x_max,
        y_max,
        radius,
        window_size,
        check_bounds,
        grid_data_enum,
        verbose,
    )
    result = np.squeeze(result)
    if len(grid_data) > 1:
        grid_data_args = np.argsort(grid_data)
        result = result[:, :, grid_data_args]
        pass
    return result
