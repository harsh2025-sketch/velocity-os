/**
 * VELOCITY REFLEX DISPATCHER (C++)
 * Low-latency pattern matching for common commands.
 * Bypasses Python/LLM for instant "Open X", "Search Y", "Click Z".
 * 
 * Latency goal: < 5ms decision + dispatch.
 */

#include <string>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <cstring>
#include <cctype>

struct ReflexAction {
    std::string action;  // "open", "search", "click", "type", "none"
    std::string target;  // app name, query, text, etc.
};

class ReflexDispatcher {
private:
    // Common app mappings (O(1) lookup)
    std::unordered_map<std::string, std::string> app_map = {
        {"notepad", "notepad.exe"},
        {"explorer", "explorer.exe"},
        {"chrome", "chrome.exe"},
        {"edge", "msedge.exe"},
        {"firefox", "firefox.exe"},
        {"calc", "calc.exe"},
        {"code", "code.exe"},
        {"vscode", "code.exe"},
        {"terminal", "wt.exe"},
        {"powershell", "powershell.exe"},
        {"cmd", "cmd.exe"},
    };

    // Normalize text: lowercase, trim, remove filler
    std::string normalize(const std::string& text) {
        std::string result = text;
        // Lowercase
        std::transform(result.begin(), result.end(), result.begin(), ::tolower);
        // Trim
        auto start = result.find_first_not_of(" \t\n\r");
        auto end = result.find_last_not_of(" \t\n\r");
        if (start != std::string::npos) {
            result = result.substr(start, end - start + 1);
        }
        return result;
    }

    // Check if string starts with prefix
    bool starts_with(const std::string& str, const std::string& prefix) {
        return str.size() >= prefix.size() &&
               str.compare(0, prefix.size(), prefix) == 0;
    }

public:
    /**
     * Parse user intent and return reflex action.
     * Returns action="none" if no pattern matches (fallback to LLM).
     */
    ReflexAction dispatch(const std::string& intent) {
        std::string text = normalize(intent);
        
        // Pattern: "open <app>"
        if (starts_with(text, "open ")) {
            std::string app = text.substr(5);
            // Check if app is in map
            if (app_map.find(app) != app_map.end()) {
                return {"open", app};
            }
            // If not exact match, still try to open (fallback to Windows search)
            return {"open", app};
        }
        
        // Pattern: "search <query>" or "google <query>"
        if (starts_with(text, "search ")) {
            std::string query = text.substr(7);
            return {"web_search", query};
        }
        if (starts_with(text, "google ")) {
            std::string query = text.substr(7);
            return {"web_search", query};
        }
        
        // Pattern: "type <text>"
        if (starts_with(text, "type ")) {
            std::string target = text.substr(5);
            return {"type", target};
        }
        
        // Pattern: "click <text>"
        if (starts_with(text, "click ")) {
            std::string target = text.substr(6);
            return {"click", target};
        }
        
        // Pattern: "select <text>"
        if (starts_with(text, "select ")) {
            std::string target = text.substr(7);
            if (target == "all") {
                return {"select", "all"};
            }
            return {"select", target};
        }
        
        // Pattern: "stop", "cancel", "abort"
        if (text == "stop" || text == "cancel" || text == "abort" || starts_with(text, "stop")) {
            return {"stop", ""};
        }
        
        // No match: fallback to LLM
        return {"none", ""};
    }
};

// C API for Python ctypes
extern "C" {
#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT __attribute__((visibility("default")))
#endif
    
    static ReflexDispatcher g_reflex;
    
    // Dispatch intent and write action/target to buffers
    EXPORT int Core_DispatchIntent(const char* intent, char* action_buf, int action_len, char* target_buf, int target_len) {
        if (!intent || !action_buf || !target_buf) return -1;
        
        ReflexAction result = g_reflex.dispatch(intent);
        
        // Copy action
        strncpy(action_buf, result.action.c_str(), action_len - 1);
        action_buf[action_len - 1] = '\0';
        
        // Copy target
        strncpy(target_buf, result.target.c_str(), target_len - 1);
        target_buf[target_len - 1] = '\0';
        
        return 0;
    }
}
