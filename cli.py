import os
import sys
import argparse
import asyncio
import subprocess
import time
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from core.runtime import AutonomousOperatorRuntime

console = Console(force_terminal=True, legacy_windows=False)

async def main():
    parser = argparse.ArgumentParser(description="CentrAlign Autonomous Enterprise Operator")
    parser.add_argument(
        "--goal",
        type=str,
        default="Scan incoming invoices, check PO allocations, submit to NexusERP portal, and verify outcomes.",
        help="Natural language business goal for the operator"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--headful",
        dest="headless",
        action="store_false",
        help="Run browser with visible UI (great for recording demos)"
    )

    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold cyan]CentrAlign AI — Founding Engineer Technical Submission[/bold cyan]\n"
        "[white]Prototype: Autonomous Company Operator Runtime (centra-operator)[/white]\n"
        "[dim]Architecture: Modular Multi-Environment Runtime with Dynamic AXTree, HITL & Verification[/dim]",
        border_style="cyan"
    ))

    # Initialize and run operator
    runtime = AutonomousOperatorRuntime(
        base_url="http://127.0.0.1:8000",
        workspace_dir=Path(__file__).parent,
        headless=args.headless
    )

    await runtime.run_goal(args.goal)

if __name__ == "__main__":
    asyncio.run(main())
