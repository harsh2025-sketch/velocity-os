/**
 * VELOCITY A-OS: AMYGDALA BRIDGE
 * FFI Contract: Links C++ Motor Cortex to Rust Safety Core.
 */
#pragma once

extern "C" {
    int check_command_safety(const char* cmd);
    int check_motor_safety(int dx, int dy);
}

class Amygdala {
public:
    bool is_safe_text(const char* text) { return check_command_safety(text) == 1; }
    bool is_safe_move(int dx, int dy) { return check_motor_safety(dx, dy) == 1; }
};
