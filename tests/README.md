# Velocity OS - Test Suite

This directory contains all test files for the Velocity Operating System.

## Test Organization

All test files have been moved here to keep the project root clean and organized.

## Available Tests

### Core Component Tests
- **test_components.py** - Tests core system components
- **test_cpp_components.py** - Tests C++ compiled components integration
- **test_core_latency.py** - Measures core system latency and performance
- **test_motor.py** - Tests the motor bridge (action execution layer)

### Path & Integration Tests
- **test_path_a.py** - Tests Path A (Python-based brain) functionality
- **test_integration_validation.py** - Validates full system integration
- **test_phase2_4_integration.py** - Phase 2-4 integration validation

### Voice & Audio Tests
- **test_voice.py** - Voice recognition and STT (Speech-to-Text) tests
- **test_tts_direct.py** - Text-to-Speech direct tests
- **test_type_direct.py** - Direct typing tests

### Vision & UI Tests
- **verify_vision.py** - Vision/OCR system verification
- **test_focus_check.py** - Window focus detection tests
- **test_focus_proper.py** - Advanced focus management tests
- **test_clipboard_verify.py** - Clipboard operations verification
- **test_sighted_agent.py** - Vision-based agent tests

### AI & Planning Tests
- **test_planner_responses.py** - AI planner response validation
- **debug_planner.py** - Planner debugging utilities

### Validation Tests
- **test_recompile_validation.py** - C++ recompilation validation

## Running Tests

### Individual Test
```bash
# From project root
python tests/test_name.py
```

### Example: Test Core Components
```bash
python tests/test_components.py
```

### Example: Test Voice Recognition
```bash
python tests/test_voice.py
```

## Path Correction Note

Since all tests have been moved to the `tests/` subdirectory, any import statements in these files that reference project modules should use:

```python
import sys
import os
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

This ensures tests can properly import brain, core, and other project modules.

## Test Best Practices

1. **Before Running Tests**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Core System Tests**: Test the core components before integration tests

3. **Voice Tests**: Require microphone access and a quiet environment

4. **Vision Tests**: Require display and may need specific UI elements visible

5. **Integration Tests**: Should be run after component tests pass

## Continuous Testing

For development, you can run specific test suites to validate changes:
- Core changes → Run motor, components, and latency tests
- Brain changes → Run planner and integration tests
- Audio changes → Run voice and TTS tests
- Vision changes → Run vision and focus tests
