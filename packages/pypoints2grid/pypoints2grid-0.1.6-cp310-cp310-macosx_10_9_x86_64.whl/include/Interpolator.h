// Copyright (C) 2022 Dag Wästberg
// This is a stripped down and simplified version of points2grid as
// provided by https://github.com/CRREL/points2grid
// Original copyright below

/*
*
COPYRIGHT AND LICENSE

Copyright (c) 2011 The Regents of the University of California.
All rights reserved.

Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following
conditions are met:

1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided
with the distribution.

3. All advertising materials mentioning features or use of this
software must display the following acknowledgement: This product
includes software developed by the San Diego Supercomputer Center.

4. Neither the names of the Centers nor the names of the contributors
may be used to endorse or promote products derived from this
software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
*
*
* Based on the notes by Prof. Ramon Arrowsmith(ramon.arrowsmith@asu.edu)
* Authors: Han S Kim (hskim@cs.ucsd.edu), Sriram Krishnan (sriram@sdsc.edu)
*
*/

#ifndef P2G_INTERPOLATOR_H
#define P2G_INTERPOLATOR_H

#include <iostream>
#include <iomanip> 
#include <float.h>
#include <math.h>

#include "GridPoint.h"
#include "GridEnum.h"

using namespace std;

class Interpolator
{
public:
  Interpolator(double dist_x, double dist_y,
               int size_x, int size_y,
               double radius,
               double _min_x, double _max_x,
               double _min_y, double _max_y,
               int _window_size, const size_t grid_data=0)
  {
    GRID_DIST_X = dist_x;
    GRID_DIST_Y = dist_y;

    GRID_SIZE_X = size_x;
    GRID_SIZE_Y = size_y;

    radius_sqr = radius * radius;

    min_x = _min_x;
    max_x = _max_x;
    min_y = _min_y;
    max_y = _max_y;

    window_size = _window_size;
  }

  ~Interpolator()
  {
    for (int i = 0; i < GRID_SIZE_X; ++i)
    {
      free(interp[i]);
    }
    free(interp);
  }

  int init()
  {
    int i, j;

    interp = (GridPoint **)malloc(sizeof(GridPoint *) * GRID_SIZE_X);
    // interp = new GridPoint*[GRID_SIZE_X];
    if (interp == NULL)
    {
      cerr << "InCoreInterp::init() new allocate error" << endl;
      return -1;
    }

    for (i = 0; i < GRID_SIZE_X; i++)
    {
      interp[i] = (GridPoint *)malloc(sizeof(GridPoint) * GRID_SIZE_Y);
      // interp[i] = new GridPoint[GRID_SIZE_Y];
      if (interp[i] == NULL)
      {
        cerr << "InCoreInterp::init() new allocate error" << endl;
        return -1;
      }
    }

    for (i = 0; i < GRID_SIZE_X; i++)
      for (j = 0; j < GRID_SIZE_Y; j++)
      {
        interp[i][j].Zmin = DBL_MAX;
        interp[i][j].Zmax = -DBL_MAX;
        interp[i][j].Zmean = 0;
        interp[i][j].count = 0;
        interp[i][j].Zidw = 0;
        interp[i][j].sum = 0;
        interp[i][j].Zstd = 0;
        interp[i][j].Zstd_tmp = 0;
        interp[i][j].empty = 0;
        interp[i][j].filled = 0;
      }

    // Info"InCoreInterp::init() done" << endl;

    return 0;
  }

  int update(double data_x, double data_y, double data_z)
  {
    double x;
    double y;
    // cerr << "x: " << str(x) << endl;

    int lower_grid_x;
    int lower_grid_y;

    data_x -= min_x;
    data_y -= min_y;

    // cerr << setprecision(12) << GRID_DIST_X << " " << GRID_DIST_Y << endl;
    // cerr << setprecision(12) << "data " << data_x << " " << data_y << endl;
    lower_grid_x = (int)floor((double)data_x / GRID_DIST_X);
    lower_grid_y = (int)floor((double)data_y / GRID_DIST_Y);
    // cerr << setprecision(12) << "lower " << lower_grid_x << " " <<lower_grid_y << endl;
    if (lower_grid_x > GRID_SIZE_X || lower_grid_y > GRID_SIZE_Y)
    {
      cerr << setprecision(12) << GRID_SIZE_X << " " << GRID_SIZE_Y << endl;
      cerr << setprecision(12) << "larger at (" << lower_grid_x << "," << lower_grid_y << "): (" << data_x << ", " << data_y << ")" << endl;
      return 0;
    }

    // printf("lower_grid_x: %d, grid_y: %d, arrX: %.2f, arrY: %.2f\n", lower_grid_x, lower_grid_y, arrX[i], arrY[i]);
    x = (data_x - (lower_grid_x)*GRID_DIST_X);
    y = (data_y - (lower_grid_y)*GRID_DIST_Y);

    // cerr << "(" << data_x << " " << data_y << ")=(" << lower_grid_x << ", " << lower_grid_y << ")" << endl;
    // cerr << "(" << x << " " << y << ")" << endl;


    update_first_quadrant(data_z, lower_grid_x + 1, lower_grid_y + 1, GRID_DIST_X - x, GRID_DIST_Y - y);
    update_second_quadrant(data_z, lower_grid_x, lower_grid_y + 1, x, GRID_DIST_Y - y);
    update_third_quadrant(data_z, lower_grid_x, lower_grid_y, x, y);
    update_fourth_quadrant(data_z, lower_grid_x + 1, lower_grid_y, GRID_DIST_X - x, y);

    // cerr << "test" << endl;
    return 0;
  }

