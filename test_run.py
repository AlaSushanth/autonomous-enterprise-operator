import asyncio
import subprocess
import time
import sys
from pathlib import Path
from rich.console import Console

# UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from core.runtime import AutonomousOperatorRuntime

console = Console(force_terminal=True, legacy_windows=False)

async def run_automated_test():
    console.print("[bold cyan]==================================================[/bold cyan]")
    console.print("[bold cyan] Starting Autonomous Operator Automated Test Suite[/bold cyan]")
    console.print("[bold cyan]==================================================[/bold cyan]")

    # 1. Start Mock ERP Server
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "mock_env.server:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "error"],
        cwd=str(Path(__file__).parent)
    )
    time.sleep(2.0)

    try:
        runtime = AutonomousOperatorRuntime(
            base_url="http://127.0.0.1:8000",
            workspace_dir=Path(__file__).parent,
            headless=True
        )
        
        # Override HITL approval for test automation
        runtime.hitl.request_approval = lambda action_name, reason, payload, risk_level="HIGH": (True, "Auto-approved for test suite", payload)

        result = await runtime.run_goal(
            "Scan incoming invoices, check PO allocations, submit to NexusERP portal, and verify outcomes."
        )

        console.print(f"\n[bold green]Test Result Status:[/bold green] {result.status}")
        console.print(f"[bold white]Steps Executed:[/bold white] {result.steps_executed}")
        console.print(f"[bold white]Self-Healing Retries:[/bold white] {result.retries_performed}")
        console.print(f"[bold white]Ground-Truth Verifications Passed:[/bold white] {sum(1 for v in result.verifications if v.verified)}/{len(result.verifications)}")

    finally:
        server_process.terminate()
        server_process.wait()
        console.print("\n[bold green]✓ Test Server Cleanly Shut Down.[/bold green]")

if __name__ == "__main__":
    asyncio.run(run_automated_test())
