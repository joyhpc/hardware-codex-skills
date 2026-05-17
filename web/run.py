"""Run the local web app, automatically avoiding occupied ports."""

from __future__ import annotations

import socket
import sys
from pathlib import Path


HOST = "127.0.0.1"
DEFAULT_PORT = 8000
MAX_PORT = 8099


def port_is_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) != 0


def find_available_port(host: str = HOST, start: int = DEFAULT_PORT) -> int:
    for port in range(start, MAX_PORT + 1):
        if port_is_free(host, port):
            return port
    raise RuntimeError(f"No free port found in {start}-{MAX_PORT}.")


def main() -> None:
    import uvicorn

    web_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(web_dir))
    from app import app

    port = find_available_port()
    url = f"http://{HOST}:{port}"
    print(f"Serving hardware-codex-skills web app at {url}", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    uvicorn.run(
        app,
        host=HOST,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
