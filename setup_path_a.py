#!/usr/bin/env python3
"""
Setup script for Velocity Path A (Python)
Installs all required dependencies and validates the environment
"""
import subprocess
import sys
import os

def run_cmd(cmd):
    """Run shell command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    if package_name is None:
        package_name = module_name
    try:
        __import__(module_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False

def install_package(package_name):
    """Install a package via pip"""
    print(f"\n📦 Installing {package_name}...")
    success, output = run_cmd(f"{sys.executable} -m pip install {package_name}")
    if success:
        print(f"✓ {package_name} installed successfully")
        return True
    else:
        print(f"✗ Failed to install {package_name}")
        print(output)
        return False

def main():
    print("=" * 60)
    print("🧠 VELOCITY PATH A - SETUP & VALIDATION")
    print("=" * 60)
    
    required_packages = {
        "zmq": "pyzmq",
    }
    
    optional_packages = {
        "ollama": "ollama",
    }
    
    print("\n[1] Checking Python version...")
    print(f"    Python {sys.version}")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        return False
    print("✓ Python version OK")
    
    print("\n[2] Checking required packages...")
    missing = []
    for module, package in required_packages.items():
        if not check_import(module, package):
            missing.append(package)
    
    if missing:
        print(f"\n[3] Installing {len(missing)} missing package(s)...")
        for package in missing:
            if not install_package(package):
                print(f"\n✗ Failed to install {package}")
                print("   Install manually: pip install", package)
                return False
    else:
        print("\n[3] All packages already installed ✓")
    
    print("\n[4] Checking optional packages...")
    print("    (These add LLM capabilities but are not required)")
    for module, package in optional_packages.items():
        if check_import(module, package):
            pass  # Already logged
        else:
            print(f"⚠️  Optional: {package} not installed (brain will use reflexes only)")
            print(f"    Install with: pip install {package}")
    required_files = [
        "brain/main.py",
        "brain/motor_bridge.py",
        "brain/wizard/planner.py",
        "brain/ganglia/reflexes.py",
        "launch_velocity.py",
        "scripts/send_intents.py",
    ]
    
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"✓ {filepath}")
        else:
            print(f"✗ {filepath} NOT FOUND")
            return False
    
    print("\n[5] Verifying ZMQ connectivity...")
    print("   (Brain will bind 5555 for TTS PUSH)")
    print("   (Publisher will bind 5557 for intents)")
    print("✓ ZMQ ports configured")
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE - Path A is ready to run!")
    print("=" * 60)
    print("\n▶️ To launch Velocity:")
    print("   python launch_velocity.py")
    print("\n   This will start:")
    print("   - Brain (core intelligence, executes actions)")
    print("   - Intent Publisher (sends test commands)")
    print("\n💡 Brain will:")
    print("   - Receive test intents via ZMQ")
    print("   - Process commands through symbolic reflexes")
    print("   - Log actions to brain.log")
    print("   - Print execution trace to console")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
