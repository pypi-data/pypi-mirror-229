import unittest

from pypoints2grid import points2grid

import numpy as np


class TestPoints2Grid(unittest.TestCase):
    def test_points2grid1(self):
        pts = np.array([[0, 0, 1], [0, 1, 2], [1, 0, 3], [1, 1, 4]])
        expected_grid = np.array([2.5])
        grid = points2grid(pts, cell_size=1)
        np.testing.assert_array_almost_equal(grid, expected_grid)

    def test_points2grid05(self):
        pts = np.array([[0, 0, 1], [0, 1, 2], [1, 0, 3], [1, 1, 4]])
        expected_grid = np.array([[1.0, 2.0], [3.0, 4.0]])
        grid = points2grid(pts, cell_size=0.5)
        np.testing.assert_array_almost_equal(grid, expected_grid)


class TestDemSize(unittest.TestCase):
    def setUp(self) -> None:
        self.pts = np.random.rand(1000, 3)

    def test_dem_size(self):
        dem = points2grid(self.pts, 0.1)
        self.assertEqual(dem.shape, (10, 10), "incorrect dem size")

        dem2 = points2grid(self.pts, 0.01)
        self.assertEqual(dem2.shape, (100, 100), "incorrect dem size")

    def test_dem_bounding_box(self):
        bounds = (0.25, 0.25, 0.75, 0.75)
        dem = points2grid(self.pts, 0.01, bounds=bounds)
        self.assertEqual(dem.shape, (50, 50), "incorrect bounded dem size")


class TestDemIDW(unittest.TestCase):
    def setUp(self) -> None:
        pt_count = 25000
        xy = np.random.rand(pt_count, 2)
        z = np.ones(pt_count).reshape((-1, 1))
        self.pts = np.hstack((xy, z))

    def test_dem_values(self):
        dem = points2grid(self.pts, 0.01)
        self.assertTrue(np.all(dem == 1))


class TestDemMinMax(unittest.TestCase):
    def setUp(self) -> None:
        pt_count = 25000
        xy = np.random.rand(pt_count, 2)
        z = np.ones(pt_count).reshape((-1, 1))
        z[240] = -100
        z[450] = 100
        self.pts = np.hstack((xy, z))

    def test_min_dem_value(self):
        dem = points2grid(self.pts, 0.01, window_size=0, grid_data=["min"])

        self.assertEqual(dem.min(), -100)
        self.assertTrue(np.sum(dem == -100) < 3)

    def test_max_dem_value(self):
        dem = points2grid(self.pts, 0.01, window_size=0, grid_data=["max"])
        self.assertTrue(dem.max() == 100)
        self.assertTrue(np.sum(dem == 100) < 3)

    def test_multiple_grid_data(self):
        dem = points2grid(
            self.pts, 0.01, window_size=3, grid_data=["idw", "min", "max"]
        )
        dem_idw = points2grid(self.pts, 0.01, window_size=3, grid_data=["idw"])
        dem_min = points2grid(self.pts, 0.01, window_size=3, grid_data=["min"])
        dem_max = points2grid(self.pts, 0.01, window_size=3, grid_data=["max"])
        w, h, c = dem.shape
        self.assertEqual(c, 3)
        self.assertTrue(np.all(dem[:, :, 0] == dem_idw))
        self.assertTrue(np.all(dem[:, :, 1] == dem_min))
        self.assertTrue(np.all(dem[:, :, 2] == dem_max))

    def test_multiple_grid_data_swapped_order(self):
        dem = points2grid(
            self.pts, 0.01, window_size=3, grid_data=["mean", "max", "min"]
        )
        dem_mean = points2grid(self.pts, 0.01, window_size=3, grid_data=["mean"])
        dem_min = points2grid(self.pts, 0.01, window_size=3, grid_data=["min"])
        dem_max = points2grid(self.pts, 0.01, window_size=3, grid_data=["max"])
        w, h, c = dem.shape
        self.assertEqual(c, 3)
        self.assertTrue(np.all(dem[:, :, 0] == dem_mean))
        self.assertTrue(np.all(dem[:, :, 1] == dem_max))
        self.assertTrue(np.all(dem[:, :, 2] == dem_min))


if __name__ == "__main__":
    unittest.main()
