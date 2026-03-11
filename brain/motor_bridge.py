import ctypes
import os
import platform
import time
from typing import Optional, List, Union
from brain.types import (
    VirtualKeyCodes,
    SPECIAL_KEY_MAP,
    MouseButton,
    VolumeKeyCodes,
)

# CTYPES BRIDGE TO C++ SHARED LIBRARY
# NOTE: This module bridges Python calls to native C++ code
# All functions should use explicit types to enable C++ conversion

if platform.system() == "Windows":
    LIBRARY_CANDIDATES: List[str] = ["lizard.dll", "liblizard.dll"]
else:
    LIBRARY_CANDIDATES: List[str] = ["liblizard.so", "lizard.so"]

core_dir: str = os.path.join(os.path.dirname(__file__), "core_bin")
lib_path: Optional[str] = None
for name in LIBRARY_CANDIDATES:
    candidate_path: str = os.path.join(core_dir, name)
    if os.path.exists(candidate_path):
        lib_path = candidate_path
        break

# Provide a lightweight Python fallback if native lib is missing
if not lib_path:
    class _LizardStub:
        """Fallback stub when C++ library is not available"""

        def Core_MoveMouse(self, x: int, y: int) -> None:
            print(f"[Stub] MoveMouse({x}, {y})")

        def Core_ClickMouse(self, btn: int) -> None:
            print(f"[Stub] ClickMouse({btn})")

        def Core_ScrollMouse(self, amt: int) -> None:
            print(f"[Stub] ScrollMouse({amt})")

        def Core_TypeString(self, text: Union[bytes, str]) -> None:
            try:
                s: str = text.decode('utf-8') if isinstance(text, (bytes, bytearray)) else str(text)
            except Exception:
                s = str(text)
            print(f"[Stub] TypeString('{s}')")

        def Core_PressKey(self, vk: int) -> None:
            print(f"[Stub] PressKey({vk})")

        def Core_InitMouse(self) -> None:
            print("[Stub] InitMouse()")

        def Core_InitKeyboard(self) -> None:
            print("[Stub] InitKeyboard()")

    lizard = _LizardStub()
else:
    if platform.system() == "Windows" and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(core_dir)
    lizard = ctypes.CDLL(lib_path)

lizard.Core_MoveMouse.argtypes = [ctypes.c_int, ctypes.c_int]
lizard.Core_MoveMouse.restype = None

lizard.Core_ClickMouse.argtypes = [ctypes.c_int]
lizard.Core_ClickMouse.restype = None

lizard.Core_ScrollMouse.argtypes = [ctypes.c_int]
lizard.Core_ScrollMouse.restype = None

lizard.Core_TypeString.argtypes = [ctypes.c_char_p]
lizard.Core_TypeString.restype = None

lizard.Core_PressKey.argtypes = [ctypes.c_int]
lizard.Core_PressKey.restype = None

lizard.Core_InitMouse.argtypes = []
lizard.Core_InitMouse.restype = None

lizard.Core_InitKeyboard.argtypes = []
lizard.Core_InitKeyboard.restype = None


class MotorBridge:
    """
    Bridge between Python and C++ motor control library.
    All methods are static to match C++ module behavior.
    
    CONVERSION NOTE: This class directly maps to C++ MotorBridge with same
    method signatures. Each method should compile to equivalent C++ code.
    """

    _initialized: bool = False

    @staticmethod
    def init() -> None:
        """Initialize motor subsystems (mouse and keyboard)"""
        if not MotorBridge._initialized:
            lizard.Core_InitMouse()
            lizard.Core_InitKeyboard()
            MotorBridge._initialized = True

    @staticmethod
    def move_to(x: int, y: int) -> None:
        """Move mouse cursor to absolute coordinates"""
        MotorBridge.init()
        lizard.Core_MoveMouse(int(x), int(y))

    @staticmethod
    def click(button: str = "left") -> None:
        """Click mouse button"""
        MotorBridge.init()
        btn_code: int = 0 if button == "left" else 1
        lizard.Core_ClickMouse(btn_code)

    @staticmethod
    def double_click(button: str = "left", delay: float = 0.12) -> None:
        """Perform a double click with delay"""
        MotorBridge.click(button)
        time.sleep(delay)
        MotorBridge.click(button)

    @staticmethod
    def shift_click(x: int, y: int, button: str = "left") -> None:
        """Click with Shift key held"""
        MotorBridge.init()
        MotorBridge.move_to(int(x), int(y))
        MotorBridge.press_special('shift')
        MotorBridge.click(button)

    @staticmethod
    def scroll(amount: int) -> None:
        """Scroll mouse wheel"""
        MotorBridge.init()
        lizard.Core_ScrollMouse(int(amount))

    @staticmethod
    def type_text(text: str) -> None:
        """Type text string"""
        MotorBridge.init()
        text_bytes: bytes = text.encode('utf-8')
        lizard.Core_TypeString(text_bytes)

    @staticmethod
    def type_keys(text: Union[str, List[str]]) -> None:
        """
        Type keys. Handles both strings and special key lists.
        
        Args:
            text: String to type OR list of special key names
        """
        MotorBridge.init()

        # List of keys (e.g., ["win", "enter"])
        if isinstance(text, list):
            for key in text:
                key_lower: str = str(key).lower().strip()
                if key_lower in SPECIAL_KEY_MAP:
                    MotorBridge.press_special(key_lower)
                else:
                    MotorBridge.type_text(str(key))
            return

        # Plain string
        MotorBridge.type_text(str(text))

    @staticmethod
    def press_key(key_code: int) -> None:
        """Press key by virtual key code"""
        MotorBridge.init()
        lizard.Core_PressKey(int(key_code))

    @staticmethod
    def press_special_key(vk_code: int) -> None:
        """Press special key by virtual key code (volume, media, etc)"""
        MotorBridge.init()
        lizard.Core_PressKey(int(vk_code))

    @staticmethod
    def press_special(key_name: str) -> None:
        """
        Press special key by name.
        
        Supported keys:
        - win, enter, tab, esc, backspace, delete, space
        - shift, ctrl, alt
        - capslock, numlock, scrolllock
        - home, end, pageup, pagedown
        - up, down, left, right
        - f1-f12
        
        Args:
            key_name: Name of special key (lowercase)
        """
        key_name_lower: str = key_name.lower().strip()

        if key_name_lower not in SPECIAL_KEY_MAP:
            print(f"⚠️  Unknown special key: {key_name_lower}")
            return

        vk_code: int = SPECIAL_KEY_MAP[key_name_lower]
        MotorBridge.init()
        lizard.Core_PressKey(int(vk_code))

