#include "lizard_mouse.h"
#include "lizard_keyboard.h"

extern "C" {
    
#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT __attribute__((visibility("default")))
#endif
    
    EXPORT void Core_MoveMouse(int x, int y) {
        MoveMouse(x, y);
    }

    EXPORT void Core_ClickMouse(int button) {
        ClickMouse(button);
    }

    EXPORT void Core_ScrollMouse(int amount) {
        ScrollMouse(amount);
    }

    EXPORT void Core_TypeString(const char* text) {
        TypeString(std::string(text));
    }

    EXPORT void Core_PressKey(int key_code) {
        PressKey(key_code);
    }

    EXPORT void Core_ReleaseKey(int key_code) {
        ReleaseKey(key_code);
    }

    EXPORT void Core_InitMouse() {
        InitMouse();
    }

    EXPORT void Core_InitKeyboard() {
        InitKeyboard();
    }
}
