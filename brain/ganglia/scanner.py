"""
🕵️ THE INDEXER: Scans Windows Start Menu to build app database.

This script teaches the Brain what applications are installed on the system.
No hardcoding. No guessing. Just facts from the filesystem.

Usage: python brain/ganglia/scanner.py
Output: brain/ganglia/installed_apps.json
"""

import os
import json
from pathlib import Path
import winreg

OUTPUT_FILE = Path("brain/ganglia/installed_apps.json")

# Standard Windows Start Menu Paths
START_MENU_PATHS = [
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    os.path.join(os.getenv('APPDATA'), r"Microsoft\Windows\Start Menu\Programs")
]

def scan_shortcuts():
    """Scan .lnk files from Start Menu."""
    print("🔍 Scanning Start Menu shortcuts...")
    apps = {}
    
    for base_path in START_MENU_PATHS:
        if not os.path.exists(base_path):
            continue
            
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(".lnk"):
                    # Clean name: "Google Chrome.lnk" -> "chrome"
                    clean_name = file.lower().replace(".lnk", "").strip()
                    
                    # Remove common prefixes for better matching
                    for prefix in ["google ", "microsoft ", "oracle ", "adobe "]:
                        if clean_name.startswith(prefix):
                            clean_name = clean_name[len(prefix):]
                    
                    # Remove common suffixes
                    for suffix in [" - shortcut", " (legacy)", " (portable)"]:
                        if clean_name.endswith(suffix):
                            clean_name = clean_name[:-len(suffix)]
                    
                    clean_name = clean_name.strip()
                    
                    if clean_name:
                        apps[clean_name] = file.replace(".lnk", "")
    
    return apps

def scan_registry():
    """Scan Windows Registry for installed applications."""
    print("🔍 Scanning Registry for applications...")
    apps = {}
    
    try:
        # 32-bit and 64-bit application paths
        paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for path in paths:
            try:
                reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                for i in range(winreg.QueryInfoKey(reg)[0]):
                    try:
                        subkey_name = winreg.EnumKey(reg, i)
                        subkey = winreg.OpenKey(reg, subkey_name)
                        
                        # Try to get DisplayName
                        try:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            clean_name = display_name.lower().strip()
                            
                            # Remove version numbers and noise
                            for prefix in ["google ", "microsoft ", "oracle ", "adobe ", "jetbrains "]:
                                if clean_name.startswith(prefix):
                                    clean_name = clean_name[len(prefix):]
                            
                            clean_name = clean_name.split()[0] if clean_name else None
                            
                            if clean_name and len(clean_name) > 2:
                                apps[clean_name] = display_name
                        except:
                            pass
                        
                        winreg.CloseKey(subkey)
                    except:
                        pass
                        
                winreg.CloseKey(reg)
            except:
                pass
    except Exception as e:
        print(f"⚠️  Registry scan failed: {e}")
    
    return apps

def merge_indexes(shortcuts, registry):
    """Merge Start Menu and Registry data."""
    print("🔀 Merging indexes...")
    merged = {**registry, **shortcuts}
    return merged

def save_index(apps):
    """Save the app index to JSON."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(apps, f, indent=2)
    
    print(f"✅ Indexed {len(apps)} applications → {OUTPUT_FILE}")

def main():
    print("\n" + "="*60)
    print("🕵️  VELOCITY INDEXER: Building System Knowledge")
    print("="*60 + "\n")
    
    # Scan both sources
    shortcuts = scan_shortcuts()
    registry = scan_registry()
    
    # Merge
    apps = merge_indexes(shortcuts, registry)
    
    # Save
    save_index(apps)
    
    print("\n📋 Sample of indexed apps:")
    for name in sorted(list(apps.keys())[:10]):
        print(f"   • {name}")
    
    if len(apps) > 10:
        print(f"   ... and {len(apps) - 10} more")
    
    print(f"\n✨ System awareness complete! Brain now knows {len(apps)} apps.\n")

if __name__ == "__main__":
    main()
