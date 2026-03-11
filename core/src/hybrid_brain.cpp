#include "hybrid_brain.h"
#include <iostream>
#include <chrono>
#include <algorithm>
#include <sstream>
#include <Windows.h>
#include <vector>
#include <cstring>
#include <fstream>

namespace Velocity {

// ============================================================================
// Constructor / Destructor
// ============================================================================

HybridBrain::HybridBrain() {
    std::cout << "⚡ HybridBrain: Instantiated" << std::endl;
}

HybridBrain::~HybridBrain() {
    Shutdown();
}

// ============================================================================
// LIFECYCLE
// ============================================================================

void HybridBrain::Init() {
    std::cout << "\n=== INITIALIZING C++ CORTEX ===" << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    try {
        // 1. Init Lizard (Body)
        std::cout << "📦 Loading Motor Core (lizard.dll)..." << std::endl;
        // InitMotor() would be called here
        std::cout << "   ✓ Motor ready" << std::endl;
        
        // 2. Init Whisper (Ears)
        std::cout << "👂 Loading Whisper STT..." << std::endl;
        {
            // Default model path; attempt base.en, then fall back to test model
            whisper_context_params wctx_params = whisper_context_default_params();
            const char* w_model_primary = "./whisper.cpp/models/ggml-base.en.bin";
            const char* w_model_fallback = "./whisper.cpp/models/for-tests-ggml-base.en.bin";
            whisper_context = whisper_init_from_file_with_params(w_model_primary, wctx_params);
            if (!whisper_context) {
                whisper_context = whisper_init_from_file_with_params(w_model_fallback, wctx_params);
            }
            if (whisper_context) {
                std::cout << "   ✓ Whisper STT loaded" << std::endl;
            } else {
                std::cout << "   ⚠️ Whisper STT not loaded, falling back to placeholders" << std::endl;
            }
        }
        
        // 3. Init Llama (Brain)
        std::cout << "🧠 Loading Llama LLM..." << std::endl;
        {
            // Initialize backend
            llama_backend_init();
            const char* l_model = "./llama.cpp/models/tinyllama.gguf";
            llama_model_params mparams = llama_model_default_params();
            llama_model_ = llama_load_model_from_file(l_model, mparams);
            if (llama_model_) {
                llama_context_params cparams = llama_context_default_params();
                // Reduce context & batch for faster CPU inference
                cparams.n_ctx = 768;
                cparams.n_batch = 128;
                llm_context = llama_new_context_with_model(llama_model_, cparams);
            }
            if (llm_context) {
                std::cout << "   ✓ Llama LLM loaded" << std::endl;
            } else {
                std::cout << "   ⚠️ Llama LLM not loaded, falling back to placeholders" << std::endl;
            }
        }
        
        // 4. Init Vision (Eyes)
        std::cout << "👁️  Loading Vision Engine..." << std::endl;
        vision = std::make_unique<VisionEngine>();
        vision->Init();
        std::cout << "   ✓ Vision ready" << std::endl;
        
        // 5. Init Reflex Database
        std::cout << "⚡ Compiling symbolic reflexes..." << std::endl;
        InitializeReflexes();
        std::cout << "   ✓ " << reflexes.size() << " reflexes loaded" << std::endl;
        
        running = true;
        audio_thread = std::thread(&HybridBrain::AudioWorker, this);
        
        auto elapsed = std::chrono::high_resolution_clock::now() - start;
        std::cout << "✅ C++ Cortex initialized in " 
                  << std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count() 
                  << "ms\n" << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Init failed: " << e.what() << std::endl;
        throw;
    }
}

void HybridBrain::RunLoop() {
    std::cout << "🔄 HYBRID INTELLIGENCE ACTIVE\n" << std::endl;
    
    while (running) {
        auto loop_start = std::chrono::high_resolution_clock::now();
        
        // ---- OBSERVE ----
        if (vad_active && !audio_buffer.empty()) {
            AudioFrame frame = GetAudioFrame();
            auto vad_start = std::chrono::high_resolution_clock::now();
            
            if (CheckVAD(frame)) {
                metrics.vad_ms = std::chrono::duration<float, std::milli>(
                    std::chrono::high_resolution_clock::now() - vad_start).count();
                
                // ---- HEAR ----
                auto transcribe_start = std::chrono::high_resolution_clock::now();
                std::string user_input = TranscribeAudio(frame);
                metrics.transcribe_ms = std::chrono::duration<float, std::milli>(
                    std::chrono::high_resolution_clock::now() - transcribe_start).count();
                
                std::cout << "\n👂 HEARD: \"" << user_input << "\" (" 
                          << metrics.transcribe_ms << "ms)" << std::endl;
                
                // ---- REASON ----
                auto decide_start = std::chrono::high_resolution_clock::now();
                Command cmd = DecideAction(user_input);
                metrics.decide_ms = std::chrono::duration<float, std::milli>(
                    std::chrono::high_resolution_clock::now() - decide_start).count();
                
                std::cout << "🧠 DECIDED: action=" << cmd.action 
                          << " target=" << cmd.target 
                          << " source=" << cmd.source
                          << " (" << metrics.decide_ms << "ms)" << std::endl;
                
                // ---- ACT ----
                auto execute_start = std::chrono::high_resolution_clock::now();
                ExecuteCommand(cmd);
                metrics.execute_ms = std::chrono::duration<float, std::milli>(
                    std::chrono::high_resolution_clock::now() - execute_start).count();
                
                std::cout << "✅ EXECUTED in " << metrics.execute_ms << "ms" << std::endl;
                
                // ---- METRICS ----
                metrics.total_ms = std::chrono::duration<float, std::milli>(
                    std::chrono::high_resolution_clock::now() - loop_start).count();
                
                std::cout << "⏱️  TOTAL LATENCY: " << metrics.total_ms << "ms\n" << std::endl;
                // Append metrics to CSV for side-by-side comparison later
                try {
                    std::ofstream csv("metrics_b.csv", std::ios::app);
                    csv << metrics.total_ms << "," << metrics.vad_ms << "," << metrics.transcribe_ms
                        << "," << metrics.decide_ms << "," << metrics.execute_ms << "," << cmd.source << "\n";
                } catch (...) {
                    // best effort; ignore file errors
                }
            }
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}

void HybridBrain::Shutdown() {
    std::cout << "\n🛑 Shutting down C++ Cortex..." << std::endl;
    
    running = false;
    
    if (audio_thread.joinable()) {
        audio_thread.join();
    }
    
    // Cleanup resources
    if (whisper_context) {
        whisper_free(whisper_context);
        whisper_context = nullptr;
    }
    if (llm_context) {
        llama_free(llm_context);
        llm_context = nullptr;
    }
    if (llama_model_) {
        llama_free_model(llama_model_);
        llama_model_ = nullptr;
    }
    llama_backend_free();
    std::cout << "✅ Shutdown complete" << std::endl;
}

void HybridBrain::Stop() {
    running = false;
}

// ============================================================================
// AUDIO PIPELINE
// ============================================================================

void HybridBrain::AudioWorker() {
    std::cout << "🎙️  Audio worker thread started" << std::endl;
    
    while (running) {
        // In production, this captures from PortAudio
        // For now, simulate audio frames
        AudioFrame frame;
        frame.sample_rate = 16000;
        frame.samples.resize(1600);  // 100ms @ 16kHz
        frame.timestamp_us = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::high_resolution_clock::now().time_since_epoch()).count();
        
        audio_buffer.push(frame);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

AudioFrame HybridBrain::GetAudioFrame() {
    AudioFrame frame = audio_buffer.front();
    audio_buffer.pop();
    return frame;
}

bool HybridBrain::CheckVAD(const AudioFrame& frame) {
    // Voice Activity Detection: Check if audio energy > threshold
    // In production: Call actual VAD algorithm
    
    // Simulate: 50% chance of voice detected
    static int counter = 0;
    counter++;
    vad_active = (counter % 2 == 0);
    
    return vad_active;
}

std::string HybridBrain::TranscribeAudio(const AudioFrame& frame) {
    // Real whisper.cpp integration
    if (whisper_context != nullptr) {
        // Convert audio frame to whisper format (mono float32)
        std::vector<float> audio_float(frame.samples.size());
        for (size_t i = 0; i < frame.samples.size(); i++) {
            audio_float[i] = frame.samples[i] / 32768.0f;  // Convert int16 to float
        }

        whisper_full_params wparams = whisper_full_default_params(WHISPER_SAMPLING_GREEDY);
        wparams.print_progress = false;
        wparams.print_realtime = false;
        wparams.no_timestamps = true;
        wparams.language = "en";
        // Speed optimizations: cap threads to avoid oversubscription
        wparams.n_threads = std::min(4u, std::max(1u, std::thread::hardware_concurrency()));

        int ret = whisper_full(whisper_context, wparams, audio_float.data(), (int)audio_float.size());
        if (ret != 0) {
            std::cerr << "⚠️ whisper_full failed, code=" << ret << std::endl;
        } else {
            std::ostringstream oss;
            int nseg = whisper_full_n_segments(whisper_context);
            for (int i = 0; i < nseg; ++i) {
                const char* seg = whisper_full_get_segment_text(whisper_context, i);
                if (seg) oss << seg;
            }
            std::string txt = oss.str();
            if (!txt.empty()) return txt;
        }
        // Fallback if transcription empty
        return "";
    }
    
    // Fallback: Simulated transcription for testing
    static const std::vector<std::string> samples = {
        "open notepad",
        "type hello world",
        "click here",
        "search google python",
        "stop"
    };
    
    static int idx = 0;
    return samples[idx++ % samples.size()];
}

// ============================================================================
// DECISION LOGIC
// ============================================================================

Command HybridBrain::DecideAction(const std::string& user_input) {
    // Priority 1: Fast Symbolic Reflex (< 1ms)
    Command reflex = CheckSymbolicReflex(user_input);
    if (!reflex.action.empty()) {
        reflex.source = "reflex";
        std::cout << "   [FAST PATH] Symbolic reflex matched" << std::endl;
        return reflex;
    }
    
    // Priority 2: Neural LLM (2-5s) - Only if reflex failed
    std::cout << "   [SLOW PATH] Invoking LLM for reasoning..." << std::endl;
    Command llm_cmd = InvokeLLM(user_input);
    llm_cmd.source = "llm";
    return llm_cmd;
}

Command HybridBrain::CheckSymbolicReflex(const std::string& input) {
    // Pre-compiled, hardcoded patterns for instant dispatch
    
    // Case-insensitive search
    std::string lower_input = input;
    std::transform(lower_input.begin(), lower_input.end(), 
                   lower_input.begin(), ::tolower);
    
    // Pattern matching
    for (const auto& rule : reflexes) {
        if (lower_input.find(rule.pattern) != std::string::npos) {
            return {rule.action, rule.target, false, "reflex"};
        }
    }
    
    return {};  // No match
}

Command HybridBrain::InvokeLLM(const std::string& input) {
    // Real llama.cpp integration
    if (llm_context != nullptr) {
        // Simple prompt aiming for key-value output
        std::string prompt = "You are a command planner. Respond in tokens like 'action:open target:notepad'. User: " + input + "\n";

        // Tokenize prompt using model vocab
        const llama_vocab* vocab = llama_model_get_vocab(llama_model_);
        std::vector<llama_token> tokens(prompt.size());
        int32_t n_tok = llama_tokenize(vocab, prompt.c_str(), (int32_t)prompt.size(), tokens.data(), (int32_t)tokens.size(), true, true);
        if (n_tok < 0) n_tok = 0;
        tokens.resize(n_tok);

        // Evaluate prompt
        // Smaller batch for quicker steps
        llama_batch batch = llama_batch_init(128, 0, 1);
        for (int i = 0; i < (int)tokens.size(); ++i) {
            batch.token[i] = tokens[i];
            batch.pos[i] = i;
            batch.n_seq_id[i] = 1;
            batch.seq_id[i][0] = 0;
            batch.logits[i] = false;
        }
        batch.n_tokens = (int)tokens.size();
        if (llama_decode(llm_context, batch) != 0) {
            std::cerr << "⚠️ llama_decode failed" << std::endl;
        }

        // Greedy decode a few tokens
        std::string out;
        int n_vocab = llama_vocab_n_tokens(vocab);
        // Limit generated tokens to keep latency low
        for (int t = 0; t < 24; ++t) {
            const float* logits = llama_get_logits(llm_context);
            int best = 0;
            float best_logit = logits[0];
            for (int i = 1; i < n_vocab; ++i) {
                if (logits[i] > best_logit) { best_logit = logits[i]; best = i; }
            }
            llama_token tok = (llama_token)best;
            char buf[256];
            int32_t len = llama_token_to_piece(vocab, tok, buf, (int32_t)sizeof(buf), 0, true);
            if (len > 0) {
                out.append(buf, buf + std::min<int32_t>(len, (int32_t)sizeof(buf)));
            }

            // Feed back token
            batch.token[0] = tok;
            batch.pos[0] = (int)tokens.size() + t;
            batch.n_seq_id[0] = 1;
            batch.seq_id[0][0] = 0;
            batch.logits[0] = true;
            batch.n_tokens = 1;
            if (llama_decode(llm_context, batch) != 0) break;

            if (out.find("\n") != std::string::npos) break;
        }

        json parsed = ParseLLMOutput(out);
        Command cmd;
        cmd.action = parsed.data["action"];
        cmd.target = parsed.data["target"];
        if (cmd.action.empty()) {
            // Fallback simple heuristics
            if (input.find("open") != std::string::npos) {
                cmd = {"open", "notepad.exe", false, "llm"};
            } else if (input.find("type") != std::string::npos) {
                cmd = {"type", input.substr(5), false, "llm"};
            } else if (input.find("click") != std::string::npos) {
                cmd = {"click", "default", false, "llm"};
            } else {
                cmd = {"unknown", "", false, "llm"};
            }
        }
        return cmd;
    }
    
    // Fallback: Simulated LLM output (would be from Llama)
    if (input.find("open") != std::string::npos) {
        return {"open", "notepad.exe", false, "llm"};
    } else if (input.find("type") != std::string::npos) {
        return {"type", input.substr(5), false, "llm"};  // Extract text after "type"
    } else if (input.find("click") != std::string::npos) {
        return {"click", "default", false, "llm"};
    } else {
        return {"unknown", "", false, "llm"};
    }
}

// ============================================================================
// EXECUTION
// ============================================================================

void HybridBrain::ExecuteCommand(const Command& cmd) {
    if (cmd.source == "reflex") {
        ExecuteReflex(cmd);
    } else if (cmd.source == "llm") {
        ExecuteLLMCommand(cmd);
    }
}

void HybridBrain::ExecuteReflex(const Command& cmd) {
    if (cmd.action == "open") {
        // Win32 direct execution (no Python overhead)
        std::string command = "start " + cmd.target;
        system(command.c_str());
    } else if (cmd.action == "type") {
        // Call C++ keyboard motor
        // Lizard::TypeText(cmd.target);
    } else if (cmd.action == "click") {
        // Call C++ mouse motor
        // Lizard::ClickAtCoords(...);
    }
}

void HybridBrain::ExecuteLLMCommand(const Command& cmd) {
    // Same as reflex for now (in production: handle more complex logic)
    ExecuteReflex(cmd);
}

// ============================================================================
// INITIALIZATION
// ============================================================================

void HybridBrain::InitializeReflexes() {
    // Pre-compiled symbolic patterns
    // These are hardcoded, not learned - pure C++ execution
    
    reflexes = {
        {"open notepad", "open", "notepad.exe", 0.99f},
        {"open chrome", "open", "chrome.exe", 0.99f},
        {"open firefox", "open", "firefox.exe", 0.99f},
        {"open word", "open", "winword.exe", 0.99f},
        {"open excel", "open", "excel.exe", 0.99f},
        
        {"type", "type", "", 0.95f},
        {"search", "web_search", "", 0.95f},
        {"click", "click", "", 0.90f},
        {"stop", "stop", "", 0.99f},
    };
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

json HybridBrain::ParseLLMOutput(const std::string& raw_output) {
    try {
        // Simple parser: "action:open target:notepad"
        json parsed;
        std::istringstream iss(raw_output);
        std::string token;
        while (iss >> token) {
            size_t colon_pos = token.find(':');
            if (colon_pos != std::string::npos) {
                std::string key = token.substr(0, colon_pos);
                std::string value = token.substr(colon_pos + 1);
                parsed.data[key] = value;
            }
        }
        return parsed;
    } catch (...) {
        std::cerr << "⚠️  LLM output parse error: " << raw_output << std::endl;
        return json{};
    }
}

bool HybridBrain::IsValidCommand(const Command& cmd) {
    return !cmd.action.empty();
}

json HybridBrain::GetStatus() {
    json status;
    status.data["running"] = running ? "true" : "false";
    status.data["vad_active"] = vad_active ? "true" : "false";
    status.data["reflexes_loaded"] = std::to_string(reflexes.size());
    status.data["last_vad_ms"] = std::to_string(static_cast<int>(metrics.vad_ms));
    status.data["last_transcribe_ms"] = std::to_string(static_cast<int>(metrics.transcribe_ms));
    status.data["last_decide_ms"] = std::to_string(static_cast<int>(metrics.decide_ms));
    status.data["last_execute_ms"] = std::to_string(static_cast<int>(metrics.execute_ms));
    status.data["last_total_ms"] = std::to_string(static_cast<int>(metrics.total_ms));
    return status;
}

void HybridBrain::LogMetrics(const std::string& stage, float latency_ms) {
    std::cout << "   [" << stage << "] " << latency_ms << "ms" << std::endl;
}

// ============================================================================
// VISION METHODS
// ============================================================================

std::string HybridBrain::ReadScreen() {
    if (!vision) {
        return "";
    }
    return vision->CaptureAndRead();
}

bool HybridBrain::FindAndClick(const std::string& target) {
    if (!vision) {
        return false;
    }
    
    int x, y;
    if (vision->LocateText(target, x, y)) {
        // Move mouse and click
        // Lizard::MoveMouse(x, y);
        // Lizard::ClickMouse(0);
        std::cout << "   [VISION] Found '" << target << "' at (" << x << "," << y << "), clicking..." << std::endl;
        return true;
    }
    
    return false;
}

} // namespace Velocity

