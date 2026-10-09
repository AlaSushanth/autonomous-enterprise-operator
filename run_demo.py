import subprocess
import time
import sys
import os
from pathlib import Path

def start_demo():
    print("==================================================")
    print(" CentrAlign AI — Autonomous Operator Demo Launcher")
    print("==================================================")
    
    server_script = Path(__file__).parent / "mock_env" / "server.py"
    cli_script = Path(__file__).parent / "cli.py"

    print("\n[1/2] Launching NexusERP Local Mock Portal on http://127.0.0.1:8000...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "mock_env.server:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "error"],
        cwd=str(Path(__file__).parent)
    )

    # Wait for server to be ready
    time.sleep(1.5)

    try:
        print("\n[2/2] Starting Autonomous Operator Runtime...")
        subprocess.run([sys.executable, str(cli_script)], cwd=str(Path(__file__).parent))
    finally:
        print("\nStopping mock server...")
        server_process.terminate()
        server_process.wait()
        print("Demo complete.")

if __name__ == "__main__":
    start_demo()
