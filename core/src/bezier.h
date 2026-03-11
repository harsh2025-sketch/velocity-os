#pragma once
#include <vector>

struct Point {
    double x, y;
};

class BezierCurve {
public:
    // Generates a path from start to end with control points for curvature
    static std::vector<Point> generatePath(Point start, Point end, int steps);
    
    // Calculates a point at time t (0.0 to 1.0)
    static Point calculate(Point p0, Point p1, Point p2, Point p3, double t);
};
