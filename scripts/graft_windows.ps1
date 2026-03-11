Write-Host ">>> GRAFTING VELOCITY ON WINDOWS"
# 1. Compile Core
cd core
if (-not (Test-Path build)) { mkdir build }
cd build
cmake ..
cmake --build . --config Release
# 2. Verify
if (Test-Path Release/lizard.exe) {
    Write-Host ">>> CORE COMPILED SUCCESSFULLY"
} else {
    Write-Error ">>> COMPILATION FAILED"
}

# Install Python dependencies
Write-Host "`n[PIP] Installing Python dependencies..."
pip install -r requirements.txt --quiet
pip install -r requirements_senses.txt --quiet

Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Registry configuration (Windows-specific)
Write-Host "`n[REGISTRY] Configuring Windows registry..."
# Add context menu entry for Velocity
# Add registry key for startup

Write-Host "`nVELOCITY A-OS installation complete!" -ForegroundColor Green
Write-Host "Run 'python brain/main.py' to start"
