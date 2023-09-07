
#ifndef GRIDDATA_ENUM
#define GRIDDATA_ENUM

enum GridData {
  IDW = 1 <<0,
  MIN = 1 <<1,
  MAX = 1 << 2,
  MEAN = 1 << 3,
  STD = 1 << 4,
};

#endif