#include "platform_utils.h"
#ifdef _WIN32
#include <Windows.h>
#include <thread>
#include <chrono>
#else
#include <X11/Xlib.h>
#include <unistd.h>
#endif

ScreenSize GetScreenResolution() {
#ifdef _WIN32
    return {GetSystemMetrics(SM_CXSCREEN), GetSystemMetrics(SM_CYSCREEN)};
#else
    Display* d = XOpenDisplay(nullptr);
    Screen* s = DefaultScreenOfDisplay(d);
    ScreenSize size = {s->width, s->height};
    XCloseDisplay(d);
    return size;
#endif
}

void SleepMs(int ms) {
#ifdef _WIN32
    Sleep(ms);
#else
    usleep(ms * 1000);
#endif
}
