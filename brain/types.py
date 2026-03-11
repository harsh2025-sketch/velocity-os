"""
VELOCITY Types Module
Explicit data structures for C++ conversion compatibility
Defines all types, enums, and constants used throughout the system
"""

from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import Optional, Dict, List, Tuple, Any


# ============== ACTION TYPES ==============
class ActionType(str, Enum):
    """All possible action types"""
    CLICK = "click"
    OPEN = "open"
    TYPE = "type"
    PRESS_KEY = "press_key"
    PRESS_SPECIAL_KEY = "press_special_key"
    SELECT = "select"
    WEB_SEARCH = "web_search"
    STOP = "stop"
    SPEAK = "speak"


class SelectMode(str, Enum):
    """Selection modes"""
    WORD = "word"
    ALL = "all"
    PHRASE = "phrase"


# ============== KEY CODES ==============
class VirtualKeyCodes(IntEnum):
    """Windows Virtual Key Codes"""
    BACKSPACE = 0x08
    TAB = 0x09
    ENTER = 0x0D
    SHIFT = 0x10
    CTRL = 0x11
    ALT = 0x12
    CAPSLOCK = 0x14
    ESC = 0x1B
    SPACE = 0x20
    PAGEUP = 0x21
    PAGEDOWN = 0x22
    END = 0x23
    HOME = 0x24
    LEFT = 0x25
    UP = 0x26
    RIGHT = 0x27
    DOWN = 0x28
    DELETE = 0x2E
    NUMLOCK = 0x90
    SCROLLLOCK = 0x91
    WIN = 0x5B
    F1 = 0x70
    F2 = 0x71
    F3 = 0x72
    F4 = 0x73
    F5 = 0x74
    F6 = 0x75
    F7 = 0x76
    F8 = 0x77
    F9 = 0x78
    F10 = 0x79
    F11 = 0x7A
    F12 = 0x7B


class SpecialKeyNames(str, Enum):
    """Special key name mappings"""
    WIN = "win"
    ENTER = "enter"
    RETURN = "return"
    TAB = "tab"
    ESC = "esc"
    ESCAPE = "escape"
    BACKSPACE = "backspace"
    DELETE = "delete"
    SPACE = "space"
    SHIFT = "shift"
    CTRL = "ctrl"
    ALT = "alt"
    CAPSLOCK = "capslock"
    NUMLOCK = "numlock"
    SCROLLLOCK = "scrolllock"
    HOME = "home"
    END = "end"
    PAGEUP = "pageup"
    PAGEDOWN = "pagedown"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    F1 = "f1"
    F2 = "f2"
    F3 = "f3"
    F4 = "f4"
    F5 = "f5"
    F6 = "f6"
    F7 = "f7"
    F8 = "f8"
    F9 = "f9"
    F10 = "f10"
    F11 = "f11"
    F12 = "f12"


# Map special key names to key codes
SPECIAL_KEY_MAP: Dict[str, int] = {
    "win": VirtualKeyCodes.WIN,
    "enter": VirtualKeyCodes.ENTER,
    "return": VirtualKeyCodes.ENTER,
    "tab": VirtualKeyCodes.TAB,
    "esc": VirtualKeyCodes.ESC,
    "escape": VirtualKeyCodes.ESC,
    "backspace": VirtualKeyCodes.BACKSPACE,
    "delete": VirtualKeyCodes.DELETE,
    "space": VirtualKeyCodes.SPACE,
    "shift": VirtualKeyCodes.SHIFT,
    "ctrl": VirtualKeyCodes.CTRL,
    "alt": VirtualKeyCodes.ALT,
    "capslock": VirtualKeyCodes.CAPSLOCK,
    "numlock": VirtualKeyCodes.NUMLOCK,
    "scrolllock": VirtualKeyCodes.SCROLLLOCK,
    "home": VirtualKeyCodes.HOME,
    "end": VirtualKeyCodes.END,
    "pageup": VirtualKeyCodes.PAGEUP,
    "pagedown": VirtualKeyCodes.PAGEDOWN,
    "up": VirtualKeyCodes.UP,
    "down": VirtualKeyCodes.DOWN,
    "left": VirtualKeyCodes.LEFT,
    "right": VirtualKeyCodes.RIGHT,
    "f1": VirtualKeyCodes.F1,
    "f2": VirtualKeyCodes.F2,
    "f3": VirtualKeyCodes.F3,
    "f4": VirtualKeyCodes.F4,
    "f5": VirtualKeyCodes.F5,
    "f6": VirtualKeyCodes.F6,
    "f7": VirtualKeyCodes.F7,
    "f8": VirtualKeyCodes.F8,
    "f9": VirtualKeyCodes.F9,
    "f10": VirtualKeyCodes.F10,
    "f11": VirtualKeyCodes.F11,
    "f12": VirtualKeyCodes.F12,
}


