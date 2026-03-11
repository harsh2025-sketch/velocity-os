/**
 * VELOCITY A-OS: HIGH-FREQUENCY AUDITORY CORTEX
 * Optimization: Lock-free atomic signaling.
 * Latency: ~10ms reaction time.
 */

#include <iostream>
#include <cmath>
#include <atomic>

#define MINIAUDIO_IMPLEMENTATION
#include "../include/miniaudio.h"

class Cochlea {
private:
    ma_device_config deviceConfig;
    ma_device device;
    std::atomic<bool> is_listening{false};
    std::atomic<float> current_energy{0.0f};
    static constexpr float VOICE_THRESHOLD = 0.05f;

    static void data_callback(ma_device* pDevice, void*, const void* pInput, ma_uint32 frameCount) {
        const float* samples = (const float*)pInput;
        if (!samples) return;

        Cochlea* self = (Cochlea*)pDevice->pUserData;
        float sum = 0.0f;
        for (ma_uint32 i = 0; i < frameCount; i++) sum += samples[i] * samples[i];
        self->current_energy.store(std::sqrt(sum / frameCount), std::memory_order_relaxed);
    }

public:
    Cochlea() {
        deviceConfig = ma_device_config_init(ma_device_type_capture);
        deviceConfig.capture.format = ma_format_f32;
        deviceConfig.capture.channels = 1;
        deviceConfig.sampleRate = 16000;
        deviceConfig.dataCallback = data_callback;
        deviceConfig.pUserData = this;

        if (ma_device_init(NULL, &deviceConfig, &device) != MA_SUCCESS) {
            std::cerr << "[COCHLEA] Failed to init mic\n";
            return;
        }
        if (ma_device_start(&device) != MA_SUCCESS) {
            std::cerr << "[COCHLEA] Failed to start stream\n";
            return;
        }
        is_listening.store(true);
    }

    ~Cochlea() { ma_device_uninit(&device); }

    bool detected_voice() { return current_energy.load(std::memory_order_relaxed) > VOICE_THRESHOLD; }
    float get_energy_level() { return current_energy.load(std::memory_order_relaxed); }
};
