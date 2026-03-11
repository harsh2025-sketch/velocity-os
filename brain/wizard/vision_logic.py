import mss
import numpy as np
import cv2

class VisionLogic:
    def __init__(self):
        self.sct = mss.mss()

    def get_screenshot(self):
        """Captures the primary monitor at HFT-level speed."""
        monitor = self.sct.monitors[1]
        sct_img = self.sct.grab(monitor)
        img = np.array(sct_img)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def find_element(self, template_path, threshold=0.8):
        """Locates a UI element on the screen. Returns (x, y) or None."""
        screen = self.get_screenshot()
        template = cv2.imread(template_path)
        
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            h, w = template.shape[:2]
            return (max_loc[0] + w//2, max_loc[1] + h//2)
        return None
