#pragma once

struct ScreenSize {
    int width;
    int height;
};

ScreenSize GetScreenResolution();
void SleepMs(int ms);