  void calculate_grid_values()
  {
    for (int i = 0; i < GRID_SIZE_X; i++)
      for (int j = 0; j < GRID_SIZE_Y; j++)
      {
        if (interp[i][j].Zmin == DBL_MAX)
        {
          //		interp[i][j].Zmin = NAN;
          interp[i][j].Zmin = 0;
        }

        if (interp[i][j].Zmax == -DBL_MAX)
        {
          // interp[i][j].Zmax = NAN;
          interp[i][j].Zmax = 0;
        }

        if (interp[i][j].count != 0)
        {
          interp[i][j].Zmean /= interp[i][j].count;
          interp[i][j].empty = 1;
        }
        else
        {
          // interp[i][j].Zmean = NAN;
          interp[i][j].Zmean = 0;
        }

        // https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Online_algorithm
        if (interp[i][j].count != 0)
        {
          interp[i][j].Zstd = interp[i][j].Zstd / (interp[i][j].count);
          interp[i][j].Zstd = sqrt(interp[i][j].Zstd);
        }
        else
        {
          interp[i][j].Zstd = 0;
        }

        if (interp[i][j].sum != 0 && interp[i][j].sum != -1)
          interp[i][j].Zidw /= interp[i][j].sum;
        else if (interp[i][j].sum == -1)
        {
          // do nothing
        }
        else
        {
          // interp[i][j].Zidw = NAN;
          interp[i][j].Zidw = 0;
        }
      }

    // Sriram's edit: Fill zeros using the window size parameter
    if (window_size != 0)
    {
      int window_dist = window_size / 2;
      for (int i = 0; i < GRID_SIZE_X; i++)
        for (int j = 0; j < GRID_SIZE_Y; j++)
        {
          if (interp[i][j].empty == 0)
          {
            double new_sum = 0.0;
            for (int p = i - window_dist; p <= i + window_dist; p++)
            {
              for (int q = j - window_dist; q <= j + window_dist; q++)
              {
                if ((p >= 0) && (p < GRID_SIZE_X) && (q >= 0) && (q < GRID_SIZE_Y))
                {
                  if ((p == i) && (q == j))
                    continue;

                  if (interp[p][q].empty != 0)
                  {
                    double distance = max(abs(p - i), abs(q - j));
                    interp[i][j].Zmean += interp[p][q].Zmean / (pow(distance, WEIGHTER));
                    interp[i][j].Zidw += interp[p][q].Zidw / (pow(distance, WEIGHTER));
                    interp[i][j].Zstd += interp[p][q].Zstd / (pow(distance, WEIGHTER));
                    interp[i][j].Zstd_tmp += interp[p][q].Zstd_tmp / (pow(distance, WEIGHTER));
                    interp[i][j].Zmin += interp[p][q].Zmin / (pow(distance, WEIGHTER));
                    interp[i][j].Zmax += interp[p][q].Zmax / (pow(distance, WEIGHTER));

                    new_sum += 1 / (pow(distance, WEIGHTER));
                  }
                }
              }
            }
            if (new_sum > 0)
            {
              interp[i][j].Zmean /= new_sum;
              interp[i][j].Zidw /= new_sum;
              interp[i][j].Zstd /= new_sum;
              interp[i][j].Zstd_tmp /= new_sum;
              interp[i][j].Zmin /= new_sum;
              interp[i][j].Zmax /= new_sum;
              interp[i][j].filled = 1;
            }
          }
        }
    }
  }
  const GridPoint& get_grid_point(int i, int j)
  {
    return interp[i][j];
  }

protected:
  double GRID_DIST_X;
  double GRID_DIST_Y;

  static const int WEIGHTER = 2;

  int GRID_SIZE_X; // total size of a grid
  int GRID_SIZE_Y; //

  // for outputting
  double min_x;
  double max_x;
  double min_y;
  double max_y;

  // for DEM filling
  int window_size;

private:
  GridPoint **interp;
  double radius_sqr;

  //////////////////////////////////////////////////////
  // Private Methods
  //////////////////////////////////////////////////////

