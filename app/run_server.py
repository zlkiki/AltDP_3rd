"""
AltDP Member Designer - Robust Server Launcher with Health Check & Auto Browser Open
"""
import os
import sys
import time
import socket
import threading
import subprocess
import webbrowser

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"

def kill_port(port=PORT):
    """Terminates any process currently listening on the target port."""
    if sys.platform == "win32":
        try:
            cmd = f'powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"'
            subprocess.run(cmd, shell=True, capture_output=True)
        except Exception:
            pass

def wait_for_server(host=HOST, port=PORT, timeout=10.0):
    """Waits until the server is listening and ready to accept connections."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            time.sleep(0.2)
    return False

def open_browser_when_ready():
    """Background worker to open the browser only after the server is fully ready."""
    if wait_for_server():
        time.sleep(0.3)
        print(f"[INFO] Server is READY at {URL}! Opening browser...")
        webbrowser.open(URL)
    else:
        print(f"[WARNING] Server did not respond within timeout, but you can try opening {URL} manually.")

def main():
    args = sys.argv[1:]
    action = args[0].lower() if args else "start"

    if action == "stop":
        print(f"[STOP] Terminating server on port {PORT}...")
        kill_port(PORT)
        print("[STOP] Server stopped.")
        sys.exit(0)

    elif action == "restart":
        print(f"[RESTART] Stopping existing server on port {PORT}...")
        kill_port(PORT)
        time.sleep(1.0)
        action = "start"

    print("=" * 60)
    print("        AltDP Member Designer Launcher (54 Modules)       ")
    print("=" * 60)
    print()

    kill_port(PORT)

    # Spawn thread to open browser once server is actually listening
    browser_thread = threading.Thread(target=open_browser_when_ready, daemon=True)
    browser_thread.start()

    reload_flag = action == "dev" or "--reload" in args
    
    import uvicorn
    from app.main import app

    print(f"[START] Launching Uvicorn server on {URL} (reload={reload_flag})...")
    print(f"[INFO] Press Ctrl+C in this window to stop the server.")
    print("=" * 60)
    print()

    try:
        uvicorn.run(
            "app.main:app" if reload_flag else app,
            host=HOST,
            port=PORT,
            reload=reload_flag,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user.")
    finally:
        kill_port(PORT)
        sys.exit(0)

if __name__ == "__main__":
    main()
