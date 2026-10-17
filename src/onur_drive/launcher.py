"""Open the local four-camera laboratory dashboard from a bundled Windows executable.

No vehicle data access, no OEM camera permissions, no controls and no external server.
"""
from __future__ import annotations

import socket
import threading
import time
import webbrowser

from onur_drive.service import CameraRunner, make_app

HOST = "127.0.0.1"
PORT = 8765


def open_dashboard_when_ready(host: str = HOST, port: int = PORT, max_wait_s: float = 25) -> bool:
    end = time.monotonic() + max_wait_s
    while time.monotonic() < end:
        try:
            with socket.create_connection((host, port), timeout=0.35):
                webbrowser.open(f"http://{host}:{port}")
                return True
        except OSError:
            time.sleep(0.2)
    return False


def main() -> None:
    import uvicorn
    print("ONUR DRIVE AI - FOUR CAMERA SYNTHETIC LAB - NOT CONNECTED TO MG HS")
    print(f"Open in browser: http://{HOST}:{PORT}")
    print("No vehicle commands, no camera speed-limit bypass. Close this window to exit.")
    runner = CameraRunner(source_spec="multi-synthetic")
    threading.Thread(target=open_dashboard_when_ready, daemon=True).start()
    uvicorn.run(make_app(runner), host=HOST, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
