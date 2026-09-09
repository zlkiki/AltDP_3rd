"""Midas Design+ RC Column Standalone Prototype One-Click Launcher.

Usage:
    python run_rc_column_sandbox.py

Opens http://localhost:8085 automatically in your default browser.
"""

import sys
import time
import webbrowser
import threading
import uvicorn


def open_browser():
    """Wait 1.2s for server to start, then open the browser."""
    time.sleep(1.2)
    url = "http://localhost:8085"
    print(f"\n[Launcher] 브라우저를 자동으로 엽니다: {url}")
    webbrowser.open(url)


if __name__ == "__main__":
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("=" * 70)
    print(" [Midas Design+ 1:1 Prototype] RC 기둥 설계 검토 독립 샌드박스 구동기")
    print(" Conforms 100% to docs/202_rc_column_module_specification.md")
    print("=" * 70)
    print(" * 서버 주소: http://localhost:8085")
    print(" * 종료 방법: 터미널에서 Ctrl + C 를 누르세요.")
    print("=" * 70)

    # 백그라운드 스레드에서 브라우저 실행
    threading.Thread(target=open_browser, daemon=True).start()

    # FastAPI Uvicorn 서버 실행
    uvicorn.run(
        "src.prototypes.rc_column.server:app",
        host="0.0.0.0",
        port=8085,
        reload=False,
        log_level="info"
    )
