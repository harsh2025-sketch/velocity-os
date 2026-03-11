
# Velocity A-OS: Native Large Action Model

A biological operating system that autonomously pilots your computer. Eyes, hands, brains—and the safety to match.

this is an experiment to know what will happen if we give control of mouse, keybord to an ai agent how it will work.
## Architecture

```
velocity-os/
├── brain/                          # THE COGNITIVE LAYER (Python)
│   ├── main.py                     # THE THALAMUS (Traffic Router)
│   ├── motor_bridge.py             # Communication Link to Lizard Core
│   │
│   ├── ganglia/                    # SYSTEM 1.5 (Habit Center - Fast)
│   │   ├── __init__.py
│   │   ├── automation.py           # Regex-based Action Router
│   │   ├── shell_scripts.py        # Native App Launchers
│   │   └── patterns.json           # Habit Patterns
│   │
│   └── wizard/                     # SYSTEM 2.0 (Strategic Center - Slow)
│       ├── __init__.py
│       ├── planner.py              # LLM Chain (Goal Decomposition)
│       ├── vision_logic.py         # Semantic Image Analysis (YOLO/OCR)
│       ├── memory_bank.py          # ChromaDB (Long-term Memory)
│       └── llm_client.py           # Ollama Interface
│
├── data/                           # PERSISTENCE
│   └── vectordb/                   # ChromaDB Storage
│
└── requirements.txt                # Python Dependencies
```

## Build & Run

```bash
# 1. Build C++ Lizard Core
cd brain/lizard
mkdir build && cd build
cmake ..
cmake --build .

# 2. Install Python deps
pip install -r requirements.txt

# 3. Start Thalamus
cd brain
python main.py
```

## Example Usage

```
Goal: Book a flight to NYC tomorrow
[WIZARD] Planning...
[EXECUTE] Open browser
[EXECUTE] Navigate to airline website
[EXECUTE] Click booking button
[EXECUTE] Enter travel dates
...
```
