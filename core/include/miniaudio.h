/**
 * MINIAUDIO - Single-file audio library
 * Download from: https://raw.githubusercontent.com/mackron/miniaudio/master/miniaudio.h
 * Replace this placeholder with the full miniaudio.h
 */
#ifndef MINIAUDIO_H
#define MINIAUDIO_H

typedef int ma_result;
#define MA_SUCCESS 0

typedef enum { ma_device_type_playback = 1, ma_device_type_capture = 2 } ma_device_type;
typedef enum { ma_format_f32 = 5 } ma_format;

typedef void (* ma_device_data_proc)(struct ma_device* pDevice, void* pOutput, const void* pInput, unsigned int frameCount);

typedef struct {
    ma_device_type deviceType;
    struct { ma_format format; unsigned int channels; } capture;
    unsigned int sampleRate;
    ma_device_data_proc dataCallback;
    void* pUserData;
} ma_device_config;

typedef struct ma_device {
    void* pUserData;
    int _internal;
} ma_device;

inline ma_device_config ma_device_config_init(ma_device_type type) {
    ma_device_config c{}; c.deviceType = type; return c;
}
inline ma_result ma_device_init(void*, const ma_device_config* cfg, ma_device* dev) {
    dev->pUserData = cfg->pUserData; return MA_SUCCESS;
}
inline ma_result ma_device_start(ma_device*) { return MA_SUCCESS; }
inline void ma_device_uninit(ma_device*) {}

#endif // MINIAUDIO_H
