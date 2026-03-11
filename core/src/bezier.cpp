#include "bezier.h"
#include <cmath>
#include <random>

Point BezierCurve::calculate(Point p0, Point p1, Point p2, Point p3, double t) {
    double u = 1 - t;
    double tt = t * t;
    double uu = u * u;
    double uuu = uu * u;
    double ttt = tt * t;

    Point p;
    p.x = uuu * p0.x + 3 * uu * t * p1.x + 3 * u * tt * p2.x + ttt * p3.x;
    p.y = uuu * p0.y + 3 * uu * t * p1.y + 3 * u * tt * p2.y + ttt * p3.y;
    return p;
}

std::vector<Point> BezierCurve::generatePath(Point start, Point end, int steps) {
    std::vector<Point> path;
    
    // Randomize control points for "Human" imperfection
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(-50.0, 50.0);

    Point p1 = { start.x + (end.x - start.x) / 3 + dis(gen), start.y + (end.y - start.y) / 3 + dis(gen) };
    Point p2 = { start.x + 2 * (end.x - start.x) / 3 + dis(gen), start.y + 2 * (end.y - start.y) / 3 + dis(gen) };

    for (int i = 0; i <= steps; ++i) {
        double t = (double)i / steps;
        path.push_back(calculate(start, p1, p2, end, t));
    }
    return path;
}
