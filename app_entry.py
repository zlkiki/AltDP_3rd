"""AltDP_3rd Application Entry Point.

This module provides programmatic and CLI entry point to start the AltDP_3rd
web-based structural member design platform.
"""

import sys
import uvicorn

def main():
    """Start AltDP_3rd web application server."""
    port = 8000
    host = "127.0.0.1"
    
    print("=======================================================================")
    print("  🚀 AltDP_3rd - Web-based Structural Member Design Platform")
    print("     KDS 14 20 00 / KDS 14 31 00 Engineering System")
    print("=======================================================================")
    print(f"[*] Starting server at http://{host}:{port}")
    print(f"[*] Interactive API docs at http://{host}:{port}/docs")
    
    uvicorn.run("src.api.server:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()
