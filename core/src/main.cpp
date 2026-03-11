#include <iostream>
#include <string>
#include <vector>
#include <sstream>

#include "lizard_mouse.h"
#include "lizard_keyboard.h"
#include "platform_utils.h"

std::vector<std::string> split_cmd(const std::string& str) {
    std::vector<std::string> tokens;
    std::stringstream ss(str);
    std::string token;
    while (ss >> token) tokens.push_back(token);
    return tokens;
}

int main() {
    std::cout << "[CORE] Waking up..." << std::endl;

    InitMouse();
    InitKeyboard();

    std::cout << "VELOCITY_LIZARD_READY" << std::endl;
    std::cout.flush();

    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;

        auto args = split_cmd(line);
        if (args.empty()) continue;
        const std::string& cmd = args[0];

        if (cmd == "MOVE" && args.size() >= 3) {
            int x = std::stoi(args[1]), y = std::stoi(args[2]);
            MoveMouse(x, y);
            std::cout << "OK" << std::endl;
        }
        else if (cmd == "CLICK") {
            int btn = (args.size() >= 2 && args[1] == "RIGHT") ? 1 : 0;
            ClickMouse(btn);
            std::cout << "OK" << std::endl;
        }
        else if (cmd == "SCROLL" && args.size() >= 2) {
            ScrollMouse(std::stoi(args[1]));
            std::cout << "OK" << std::endl;
        }
        else if (cmd == "TYPE" && line.size() > 5) {
            std::string text = line.substr(5);
            TypeString(text);
            std::cout << "OK" << std::endl;
        }
        else if (cmd == "PRESS" && args.size() >= 2) {
            PressKey(std::stoi(args[1]));
            std::cout << "OK" << std::endl;
        }
        else if (cmd == "RESOLUTION") {
            ScreenSize s = GetScreenResolution();
            std::cout << "RESOLUTION:" << s.width << "x" << s.height << std::endl;
        }
        else if (cmd == "STATUS") {
            std::cout << "STATUS:ONLINE" << std::endl;
        }
        else if (cmd == "EXIT") {
            break;
        }
        else {
            std::cout << "UNKNOWN_COMMAND" << std::endl;
        }
        std::cout.flush();
    }

    std::cout << "[CORE] Shutting down." << std::endl;
    return 0;
}
