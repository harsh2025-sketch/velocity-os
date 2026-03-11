"""
👁️ THE RETINA: OCR Vision System

When the Brain needs to find text on screen (e.g., "Click the Login button"),
it uses OCR to actually see and locate text.

This is the 3rd line of defense:
1. Reflex: No AI needed (Win+Type "Chrome")
2. Coordinates: Pre-mapped locations (points.json)
3. Vision: Actual OCR (this file) - most flexible but slower

Speed Optimization:
- Only scan visible regions (not the whole screen)
- Grayscale conversion (faster OCR)
- Integer-only arithmetic

Requires:
  pip install pytesseract mss opencv-python

And Tesseract-OCR installed:
  https://github.com/UB-Mannheim/tesseract/wiki
"""

import time
import json
from pathlib import Path
from typing import Optional, Tuple

try:
    import pytesseract
    import mss
    import cv2
    import numpy as np
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("[WARNING] OCR dependencies not installed. Install with: pip install pytesseract mss opencv-python")


# Point to Tesseract executable (adjust if installed elsewhere)
if HAS_OCR:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def find_text_on_screen(target_text: str, debug=True) -> Optional[Tuple[int, int]]:
    """
    Find text on screen using OCR and return its center coordinates.
    
    Args:
        target_text: Text to find (e.g., "Login", "Click here")
        debug: Print debug info
    
    Returns:
        Tuple of (x, y) coordinates of text center, or None if not found
    """
    if not HAS_OCR:
        print("[ERROR] OCR not available. Install: pip install pytesseract mss opencv-python")
        return None
    
    if debug:
        print(f"👁️  RETINA: Searching for '{target_text}'...")
    
    start_time = time.time()
    
    try:
        with mss.mss() as sct:
            # Capture primary monitor
            monitor = sct.monitors[1]
            
            # Capture screen to numpy array (no file I/O)
            screenshot = np.array(sct.grab(monitor))
            
            # Convert BGRA to BGR then to Grayscale (faster OCR)
            bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            
            # Optional: Enhance contrast for better OCR
            # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            # gray = clahe.apply(gray)
            
            # Run Tesseract OCR with detailed output
            data = pytesseract.image_to_data(
                gray,
                output_type=pytesseract.Output.DICT,
                config='--psm 6'  # Assume single uniform block of text
            )
            
            # Search for target text
            target_lower = target_text.lower().strip()
            n_boxes = len(data['text'])
            matches = []
            
            for i in range(n_boxes):
                detected_text = data['text'][i].lower().strip()
                confidence = int(data['conf'][i])
                
                # Skip low-confidence matches
                if confidence < 30:
                    continue
                
                # Check for exact or partial match
                if target_lower in detected_text or detected_text in target_lower:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # Calculate center
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    matches.append({
                        'text': detected_text,
                        'x': center_x,
                        'y': center_y,
                        'confidence': confidence,
                        'width': w,
                        'height': h
                    })
            
            if matches:
                # Use highest confidence match
                best_match = max(matches, key=lambda m: m['confidence'])
                elapsed = time.time() - start_time
                
                if debug:
                    print(f"[OK] Found '{best_match['text']}' @ ({best_match['x']}, {best_match['y']}) "
                          f"[{best_match['confidence']}% confidence, {elapsed:.2f}s]")
                
                return (best_match['x'], best_match['y'])
            else:
                elapsed = time.time() - start_time
                if debug:
                    print(f"[FAIL] Text '{target_text}' not found on screen [{elapsed:.2f}s]")
                return None
                
    except Exception as e:
        print(f"[ERROR] OCR error: {e}")
        return None


def find_phrase_region(phrase: str, debug: bool = True) -> Optional[Tuple[int, int, int, int]]:
    """
    Attempt to find a multi-word phrase region by locating the first and last
    words on screen and returning a bounding rectangle that covers the phrase.

    Returns: (x, y, width, height) or None
    """
    if not HAS_OCR:
        return None

    try:
        tokens = [t for t in phrase.lower().strip().split() if t]
        if not tokens:
            return None

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = np.array(sct.grab(monitor))
            bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

            data = pytesseract.image_to_data(
                gray,
                output_type=pytesseract.Output.DICT,
                config='--psm 6'
            )

            n_boxes = len(data['text'])
            first_box = None
            last_box = None

            for i in range(n_boxes):
                detected_text = data['text'][i].lower().strip()
                conf = int(data['conf'][i])
                if conf < 30:
                    continue
                if not detected_text:
                    continue

                if detected_text in tokens or any(token in detected_text for token in tokens):
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]

                    if first_box is None:
                        first_box = (x, y, w, h)
                    # Update last_box every time we see a token; assuming left-to-right scan
                    last_box = (x, y, w, h)

            if first_box and last_box:
                x1, y1, w1, h1 = first_box
                x2, y2, w2, h2 = last_box
                left = min(x1, x2)
                top = min(y1, y2)
                right = max(x1 + w1, x2 + w2)
                bottom = max(y1 + h1, y2 + h2)
                region = (left, top, right - left, bottom - top)
                if debug:
                    print(f"✅ Phrase region for '{phrase}': {region}")
                return region
            else:
                if debug:
                    print(f"❌ Phrase '{phrase}' not found on screen")
                return None

    except Exception as e:
        print(f"❌ OCR phrase error: {e}")
        return None


def find_button_region(button_name: str, debug=True) -> Optional[Tuple[int, int, int, int]]:
    """
    Find a button by name and return its bounding box.
    
    Returns:
        Tuple of (x, y, width, height), or None if not found
    """
    if not HAS_OCR:
        return None
    
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = np.array(sct.grab(monitor))
            bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            button_name_lower = button_name.lower().strip()
            
            for i in range(len(data['text'])):
                if button_name_lower in data['text'][i].lower():
                    return (
                        data['left'][i],
                        data['top'][i],
                        data['width'][i],
                        data['height'][i]
                    )
        
        return None
        
    except Exception as e:
        print(f"❌ Button search error: {e}")
        return None


def screenshot_to_text(region: Optional[Tuple[int, int, int, int]] = None) -> str:
    """
    Convert screen or region to text using OCR.
    
    Args:
        region: Optional (x, y, width, height) tuple. If None, scans entire screen.
    
    Returns:
        Extracted text
    """
    if not HAS_OCR:
        return ""
    
    try:
        with mss.mss() as sct:
            if region:
                x, y, w, h = region
                monitor = {'left': x, 'top': y, 'width': w, 'height': h}
            else:
                monitor = sct.monitors[1]
            
            screenshot = np.array(sct.grab(monitor))
            bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            
            text = pytesseract.image_to_string(gray)
            return text.strip()
        
    except Exception as e:
        print(f"❌ Text extraction error: {e}")
        return ""


def validate_on_screen(text: str) -> bool:
    """Check if text exists on the current screen."""
    return find_text_on_screen(text, debug=False) is not None


# Legacy class for backward compatibility
class OCRWorker:
    """Text extraction using Tesseract OCR"""
    
    def __init__(self):
        self.ocr = HAS_OCR
    
    async def initialize(self):
        """Initialize OCR engine"""
        if self.ocr:
            print("[OCR] Tesseract OCR ready")
        else:
            print("[OCR] Tesseract OCR not available")
    
    async def extract_text(self, image_array) -> list:
        """Extract text from image"""
        if not self.ocr:
            return []
        
        try:
            text = pytesseract.image_to_string(image_array)
            return text.split('\n')
        except:
            return []
    
    async def shutdown(self):
        """Cleanup"""
        pass

        print("[OCR] Shutting down")
