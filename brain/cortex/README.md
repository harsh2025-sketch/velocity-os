# Velocity Cortex - L3 Logic Layer

This directory contains the **Cortex Module** - the decision-making brain of Velocity OS.

## 🧠 Architecture

The Cortex implements the **3-Layer Defense System**:

```
User Intent → processor.py
                ↓
    ┌───────────────────────────────────────┐
    ↓                   ↓                    ↓
[L4: SYMBOLIC]     [L2: STRUCTURAL]      [L1: VISUAL]
Memory JSON        UI Tree Parser        VLM Vision
0ms (instant)      100ms (reliable)      2s (universal)
    ↓                   ↓                    ↓
    └─────────────────────────────────────┘
              ↓
        Motor Bridge
              ↓
        System Action
```

---

## 📁 Module Structure

### Core Modules (To Be Implemented)

| Module | Purpose | Status |
|--------|---------|--------|
| `processor.py` | Master orchestrator (O.P.A.R.L. loop) | 🔴 TODO |
| `learning.py` | RL engine for confidence updates | 🔴 TODO |
| `observer.py` | Imitation learning recorder | 🔴 TODO |
| `synthesizer.py` | Converts raw logs → JSON skills | 🔴 TODO |

---

## 🎯 The O.P.A.R.L. Loop

**Observe → Plan → Act → Record → Learn**

```python
def execute_with_fallback(intent: str):
    """The 3-Layer Defense System"""
    
    # L4: Try Symbolic (JSON skills)
    result = try_symbolic(intent)
    if result and result.confidence > 0.7:
        return execute(result)
    
    # L2: Try Structural (UI Tree)
    result = try_structural(intent)
    if result and result.confidence > 0.6:
        return execute(result)
    
    # L1: Try Visual (VLM)
    result = try_visual(intent)
    if result and result.confidence > 0.5:
        return execute(result)
    
    # Total Failure: Ask for help
    return request_demonstration(intent)
```

---

## 🔧 Reinforcement Learning Engine

### Confidence Update Algorithm

```python
# Success
confidence = min(1.0, confidence + 0.1)
success_count += 1

# Failure
confidence = max(0.1, confidence - 0.2)
fail_count += 1

# Decay (prevent overfitting to stale data)
if time_since_use > 30_days:
    confidence *= 0.95
```

### Method Selection
- Always try highest confidence method first
- If fails, try next highest
- Record performance for future learning

---

## 📊 Imitation Learning Pipeline

### 1. Observer (Recording)
```python
# Record user actions
observer.start_recording()
# User performs task...
log = observer.stop_recording()
# Output: Raw interaction log
```

### 2. Synthesizer (Learning)
```python
# Convert log to skill
skill = synthesizer.generate_skill(log)
# Output: New entry in skills.json
```

---

## 🚀 Usage Example

```python
from brain.cortex import processor

# Execute with automatic fallback
result = processor.execute_with_fallback("play spotify")

# Result includes:
# - method_used: "symbolic" | "structural" | "visual"
# - latency_ms: execution time
# - success: True/False
# - confidence: 0.0-1.0
```

---

## ⚠️ Design Principles

1. **Fail Fast, Fallback Faster** - Don't retry the same method twice
2. **Always Log** - Every execution updates `execution_history.json`
3. **Never Guess** - If all layers fail, ask user for demonstration
4. **Learn from Everything** - Success AND failure both update confidence

---

**Status:** 🚧 Under Construction  
**Next Step:** Implement `processor.py`  
**Last Updated:** 2026-01-29
