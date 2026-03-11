#pragma once

#include <vector>
#include <string>

namespace Velocity {

// OpenCV + Tesseract Vision Pipeline
class VisionEngine {
public:
    VisionEngine();
    ~VisionEngine();
    
    // Initialize vision (load Tesseract, init OpenCV)
    void Init();
    
    // Capture screenshot and run OCR
    std::string CaptureAndRead();
    
    // Find text on screen (returns coordinates)
    bool LocateText(const std::string& target, int& x, int& y);
    
    // Read specific screen region
    std::string ReadRegion(int x, int y, int width, int height);
    
private:
    void* tesseract_api = nullptr;  // TessBaseAPI*
    bool initialized = false;
};

} // namespace Velocity
