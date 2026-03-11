#include "lizard_keyboard.h"
#include "platform_utils.h"
#include <map>

#ifdef _WIN32
    #include <windows.h>
#elif __linux__
    #include <linux/uinput.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <cstring>
#endif

static int kb_fd = -1;

void InitKeyboard() {
#ifdef __linux__
    kb_fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    if (kb_fd < 0) return;
    
    ioctl(kb_fd, UI_SET_EVBIT, EV_KEY);
    for (int i = 0; i < KEY_MAX; i++) {
        ioctl(kb_fd, UI_SET_KEYBIT, i);
    }
    
    struct uinput_setup usetup{};
    strcpy(usetup.name, "VelocityKeyboard");
    usetup.id.bustype = BUS_USB;
    ioctl(kb_fd, UI_DEV_SETUP, &usetup);
    ioctl(kb_fd, UI_DEV_CREATE);
#endif
}

void TypeString(const std::string& text) {
    for (char c : text) {
#ifdef _WIN32
        SHORT vk = VkKeyScan(c);
        BYTE key = LOBYTE(vk);
        bool shift = (HIBYTE(vk) & 1) != 0;
        
        INPUT inputs[4] = {};
        int count = 0;
        
        if (shift) {
            inputs[count].type = INPUT_KEYBOARD;
            inputs[count].ki.wVk = VK_SHIFT;
            count++;
        }
        
        inputs[count].type = INPUT_KEYBOARD;
        inputs[count].ki.wVk = key;
        count++;
        
        inputs[count].type = INPUT_KEYBOARD;
        inputs[count].ki.wVk = key;
        inputs[count].ki.dwFlags = KEYEVENTF_KEYUP;
        count++;
        
        if (shift) {
            inputs[count].type = INPUT_KEYBOARD;
            inputs[count].ki.wVk = VK_SHIFT;
            inputs[count].ki.dwFlags = KEYEVENTF_KEYUP;
            count++;
        }
        
        SendInput(count, inputs, sizeof(INPUT));
        SleepMs(10);
#endif
    }
}

void PressKey(int keyCode) {
#ifdef _WIN32
    INPUT input{};
    input.type = INPUT_KEYBOARD;
    input.ki.wVk = keyCode;
    SendInput(1, &input, sizeof(INPUT));
    SleepMs(50);
    input.ki.dwFlags = KEYEVENTF_KEYUP;
    SendInput(1, &input, sizeof(INPUT));
#elif __linux__
    struct input_event ev{};
    ev.type = EV_KEY;
    ev.code = keyCode;
    ev.value = 1;
    write(kb_fd, &ev, sizeof(ev));
    SleepMs(50);
    ev.value = 0;
    write(kb_fd, &ev, sizeof(ev));
#endif
}

void ReleaseKey(int keyCode) {
#ifdef _WIN32
    INPUT input{};
    input.type = INPUT_KEYBOARD;
    input.ki.wVk = keyCode;
    input.ki.dwFlags = KEYEVENTF_KEYUP;
    SendInput(1, &input, sizeof(INPUT));
#elif __linux__
    struct input_event ev{};
    ev.type = EV_KEY;
    ev.code = keyCode;
    ev.value = 0;
    write(kb_fd, &ev, sizeof(ev));
#endif
}
