"""
Reflecting Pool - Desktop Launcher
Starts the Streamlit server and opens it in a native desktop window.
"""

import os
import sys
import subprocess
import socket
import threading
import time


def find_free_port(start=8501):
    """Find a free port starting from the given port."""
    for port in range(start, start + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start


def wait_for_server(port, timeout=30):
    """Wait until the Streamlit server is accepting connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.5)
    return False


def main():
    # Resolve paths relative to this executable / script
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    app_path = os.path.join(base_dir, "app.py")
    if not os.path.exists(app_path):
        print(f"Error: app.py not found at {app_path}")
        input("Press Enter to exit...")
        sys.exit(1)

    port = find_free_port()
    url = f"http://localhost:{port}"

    # Start Streamlit as a background subprocess
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--browser.serverAddress", "localhost",
        ],
        cwd=base_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for the server to be ready
    if not wait_for_server(port):
        print("Error: Streamlit server did not start in time.")
        proc.terminate()
        input("Press Enter to exit...")
        sys.exit(1)

    # Try native desktop window (pywebview), fall back to browser
    try:
        import webview
        window = webview.create_window(
            "Reflecting Pool",
            url,
            width=1280,
            height=900,
            min_size=(800, 600),
        )
        webview.start()
    except ImportError:
        import webbrowser
        print(f"Reflecting Pool running at {url}")
        print("(Install pywebview for a native desktop window: pip install pywebview)")
        print("Close this window to stop the server.\n")
        webbrowser.open(url)
        try:
            proc.wait()
        except KeyboardInterrupt:
            pass

    # Clean up the server when the window is closed
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


if __name__ == "__main__":
    main()
