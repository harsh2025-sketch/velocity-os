#!/usr/bin/env python3
"""
VELOCITY OS - UNIFIED LAUNCHER
Main entry point for starting the Velocity Operating System

Features:
- Pre-flight dependency checks
- Automatic path and environment setup
- Brain (core intelligence) initialization
- Motor bridge integration
- Clean shutdown handling
- Optional test mode with intent publisher
"""
import subprocess
import time
import sys
import os
import io
import argparse

# Fix emoji encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Change to project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

# Track background processes
processes = []

def banner():
    """Display startup banner"""
    print("\n" + "=" * 70)
    print("VELOCITY OPERATING SYSTEM")
    print("=" * 70)
    print(f"Root: {PROJECT_ROOT}")
    print(f"Python: {sys.executable}")
    print("=" * 70 + "\n")

def check_dependencies():
    """Verify all required dependencies are installed"""
    print("Pre-flight Dependency Check...\n")
    
    dependencies = {
        'zmq': 'pyzmq',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'cv2': 'opencv-python'
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    
    print("\nAll dependencies satisfied\n")
    return True

def check_brain_module():
    """Verify brain module can be imported"""
    print("🧠 Checking Brain Module...\n")
    try:
        from brain.main import VelocityBrain
        print("  ✓ Brain module loaded")
        return True
    except ImportError as e:
        print(f"  ✗ Brain import failed: {e}")
        return False

def check_motor_bridge():
    """Verify motor bridge is available"""
    print("\n🔧 Checking Motor Bridge...\n")
    try:
        from brain.motor_bridge import MotorBridge
        MotorBridge.init()
        print("  ✓ Motor bridge initialized")
        return True
    except Exception as e:
        print(f"  ✗ Motor bridge failed: {e}")
        return False

def start_brain_direct():
    """Start brain directly in this process (blocking)"""
    from brain.main import VelocityBrain
    
    print("\n" + "=" * 70)
    print("🧠 STARTING VELOCITY BRAIN")
    print("=" * 70)
    print("\nBrain is now listening for intents...")
    print("   To test: python scripts/send_intents.py")
    print("\n🛑 Press Ctrl+C to stop\n")
    
    brain = VelocityBrain()
    
    # Keep alive - brain runs in background threads
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down brain...")
        print("✓ Shutdown complete")

def start_service(name, script_path, description):
    """Start a service in background process"""
    print(f"\n[{name}] Starting: {description}...")
    try:
        p = subprocess.Popen(
            [sys.executable, script_path],
            cwd=PROJECT_ROOT
        )
        processes.append((name, p))
        print(f"[{name}] ✓ PID {p.pid}")
        time.sleep(2)  # Allow initialization
        
        # Check if process is still alive
        if p.poll() is not None:
            print(f"[{name}] ✗ Process died immediately")
            return False
        
        return True
    except Exception as e:
        print(f"[{name}] ✗ Failed: {e}")
        return False

def start_with_test_intents():
    """Start brain + test intent publisher in separate processes"""
    print("\n" + "=" * 70)
    print("🧠 VELOCITY - TEST MODE")
    print("=" * 70)
    
    # 1. Start Brain
    if not start_service("BRAIN", "brain/main.py", "Core Intelligence"):
        print("\nFailed to start brain")
        return False
    
    # 2. Start Intent Publisher
    if not start_service("INTENTS", "scripts/send_intents.py", "Test Intent Publisher"):
        print("\nBrain running but intent publisher failed")
        print("   You can still send intents manually")
    
    print("\n" + "=" * 70)
    print("VELOCITY ONLINE - TEST MODE")
    print("=" * 70)
    print("\nTest intents being sent to brain...")
    print("🛑 Press Ctrl+C to stop all services\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Terminating all services...")
        for name, p in processes:
            try:
                p.terminate()
                p.wait(timeout=5)
                print(f"[{name}] Terminated")
            except:
                try:
                    p.kill()
                except:
                    pass
        print("\n✓ All services stopped")

def main():
    parser = argparse.ArgumentParser(
        description='Velocity OS Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  velocity_launch.py              # Start brain (normal mode)
  velocity_launch.py --test       # Start with test intent publisher
  velocity_launch.py --no-check   # Skip dependency checks (faster)
        """
    )
    parser.add_argument('--test', action='store_true',
                       help='Start with test intent publisher')
    parser.add_argument('--no-check', action='store_true',
                       help='Skip dependency checks')
    
    args = parser.parse_args()
    
    banner()
    
    # Pre-flight checks (unless skipped)
    if not args.no_check:
        if not check_dependencies():
            return 1
        
        if not check_brain_module():
            return 1
        
        if not check_motor_bridge():
            return 1
    
    # Launch mode
    try:
        if args.test:
            start_with_test_intents()
        else:
            start_brain_direct()
        
        return 0
        
    except Exception as e:
        print(f"\nFatal Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
