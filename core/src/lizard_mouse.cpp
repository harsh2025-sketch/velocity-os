#include "lizard_mouse.h"
#include "bezier.h"
#include "platform_utils.h"

#ifdef _WIN32
    #include <windows.h>
#elif __linux__
    #include <linux/uinput.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <cstring>
    #include <sys/ioctl.h>
#endif

static int mouse_fd = -1;
static bool mouse_initialized = false;

void InitMouse() {
    if (mouse_initialized) return;
    mouse_initialized = true;
#ifdef __linux__
    mouse_fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    if (mouse_fd < 0) return;
    
    ioctl(mouse_fd, UI_SET_EVBIT, EV_KEY);
    ioctl(mouse_fd, UI_SET_KEYBIT, BTN_LEFT);
    ioctl(mouse_fd, UI_SET_KEYBIT, BTN_RIGHT);
    ioctl(mouse_fd, UI_SET_EVBIT, EV_REL);
    ioctl(mouse_fd, UI_SET_RELBIT, REL_X);
    ioctl(mouse_fd, UI_SET_RELBIT, REL_Y);
    ioctl(mouse_fd, UI_SET_RELBIT, REL_WHEEL);
    
    struct uinput_setup usetup{};
    strcpy(usetup.name, "VelocityMouse");
    usetup.id.bustype = BUS_USB;
    ioctl(mouse_fd, UI_DEV_SETUP, &usetup);
    ioctl(mouse_fd, UI_DEV_CREATE);
#endif
}

void MoveMouse(int x, int y) {
#ifdef _WIN32
    POINT cur;
    GetCursorPos(&cur);
    
    // Fast path: small moves don't need Bezier smoothing
    int dx = x - cur.x;
    int dy = y - cur.y;
    if (dx * dx + dy * dy < 10000) {  // < 100px distance
        SetCursorPos(x, y);
        return;
    }
    
    Point start{(double)cur.x, (double)cur.y};
    Point end{(double)x, (double)y};
    
    auto path = BezierCurve::generatePath(start, end, 50);
    for (const auto& p : path) {
        SetCursorPos((int)p.x, (int)p.y);
        SleepMs(2);
    }
#elif __linux__
    struct input_event ev{};
    ev.type = EV_REL;
    ev.code = REL_X;
    ev.value = x;
    write(mouse_fd, &ev, sizeof(ev));
    ev.code = REL_Y;
    ev.value = y;
    write(mouse_fd, &ev, sizeof(ev));
    
    ev.type = EV_SYN;
    ev.code = SYN_REPORT;
    ev.value = 0;
    write(mouse_fd, &ev, sizeof(ev));
#endif
}

void ClickMouse(int button) {
#ifdef _WIN32
    INPUT input{};
    input.type = INPUT_MOUSE;
    input.mi.dwFlags = (button == 0) ? MOUSEEVENTF_LEFTDOWN : MOUSEEVENTF_RIGHTDOWN;
    SendInput(1, &input, sizeof(INPUT));
    SleepMs(50);
    input.mi.dwFlags = (button == 0) ? MOUSEEVENTF_LEFTUP : MOUSEEVENTF_RIGHTUP;
    SendInput(1, &input, sizeof(INPUT));
#elif __linux__
    struct input_event ev{};
    ev.type = EV_KEY;
    ev.code = (button == 0) ? BTN_LEFT : BTN_RIGHT;
    ev.value = 1;
    write(mouse_fd, &ev, sizeof(ev));
    
    ev.type = EV_SYN;
    ev.code = SYN_REPORT;
    ev.value = 0;
    write(mouse_fd, &ev, sizeof(ev));
    
    SleepMs(50);
    
    ev.type = EV_KEY;
    ev.code = (button == 0) ? BTN_LEFT : BTN_RIGHT;
    ev.value = 0;
    write(mouse_fd, &ev, sizeof(ev));
    
    ev.type = EV_SYN;
    ev.code = SYN_REPORT;
    ev.value = 0;
    write(mouse_fd, &ev, sizeof(ev));
#endif
}

void ScrollMouse(int amount) {
#ifdef _WIN32
    INPUT input{};
    input.type = INPUT_MOUSE;
    input.mi.dwFlags = MOUSEEVENTF_WHEEL;
    input.mi.mouseData = amount * 120;
    SendInput(1, &input, sizeof(INPUT));
#elif __linux__
    struct input_event ev{};
    ev.type = EV_REL;
    ev.code = REL_WHEEL;
    ev.value = amount;
    write(mouse_fd, &ev, sizeof(ev));
    
    ev.type = EV_SYN;
    ev.code = SYN_REPORT;
    ev.value = 0;
    write(mouse_fd, &ev, sizeof(ev));
#endif
}
