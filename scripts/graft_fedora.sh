#!/bin/bash
# Fedora Installation Script with SystemD Service
# Requires: root, development-tools, Python 3.11+

echo "=== VELOCITY A-OS: Fedora Graft Script ==="

if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root" 
   exit 1
fi

# Install dependencies
echo "[SETUP] Installing Fedora packages..."
dnf install -y \
    @development-tools \
    cmake \
    python3.11 \
    python3-devel \
    cargo \
    libX11-devel \
    libXi-devel

# Build C++ core
echo "[BUILD] Compiling C++ Lizard Core..."
cd core
mkdir -p build
cd build
cmake ..
cmake --build . --config Release
cd ../..

# Setup Python
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_senses.txt

# Create SystemD service
echo "[SERVICE] Creating SystemD service..."
cat > /etc/systemd/system/velocity-aos.service << EOF
[Unit]
Description=Velocity A-OS Brain
After=network.target

[Service]
Type=simple
User=velocity
ExecStart=/opt/velocity-aos/venv/bin/python /opt/velocity-aos/brain/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable velocity-aos

echo "VELOCITY A-OS installed with SystemD service!"
echo "Start with: systemctl start velocity-aos"