# ============== MOUSE CODES ==============
class MouseButton(IntEnum):
    """Mouse button codes"""
    LEFT = 0
    RIGHT = 1
    MIDDLE = 2


class VolumeKeyCodes(IntEnum):
    """Volume and media control key codes"""
    VOLUME_MUTE = 0xAD
    VOLUME_DOWN = 0xAE
    VOLUME_UP = 0xAF
    MEDIA_PLAY_PAUSE = 0xB3


# ============== ACTION PLAN STRUCTURES ==============
@dataclass
class ClickAction:
    """Click action parameters"""
    action: str = ActionType.CLICK
    target_name: Optional[str] = None  # Known point name from map
    target_text: Optional[str] = None  # Text to find on screen
    x: int = 0  # Absolute coordinates
    y: int = 0
    button: str = "left"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "target_name": self.target_name,
            "target_text": self.target_text,
            "x": self.x,
            "y": self.y,
            "button": self.button,
        }


@dataclass
class OpenAction:
    """Open app action parameters"""
    action: str = ActionType.OPEN
    app: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"action": self.action, "app": self.app}


@dataclass
class TypeAction:
    """Type text action parameters"""
    action: str = ActionType.TYPE
    text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"action": self.action, "text": self.text}


@dataclass
class SelectAction:
    """Select text action parameters"""
    action: str = ActionType.SELECT
    target: Optional[str] = None
    mode: str = SelectMode.WORD

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "target": self.target,
            "mode": self.mode,
        }


@dataclass
class PressKeyAction:
    """Press key action parameters"""
    action: str = ActionType.PRESS_KEY
    key_code: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {"action": self.action, "key_code": self.key_code}


@dataclass
class PressSpecialKeyAction:
    """Press special key action parameters"""
    action: str = ActionType.PRESS_SPECIAL_KEY
    key_name: Optional[str] = None
    code: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "key_name": self.key_name,
            "code": self.code,
        }


@dataclass
class WebSearchAction:
    """Web search action parameters"""
    action: str = ActionType.WEB_SEARCH
    query: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"action": self.action, "query": self.query}


@dataclass
class SpeechAction:
    """Speech/speak action parameters"""
    action: str = ActionType.SPEAK
    text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"action": self.action, "text": self.text}


@dataclass
class StopAction:
    """Stop/cancel action parameters"""
    action: str = ActionType.STOP

    def to_dict(self) -> Dict[str, Any]:
        return {"action": self.action}


# ============== COORDINATE STRUCTURES ==============
@dataclass
class Coordinate:
    """2D screen coordinate"""
    x: int
    y: int

    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def to_dict(self) -> Dict[str, int]:
        return {"x": self.x, "y": self.y}


@dataclass
class Region:
    """Screen region (bounding box)"""
    x: int
    y: int
    width: int
    height: int

    def to_tuple(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)

    def to_dict(self) -> Dict[str, int]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }


@dataclass
class ScreenPoint:
    """Named screen point from coordinates map"""
    name: str
    x: int
    y: int
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "description": self.description,
        }


# ============== INTENT/COMMAND STRUCTURES ==============
@dataclass
class UserIntent:
    """User's expressed intent"""
    text: str
    timestamp: float = 0.0
    is_corrected: bool = False
    original_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "timestamp": self.timestamp,
            "is_corrected": self.is_corrected,
            "original_text": self.original_text,
        }


@dataclass
class ActionPlan:
    """Complete action plan from planner"""
    action: str
    target_name: Optional[str] = None
    target_text: Optional[str] = None
    target: Optional[str] = None
    app: Optional[str] = None
    text: Optional[str] = None
    query: Optional[str] = None
    speech: Optional[str] = None
    mode: Optional[str] = None
    x: int = 0
    y: int = 0
    button: str = "left"
    key_name: Optional[str] = None
    phrase: Optional[str] = None
    code: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None and (not isinstance(value, int) or value != 0):
                result[key] = value
        return result


# ============== VISION STRUCTURES ==============
@dataclass
class TextLocation:
    """Location of text found on screen"""
    text: str
    x: int
    y: int
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "confidence": self.confidence,
        }


# ============== CONFIGURATION STRUCTURES ==============
@dataclass
class BrainConfig:
    """Brain configuration"""
    strict_mode: bool = True
    log_file: str = "brain.log"
    points_json: str = "brain/ganglia/points.json"
    patterns_json: str = "brain/ganglia/patterns.json"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strict_mode": self.strict_mode,
            "log_file": self.log_file,
            "points_json": self.points_json,
            "patterns_json": self.patterns_json,
        }


# ============== RESULT STRUCTURES ==============
@dataclass
class ExecutionResult:
    """Result of action execution"""
    success: bool
    action: str
    message: str = ""
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "message": self.message,
            "error": self.error,
            "details": self.details,
        }
