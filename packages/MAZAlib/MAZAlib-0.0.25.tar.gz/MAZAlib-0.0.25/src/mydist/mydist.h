#pragma once

class MyDist {
public:
  MyDist(double shift);

  double dist(double x, double y) const;

private:
  double shift_;
};