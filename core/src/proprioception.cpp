/**
 * VELOCITY A-OS: PROPRIOCEPTION (Body Awareness)
 * Role: State Estimation (Position, Screen Resolution).
 * Optimization: Cached resolution to avoid slow syscalls.
 */

#include <iostream>

#ifdef _WIN32
    #include <windows.h>
#elif __linux__
    #include <X11/Xlib.h>
#endif

struct BodyState {
    int mouse_x, mouse_y, screen_w, screen_h;
};

class Proprioception {
private:
    int cached_width = 1920, cached_height = 1080;
    #ifdef __linux__
        Display* display = nullptr;
    #endif

public:
    Proprioception() {
        #ifdef _WIN32
            cached_width = GetSystemMetrics(SM_CXSCREEN);
            cached_height = GetSystemMetrics(SM_CYSCREEN);
        #elif __linux__
            display = XOpenDisplay(NULL);
            if (display) {
                Screen* scr = DefaultScreenOfDisplay(display);
                cached_width = scr->width;
                cached_height = scr->height;
            }
        #endif
        std::cout << "[BODY] Sensors calibrated. Screen: " << cached_width << "x" << cached_height << "\n";
    }

    ~Proprioception() {
        #ifdef __linux__
            if (display) XCloseDisplay(display);
        #endif
    }

    BodyState get_state() {
        BodyState s{0, 0, cached_width, cached_height};
        #ifdef _WIN32
            POINT p;
            if (GetCursorPos(&p)) { s.mouse_x = p.x; s.mouse_y = p.y; }
        #elif __linux__
            if (display) {
                Window root = DefaultRootWindow(display);
                Window ret_root, ret_child;
                int root_x, root_y, win_x, win_y;
                unsigned int mask;
                if (XQueryPointer(display, root, &ret_root, &ret_child, 
                                  &root_x, &root_y, &win_x, &win_y, &mask)) {
                    s.mouse_x = root_x;
                    s.mouse_y = root_y;
                }
            }
        #endif
        return s;
    }

    void report() {
        auto s = get_state();
        std::cout << "STATUS_REPORT::MOUSE_AT::" << s.mouse_x << "," << s.mouse_y 
                  << "::SCREEN_SIZE::" << s.screen_w << "x" << s.screen_h << "\n";
    }
};
