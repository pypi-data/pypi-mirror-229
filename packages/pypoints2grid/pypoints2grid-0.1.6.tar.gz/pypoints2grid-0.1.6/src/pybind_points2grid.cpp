#include <limits>
#include <math.h>
#include <stddef.h>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "GridEnum.h"
#include "Interpolator.h"

#include <chrono>


using namespace std;
namespace py = pybind11;

size_t count_set_bits(size_t n) {
    size_t count = 0;
    while (n) {
        count += n & 1;
        n >>= 1;
    }
    return count;
}

py::array_t<double> _points2grid(py::array_t<double> pts, double cell_size,
                                 double x_min, double y_min, double x_max,
                                 double y_max, double radius, int window_size,
                                 bool check_bounds, size_t grid_data, bool verbose) {

    auto pts_r = pts.unchecked<2>();
    size_t pt_count = pts_r.shape(0);

    if (radius <= 0) {
        radius = (std::sqrt(2.0) * cell_size)/2;
    }

    if (cell_size <= 0) {
        domain_error("Cell size must be great than 0");
    }

    // The user defines the edges of the bounding box, here we want the min/max
    // values to represent the centers of the edge cells
    double orig_x_min = x_min;
    double orig_y_min = y_min;
    double orig_x_max = x_max;
    double orig_y_max = y_max;

    x_min = x_min + cell_size / 2.0;
    x_max = x_max - cell_size / 2.0;
    y_min = y_min + cell_size / 2.0;
    y_max = y_max - cell_size / 2.0;

    size_t size_x = (size_t) (std::ceil((x_max - x_min) / cell_size)) + 1;
    size_t size_y = (size_t) (std::ceil((y_max - y_min) / cell_size)) + 1;

    if (verbose)
        py::print("generating grid with size (", size_x, ",", size_y, ")");
    auto grid_interp = Interpolator(cell_size, cell_size, size_x, size_y, radius,
                                    x_min, x_max, y_min, y_max, window_size);

    //auto t0_init = std::chrono::high_resolution_clock::now();
    grid_interp.init();
    //auto t1_init = std::chrono::high_resolution_clock::now();
    //std::cout << "init time: " << std::chrono::duration_cast<std::chrono::milliseconds>(t1_init - t0_init).count() << " ms" << std::endl;


    double x, y, z;
    //auto t0_update = std::chrono::high_resolution_clock::now();
    for (size_t i = 0; i < pt_count; i++) {
        x = pts_r(i, 0);
        y = pts_r(i, 1);
        z = pts_r(i, 2);
        if (check_bounds) {
            if (x < orig_x_min || x > orig_x_max || y < orig_y_min || y > orig_y_max)
                continue;
        }
        grid_interp.update(x, y, z);
    }
    //auto t1_update = std::chrono::high_resolution_clock::now();
    //std::cout << "update time: " << std::chrono::duration_cast<std::chrono::milliseconds>(t1_update - t0_update).count() << " ms" << std::endl;

    //auto t0_finalize = std::chrono::high_resolution_clock::now();
    grid_interp.calculate_grid_values();
    //auto t1_finalize = std::chrono::high_resolution_clock::now();
    //std::cout << "finalize time: " << std::chrono::duration_cast<std::chrono::milliseconds>(t1_finalize - t0_finalize).count() << " ms" << std::endl;

    size_t num_layers = count_set_bits(grid_data);

    //auto t0_get = std::chrono::high_resolution_clock::now();
    py::array_t<double> result = py::array_t<double>(size_x * size_y * num_layers);
    py::buffer_info result_buf = result.request();
    double *result_ptr = (double *) result_buf.ptr;
    for (size_t idx = 0; idx < size_x; idx++) {
        for (size_t idy = 0; idy < size_y; idy++) {
            auto gp = grid_interp.get_grid_point(idx, idy);
            size_t offset = idx * size_y * num_layers + idy * num_layers;
            if (grid_data & GridData::IDW) {
                result_ptr[offset] = gp.Zidw;
                offset++;
            }
            if (grid_data & GridData::MIN) {
                result_ptr[offset] = gp.Zmin;
                offset++;
            }
            if (grid_data & GridData::MAX) {
                result_ptr[offset] = gp.Zmax;
                offset++;
            }
            if (grid_data & GridData::MEAN) {
                result_ptr[offset] = gp.Zmean;
                offset++;
            }
            if (grid_data & GridData::STD) {
                result_ptr[offset] = gp.Zstd;
                offset++;
            }

        }
    }
    result.resize({size_x, size_y, num_layers});
    //auto t1_get = std::chrono::high_resolution_clock::now();
    //std::cout << "get time: " << std::chrono::duration_cast<std::chrono::milliseconds>(t1_get - t0_get).count() << " ms" << std::endl;
    return result;
}

PYBIND11_MODULE(_points2grid, m) {
    m.doc() = "implementation of points2grid algorithm";
    m.def("_points2grid", &_points2grid, "generate grid from pointcloud");
}