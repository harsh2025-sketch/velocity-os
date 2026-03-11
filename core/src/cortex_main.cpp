#include "hybrid_brain.h"
#include <iostream>

int main() {
    std::cout << R"(
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║            ⚡ VELOCITY: C++ SUPREMACY ARCHITECTURE ⚡          ║
║                                                                ║
║  "Latency is Death" → Pure C++ Brain with Embedded LLM        ║
║                                                                ║
║  Components:                                                  ║
║    🧠 Brain:  llama.cpp (In-process LLM inference)            ║
║    👂 Ears:   whisper.cpp (Real-time STT)                     ║
║    👁️  Eyes:   OpenCV + Tesseract (Real-time OCR)            ║
║    💪 Body:   liblizard.dll (Native motor control)            ║
║                                                                ║
║  Decision Pipeline:                                           ║
║    Audio Input → VAD → Transcription → Decision → Motor       ║
║                                                                ║
║  Execution:                                                   ║
║    Fast Path:  C++ Symbolic Reflex    (<  5ms)               ║
║    Slow Path:  LLM Reasoning          (2-5s, only if needed) ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    )" << std::endl;

    try {
        Velocity::HybridBrain velocity;
        velocity.Init();
        velocity.RunLoop();
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}

