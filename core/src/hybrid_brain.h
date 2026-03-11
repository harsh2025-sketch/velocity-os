#pragma once

#include <iostream>
#include <thread>
#include <atomic>
#include <queue>
#include <string>
#include <memory>
#include <map>
#include "vision_engine.h"
// Real in-process model headers
#include "whisper.h"
#include "llama.h"

// Motor control interface (from lizard motor)
namespace Lizard {
    void InitMouse();
    void MoveMouse(int x, int y);
    void ClickMouse(int button = 0);
}

// Simple JSON-like object for serialization (no external dependency)
struct JsonValue {
    std::map<std::string, std::string> data;
    std::string dump() const {
        std::string result = "{";
        bool first = true;
        for (const auto& [key, value] : data) {
            if (!first) result += ",";
            result += "\"" + key + "\":\"" + value + "\"";
            first = false;
        }
        result += "}";
        return result;
    }
};
using json = JsonValue;

// ============================================================================
// HybridBrain: The C++ Cortex
// 
// Replaces Python brain/main.py with native performance.
// Handles: VAD -> Transcription -> Decision -> Execution (all in-process)
// ============================================================================

namespace Velocity {

// Symbolic Reflex Patterns (Pre-computed in C++)
struct ReflexRule {
    std::string pattern;
    std::string action;
    std::string target;
    float confidence;
};

// Command Execution Interface
struct Command {
    std::string action;     // "open", "type", "click", "search"
    std::string target;     // "notepad", "hello", "x:100,y:200", "google python"
    bool urgent = false;    // Interrupt flag
    std::string source;     // "reflex" or "llm"
};

// Audio Frame (16-bit PCM)
struct AudioFrame {
    int sample_rate;
    std::vector<int16_t> samples;
    int64_t timestamp_us;
};

// ============================================================================
// HybridBrain Class
// ============================================================================

class HybridBrain {
public:
    HybridBrain();
    ~HybridBrain();

    // ---- LIFECYCLE ----
    void Init();                       // Load models, init hardware
    void RunLoop();                    // Main event loop
    void Shutdown();                   // Graceful cleanup
    void Stop();                       // Atomic stop signal

    // ---- AUDIO PIPELINE ----
    bool CheckVAD(const AudioFrame& frame);           // Voice Activity Detect
    std::string TranscribeAudio(const AudioFrame& frame);  // STT via whisper.cpp

    // ---- DECISION LOGIC ----
    Command DecideAction(const std::string& user_input);  // Symbolic + Neural
    Command CheckSymbolicReflex(const std::string& input);  // Fast path
    Command InvokeLLM(const std::string& input);           // Neural fallback

    // ---- EXECUTION ----
    void ExecuteCommand(const Command& cmd);          // Motor control bridge
    void ExecuteReflex(const Command& cmd);           // Direct Win32
    void ExecuteLLMCommand(const Command& cmd);       // Parse JSON + execute

    // ---- VISION ----
    std::string ReadScreen();                         // OCR capture
    bool FindAndClick(const std::string& target);     // Vision-guided clicking

    // ---- INTROSPECTION ----
    json GetStatus();                  // Current brain state
    void LogMetrics(const std::string& stage, float latency_ms);

private:
    // ---- STATE ----
    std::atomic<bool> running{false};
    std::atomic<bool> vad_active{false};
    
    // ---- MODELS (In-Process) ----
    llama_model* llama_model_ = nullptr;   // llama.cpp model
    llama_context* llm_context = nullptr;  // llama.cpp context
    struct whisper_context* whisper_context = nullptr; // whisper.cpp context
    
    // ---- VISION ----
    std::unique_ptr<VisionEngine> vision;  // OpenCV + Tesseract
    
    // ---- AUDIO ----
    std::thread audio_thread;
    std::queue<AudioFrame> audio_buffer;
    void AudioWorker();                    // Background audio capture
    AudioFrame GetAudioFrame();
    
    // ---- REFLEX DATABASE ----
    std::vector<ReflexRule> reflexes;
    void InitializeReflexes();             // Pre-compile symbolic patterns
    
    // ---- METRICS ----
    struct Latencies {
        float vad_ms = 0;
        float transcribe_ms = 0;
        float decide_ms = 0;
        float execute_ms = 0;
        float total_ms = 0;
    } metrics;

    // ---- HELPERS ----
    json ParseLLMOutput(const std::string& raw_output);
    bool IsValidCommand(const Command& cmd);
    void SetupSignalHandlers();
};

} // namespace Velocity

