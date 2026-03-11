#!/bin/bash
# Kali Linux Installation Script for Velocity A-OS
# Requires: root, build-essentials, Python 3.11+

echo "=== VELOCITY A-OS: Kali Graft Script ==="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root" 
   exit 1
fi

# Update system
echo "[SETUP] Updating system packages..."
apt-get update && apt-get upgrade -y

# Install dependencies
echo "[SETUP] Installing build dependencies..."
apt-get install -y \
    build-essential \
    cmake \
    python3.11 \
    python3-pip \
    python3-venv \
    cargo \
    rustc \
    libx11-dev \
    libxi-dev \
    libxt-dev

# Build C++ core
echo "[BUILD] Compiling C++ Lizard Core..."
cd core
mkdir -p build
cd build
cmake ..
cmake --build . --config Release
cd ../..

if [ $? -ne 0 ]; then
    echo "ERROR: C++ compilation failed"
    exit 1
fi

echo "✓ C++ Core compiled successfully"

# Setup Python environment
echo "[PYTHON] Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate venv
source venv/bin/activate

# Install Python dependencies
echo "[PIP] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements_senses.txt

echo "✓ Python dependencies installed"

# Grant necessary capabilities
echo "[PERMISSIONS] Granting necessary Linux capabilities..."
# Allow input event injection
setcap cap_sys_nice,cap_dac_override=ep ./core/build/lizard

echo "VELOCITY A-OS installation complete!"
echo "Run 'python brain/main.py' to start"
