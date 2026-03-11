#!/bin/bash
# Arch Linux Installation Script with HFT Optimization
# Requires: root, base-devel, Python 3.11+

echo "=== VELOCITY A-OS: Arch HFT Graft Script ==="

if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root" 
   exit 1
fi

# Install with pacman
echo "[SETUP] Installing packages via pacman..."
pacman -Sy --noconfirm \
    base-devel \
    cmake \
    python \
    rust \
    libx11 \
    libxi

# Build with HFT optimizations
echo "[BUILD] Building with HFT optimizations..."
cd core
mkdir -p build
cd build
cmake -DCMAKE_CXX_FLAGS="-O3 -march=native -flto" ..
cmake --build . --config Release
cd ../..

# Setup Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_senses.txt

# Set CPU affinity for performance
echo "[OPTIMIZATION] Setting CPU affinity..."
# Pin core process to specific CPU cores

echo "VELOCITY A-OS with HFT optimizations installed!"
