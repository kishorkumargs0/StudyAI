import socket
import threading
import time
import urllib.request

import uvicorn
import webview

from app.main import app

TITLE = "StudyAI"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_until_ready(url, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def start_server(port):
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    return server


def main():
    port = free_port()
    server = start_server(port)
    url = f"http://127.0.0.1:{port}/"
    if not wait_until_ready(url):
        raise SystemExit("StudyAI could not start its local server.")
    webview.create_window(TITLE, url, width=1280, height=860, min_size=(900, 600))
    webview.start()
    server.should_exit = True


if __name__ == "__main__":
    main()
