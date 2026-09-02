#!/usr/bin/env python3
"""
scripts/install_ghidra_env.py
=============================
Automated installer for Ghidra and OpenJDK 21 in C:\\tools.
Downloads portable zip archives directly from official GitHub releases and extracts them.
Zero admin/UAC prompt required.
"""

import os
import sys
import shutil
import urllib.request
import zipfile
from pathlib import Path

TOOLS_DIR = Path(r"C:\tools")
JDK_DIR = TOOLS_DIR / "jdk-21"
GHIDRA_DIR = TOOLS_DIR / "ghidra_12.1.3_PUBLIC"

# Direct Official Release URLs / API Redirects
JDK_URL = "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse"
GHIDRA_URL = "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.3_build/ghidra_12.1.3_PUBLIC_20260817.zip"



def download_file(url: str, dest: Path, desc: str):
    print(f"[*] Downloading {desc} from {url}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
        total_size = int(response.info().get('Content-Length', 0))
        downloaded = 0
        block_size = 1024 * 1024  # 1MB
        
        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            out_file.write(buffer)
            downloaded += len(buffer)
            if total_size > 0:
                percent = downloaded / total_size * 100
                print(f"\r    Progress: {downloaded / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB ({percent:.1f}%)", end="", flush=True)
    print("\n[+] Download complete.")


def extract_zip(zip_path: Path, extract_to: Path, desc: str):
    print(f"[*] Extracting {desc} to {extract_to}...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_to)
    print(f"[+] Extracted {desc}.")


def install_jdk():
    if (JDK_DIR / "bin" / "java.exe").exists():
        print(f"[+] OpenJDK 21 is already installed at {JDK_DIR}")
        return

    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    zip_dest = TOOLS_DIR / "jdk21.zip"
    try:
        download_file(JDK_URL, zip_dest, "OpenJDK 21")
        
        temp_extract = TOOLS_DIR / "jdk_temp"
        temp_extract.mkdir(parents=True, exist_ok=True)
        extract_zip(zip_dest, temp_extract, "OpenJDK 21")
        
        # Move inner folder (e.g. jdk-21.0.12+1) to target JDK_DIR
        subdirs = [d for d in temp_extract.iterdir() if d.is_dir()]
        if subdirs:
            inner_dir = subdirs[0]
            if JDK_DIR.exists():
                shutil.rmtree(JDK_DIR)
            shutil.move(str(inner_dir), str(JDK_DIR))
        shutil.rmtree(temp_extract, ignore_errors=True)
        print(f"[+] Successfully installed OpenJDK 21 to {JDK_DIR}")
    finally:
        if zip_dest.exists():
            zip_dest.unlink()


def install_ghidra():
    headless_bat = GHIDRA_DIR / "support" / "analyzeHeadless.bat"
    if headless_bat.exists():
        print(f"[+] Ghidra 12.1.3 is already installed at {GHIDRA_DIR}")
        return

    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    zip_dest = TOOLS_DIR / "ghidra.zip"
    try:
        download_file(GHIDRA_URL, zip_dest, "Ghidra 12.1.3")
        
        temp_extract = TOOLS_DIR / "ghidra_temp"
        temp_extract.mkdir(parents=True, exist_ok=True)
        extract_zip(zip_dest, temp_extract, "Ghidra 12.1.3")
        
        # Move inner folder (e.g. ghidra_12.1.3_PUBLIC) to target GHIDRA_DIR
        subdirs = [d for d in temp_extract.iterdir() if d.is_dir()]
        if subdirs:
            inner_dir = subdirs[0]
            if GHIDRA_DIR.exists():
                shutil.rmtree(GHIDRA_DIR)
            shutil.move(str(inner_dir), str(GHIDRA_DIR))
        shutil.rmtree(temp_extract, ignore_errors=True)
        print(f"[+] Successfully installed Ghidra to {GHIDRA_DIR}")
    finally:
        if zip_dest.exists():
            zip_dest.unlink()


def main():
    print("==================================================")
    print(" AltDP_3rd Ghidra & OpenJDK 21 Automated Installer ")
    print("==================================================")
    install_jdk()
    install_ghidra()
    
    # Test verify
    java_exe = JDK_DIR / "bin" / "java.exe"
    headless_bat = GHIDRA_DIR / "support" / "analyzeHeadless.bat"
    
    print("\n[+] Verification:")
    print(f"    - Java Executable: {java_exe.exists()} ({java_exe})")
    print(f"    - Ghidra Headless: {headless_bat.exists()} ({headless_bat})")
    
    if java_exe.exists() and headless_bat.exists():
        print("\n[SUCCESS] Ghidra and JDK 21 installation completed successfully!")
    else:
        print("\n[ERROR] Installation verification failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
