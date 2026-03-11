/**
 * VELOCITY A-OS: VISUAL REFLEX (Optic Nerve)
 * Optimization: Single-pixel sampling, <1ms latency.
 */

#include <iostream>
#include <cmath>

#ifdef _WIN32
    #include <windows.h>
#elif __linux__
    #include <X11/Xlib.h>
    #include <X11/Xutil.h>
#endif

struct RGB {
    unsigned char r, g, b;
    bool matches(const RGB& o, int tol = 10) const {
        return std::abs(r - o.r) <= tol &&
               std::abs(g - o.g) <= tol &&
               std::abs(b - o.b) <= tol;
    }
};

class VisualReflex {
private:
    #ifdef __linux__
        Display* display = nullptr;
    #endif

public:
    VisualReflex() {
        #ifdef __linux__
            display = XOpenDisplay(NULL);
            if (!display) std::cerr << "[VISION] X Display failed\n";
        #endif
    }

    ~VisualReflex() {
        #ifdef __linux__
            if (display) XCloseDisplay(display);
        #endif
    }

    RGB get_pixel_at(int x, int y) {
        RGB c{0, 0, 0};
        #ifdef _WIN32
            HDC hDC = GetDC(NULL);
            if (hDC) {
                COLORREF p = GetPixel(hDC, x, y);
                c.r = GetRValue(p); c.g = GetGValue(p); c.b = GetBValue(p);
                ReleaseDC(NULL, hDC);
            }
        #elif __linux__
            if (display) {
                XImage* img = XGetImage(display, DefaultRootWindow(display), x, y, 1, 1, AllPlanes, ZPixmap);
                if (img) {
                    unsigned long px = XGetPixel(img, 0, 0);
                    c.r = (px >> 16) & 0xFF; c.g = (px >> 8) & 0xFF; c.b = px & 0xFF;
                    XDestroyImage(img);
                }
            }
        #endif
        return c;
    }

    bool verify_safe(int x, int y, const RGB& expected, int tol = 10) {
        return get_pixel_at(x, y).matches(expected, tol);
    }
};
