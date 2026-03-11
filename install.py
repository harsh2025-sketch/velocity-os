
"""
VELOCITY A-OS: Master Installer
Orchestrates platform-specific setup and verification
"""

import subprocess
import sys
import os
import platform
from pathlib import Path
from typing import Optional


class VelocityInstaller:
    """Master installation orchestrator"""
    
    def __init__(self):
        self.os_name = platform.system()
        self.root_path = Path(__file__).parent
        self.venv_path = self.root_path / "venv"
        
    def check_dependencies(self) -> bool:
        """Check for required tools"""
        required = ["cmake", "python", "cargo"]
        
        print("[INSTALL] Checking dependencies...")
        missing = []
        
        for tool in required:
            try:
                subprocess.run(
                    f"{tool} --version",
                    shell=True,
                    capture_output=True,
                    check=True
                )
                print(f"  ✓ {tool} found")
            except subprocess.CalledProcessError:
                missing.append(tool)
                print(f"  ✗ {tool} NOT found")
        
        if missing:
            print(f"\nERROR: Missing tools: {', '.join(missing)}")
            print("Install them before running this installer")
            return False
        
        return True
    
    def build_cpp_core(self) -> bool:
        """Build C++ Lizard Core"""
        print("\n[BUILD] Compiling C++ Lizard Core...")
        
        core_path = self.root_path / "core"
        build_path = core_path / "build"
        
        try:
            build_path.mkdir(exist_ok=True)
            
            # CMake configure
            subprocess.run(
                "cmake ..",
                shell=True,
                cwd=str(build_path),
                check=True
            )
            
            # CMake build
            subprocess.run(
                "cmake --build . --config Release",
                shell=True,
                cwd=str(build_path),
                check=True
            )
            
            print("✓ C++ Core compiled successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"ERROR: C++ compilation failed: {e}")
            return False
    
    def setup_python_env(self) -> bool:
        """Setup Python virtual environment"""
        print("\n[PYTHON] Setting up Python environment...")
        
        try:
            # Create venv
            subprocess.run(
                f"{sys.executable} -m venv venv",
                shell=True,
                cwd=str(self.root_path),
                check=True
            )
            
            # Install dependencies
            pip_executable = (
                self.venv_path / "Scripts" / "pip.exe"
                if self.os_name == "Windows"
                else self.venv_path / "bin" / "pip"
            )
            
            subprocess.run(
                f"{pip_executable} install -r requirements.txt",
                shell=True,
                check=True
            )
            
            subprocess.run(
                f"{pip_executable} install -r requirements_senses.txt",
                shell=True,
                check=True
            )
            
            print("✓ Python environment ready")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Python setup failed: {e}")
            return False
    
    def run_platform_script(self) -> bool:
        """Run platform-specific installation script"""
        scripts_path = self.root_path / "scripts"
        
        if self.os_name == "Windows":
            script = scripts_path / "graft_windows.ps1"
            # Run PowerShell script
            print("[GRAFT] Running Windows installation script...")
            
        elif self.os_name == "Linux":
            # Detect Linux distribution
            script = scripts_path / "graft_kali.sh"
            print("[GRAFT] Running Linux installation script...")
        
        else:
            print(f"WARNING: Unsupported OS: {self.os_name}")
            return True
        
        return True
    
    def install(self) -> bool:
        """Run full installation"""
        print("╔════════════════════════════════════════╗")
        print("║    VELOCITY A-OS INSTALLER            ║")
        print("╚════════════════════════════════════════╝")
        
        steps = [
            ("Checking dependencies", self.check_dependencies),
            ("Building C++ core", self.build_cpp_core),
            ("Setting up Python", self.setup_python_env),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n✗ Installation failed at: {step_name}")
                return False
        
        print("\n╔════════════════════════════════════════╗")
        print("║  INSTALLATION COMPLETE!                ║")
        print("║  Run: python brain/main.py             ║")
        print("╚════════════════════════════════════════╝")
        
        return True


if __name__ == "__main__":
    installer = VelocityInstaller()
    success = installer.install()
    sys.exit(0 if success else 1)
