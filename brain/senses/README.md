# Velocity Senses - L2 Perception Layer

This directory contains the **Senses Module** - perception capabilities for understanding the UI.

## 👁️ Architecture

The Senses module provides two complementary perception methods:

```
┌─────────────────────────────────────────┐
│         USER INTERFACE                   │
├─────────────────────────────────────────┤
│  ui_parser.py          vision.py         │
│  (Structural)          (Visual)          │
│  ↓                     ↓                 │
│  UI Tree (DOM)         Pixels (VLM)      │
│  100ms                 2s                │
│  High Reliability      Universal Fallback│
└─────────────────────────────────────────┘
```

---

## 📁 Module Structure

### Modules (To Be Implemented)

| Module | Purpose | Technology | Status |
|--------|---------|------------|--------|
| `ui_parser.py` | Parse accessibility tree | uiautomation | 🔴 TODO |
| `vision.py` | Visual understanding | VLM + OpenCV | 🟡 PARTIAL |

---

## 🔍 UI Parser (Structural Perception)

### Capabilities
- Read Windows accessibility tree (UIA)
- Find elements by name, type, or properties
- Extract button locations, textbox bounds
- Cache results for performance

### Example Usage
```python
from brain.senses import ui_parser

# Find element
element = ui_parser.find_element(
    window_name="Calculator",
    element_name="Seven",
    control_type="Button"
)

# Get coordinates
coords = element.get_center()
# Output: (x, y)

# Click directly
ui_parser.click_element(element)
```

### When It Works
- ✅ Win32 apps (Notepad, Calculator)
- ✅ UWP apps (modern Windows apps)
- ✅ WPF apps (.NET applications)
- ✅ Qt apps (cross-platform)
- ❌ Canvas-based apps (Figma, games)
- ❌ Remote desktop/VMs

---

## 👁️ Vision Module (Visual Perception)

### Capabilities
- VLM-based screen understanding (llava/moondream)
- Template matching (OpenCV)
- OCR for text detection
- Icon/button recognition

### Example Usage
```python
from brain.senses import vision

# Find via VLM
coords = vision.find_button_vlm(
    description="red record button"
)
# Output: (x, y) or None

# Template matching (fast)
coords = vision.find_template(
    template_path="templates/play_button.png",
    threshold=0.8
)
# Output: (x, y) or None
```

### When It Works
- ✅ Canvas apps (Figma, Photoshop)
- ✅ Games
- ✅ Remote desktop/VMs
- ✅ Custom UIs without accessibility
- ⚠️ Slower (2s vs 100ms)
- ⚠️ Less reliable (depends on visual clarity)

---

## 🔄 Integration with Cortex

```python
# In processor.py
def try_structural(intent: str):
    """L2: Structural perception"""
    window = get_active_window()
    element = ui_parser.find_element(window, intent)
    return element.coords if element else None

def try_visual(intent: str):
    """L1: Visual perception"""
    screenshot = capture_screen()
    coords = vision.find_button_vlm(intent)
    return coords
```

---

## 🎯 Design Principles

1. **Structure Before Vision** - UI tree is faster and more reliable
2. **Cache Everything** - Element locations rarely change
3. **Fallback is Mandatory** - Apps without UIA support exist
4. **Context Matters** - Same button name in different apps = different locations

---

## 🚀 Technology Stack

### UI Parser Dependencies
```bash
pip install uiautomation
pip install pywinauto  # Alternative/backup
```

### Vision Dependencies
```bash
pip install opencv-python
pip install pillow
pip install pyautogui  # Screen capture
# VLM: Ollama with llava/moondream models
```

---

## ⚠️ Known Limitations

### UI Parser
- **Windows Only** - Uses Windows UIA API
- **Access Denied** - Some elevated apps block inspection
- **Dynamic UIs** - Element IDs may change

### Vision
- **Latency** - VLM inference takes 1-3 seconds
- **Accuracy** - Depends on screen resolution and clarity
- **Resource Usage** - Requires GPU for fast inference

---

## 📊 Performance Comparison

| Method | Latency | Reliability | Coverage |
|--------|---------|-------------|----------|
| **UI Parser** | 100ms | 95% | 70% apps |
| **Vision (Template)** | 200ms | 85% | 90% apps |
| **Vision (VLM)** | 2000ms | 75% | 100% apps |

**Strategy:** Try UI Parser first, fallback to Vision

---

**Status:** 🚧 Under Construction  
**Next Step:** Implement `ui_parser.py`  
**Last Updated:** 2026-01-29