  void update_first_quadrant(double data_z, int base_x, int base_y, double x, double y)
  {
    int i;
    int j;
    // double temp;

    // printf("radius: %f ", radius_sqrt);

    for (i = base_x; i < GRID_SIZE_X; i++)
    {
      for (j = base_y; j < GRID_SIZE_Y; j++)
      {
        /*
          temp = (   ((i - base_x)*GRID_DIST + x) * ((i - base_x)*GRID_DIST + x) +
          ((j - base_y)*GRID_DIST + y) * ((j - base_y)*GRID_DIST + y)) ;
          printf("%f ", temp);
        */

        double distance = ((i - base_x) * GRID_DIST_X + x) * ((i - base_x) * GRID_DIST_X + x) +
                          ((j - base_y) * GRID_DIST_Y + y) * ((j - base_y) * GRID_DIST_Y + y);

        if (distance <= radius_sqr)
        {
          // printf("(%d %d) ", i, j);
          // interp[i][j]++;

          // update GridPoint
          updateGridPoint(i, j, data_z, sqrt(distance));
        }
        else if (j == base_y)
        {
          // printf("return ");
          return;
        }
        else
        {
          // printf("break ");
          break;
        }
      }
    }

    // cerr << "test2" << endl;
  }

  void update_second_quadrant(double data_z, int base_x, int base_y, double x, double y)
  {
    int i;
    int j;

    for (i = base_x; i >= 0; i--)
    {
      for (j = base_y; j < GRID_SIZE_Y; j++)
      {
        double distance = ((base_x - i) * GRID_DIST_X + x) * ((base_x - i) * GRID_DIST_X + x) +
                          ((j - base_y) * GRID_DIST_Y + y) * ((j - base_y) * GRID_DIST_Y + y);

        if (distance <= radius_sqr)
        {
          // printf("(%d %d) ", i, j);
          // interp[i][j]++;

          updateGridPoint(i, j, data_z, sqrt(distance));
        }
        else if (j == base_y)
        {
          return;
        }
        else
        {
          break;
        }
      }
    }
  }

  void update_third_quadrant(double data_z, int base_x, int base_y, double x, double y)
  {
    int i;
    int j;

    for (i = base_x; i >= 0; i--)
    {
      for (j = base_y; j >= 0; j--)
      {
        double distance = ((base_x - i) * GRID_DIST_X + x) * ((base_x - i) * GRID_DIST_X + x) +
                          ((base_y - j) * GRID_DIST_Y + y) * ((base_y - j) * GRID_DIST_Y + y);

        if (distance <= radius_sqr)
        {
          // if(j == 30)
          // printf("(%d %d)\n", i, j);
          // interp[i][j]++;
          updateGridPoint(i, j, data_z, sqrt(distance));
        }
        else if (j == base_y)
        {
          return;
        }
        else
        {
          break;
        }
      }
    }
  }

  void update_fourth_quadrant(double data_z, int base_x, int base_y, double x, double y)
  {
    int i, j;

    for (i = base_x; i < GRID_SIZE_X; i++)
    {
      for (j = base_y; j >= 0; j--)
      {
        double distance = ((i - base_x) * GRID_DIST_X + x) * ((i - base_x) * GRID_DIST_X + x) +
                          ((base_y - j) * GRID_DIST_Y + y) * ((base_y - j) * GRID_DIST_Y + y);

        if (distance <= radius_sqr)
        {
          // printf("(%d %d) ", i, j);
          // interp[i][j]++;
          updateGridPoint(i, j, data_z, sqrt(distance));
        }
        else if (j == base_y)
        {
          return;
        }
        else
        {
          break;
        }
      }
    }
  }

  void updateGridPoint(int x, int y, double data_z, double distance)
  {
    // Add checks for invalid indices that result from user-defined grids
    if (x >= GRID_SIZE_X || x < 0 || y >= GRID_SIZE_Y || y < 0)
      return;

    if (interp[x][y].Zmin > data_z)
      interp[x][y].Zmin = data_z;
    if (interp[x][y].Zmax < data_z)
      interp[x][y].Zmax = data_z;

    interp[x][y].Zmean += data_z;
    interp[x][y].count++;

    // https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Online_algorithm
    double delta = data_z - interp[x][y].Zstd_tmp;
    interp[x][y].Zstd_tmp += delta / interp[x][y].count;
    interp[x][y].Zstd += delta * (data_z - interp[x][y].Zstd_tmp);

    double dist = pow(distance, WEIGHTER);

    if (interp[x][y].sum != -1)
    {
      if (dist != 0)
      {
        interp[x][y].Zidw += data_z / dist;
        interp[x][y].sum += 1 / dist;
      }
      else
      {
        interp[x][y].Zidw = data_z;
        interp[x][y].sum = -1;
      }
    }
    else
    {
      // do nothing
    }
  }
};
#endif
