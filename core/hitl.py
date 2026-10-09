import json
from typing import Dict, Any, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console(force_terminal=True, legacy_windows=False)

class HumanInTheLoop:
    def __init__(self, console_instance: Console = None):
        self.console = console_instance or console

    def request_approval(
        self,
        action_name: str,
        reason: str,
        payload: Dict[str, Any],
        risk_level: str = "HIGH"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Presents structured action diff and requests human sign-off.
        Returns: (is_approved, human_feedback, updated_payload)
        """
        table = Table(title="[bold yellow]⚠️ Human-in-the-Loop Approval Required[/bold yellow]", border_style="yellow")
        table.add_column("Field / Parameter", style="cyan")
        table.add_column("Proposed Value", style="white")

        for k, v in payload.items():
            table.add_row(str(k), str(v))

        self.console.print()
        self.console.print(
            Panel(
                f"[bold red]Action Risk Level: {risk_level}[/bold red]\n"
                f"[bold white]Action:[/bold white] {action_name}\n"
                f"[bold white]Trigger Reason:[/bold white] {reason}",
                title="[bold red]SECURITY / POLICY INTERCEPT[/bold red]",
                border_style="red"
            )
        )
        self.console.print(table)
        self.console.print("[dim]Options: [green][Y][/green] Approve | [red][N][/red] Reject | [cyan][M][/cyan] Modify Values | [magenta][R][/magenta] Add Learned Rule[/dim]")
        
        choice = Prompt.ask("Authorize this action?", choices=["y", "n", "m", "r"], default="y")
        
        if choice == "y":
            self.console.print("[bold green]✓ Action Approved by Human Operator.[/bold green]")
            return True, "Approved directly", payload
        
        elif choice == "n":
            feedback = Prompt.ask("Reason for rejection / instructions for agent", default="Cancelled by human operator.")
            self.console.print(f"[bold red]✗ Action Rejected: {feedback}[/bold red]")
            return False, feedback, payload
        
        elif choice == "m":
            field = Prompt.ask("Which field to modify?", choices=list(payload.keys()))
            new_val = Prompt.ask(f"Enter new value for {field}")
            payload[field] = new_val
            self.console.print(f"[bold cyan]✓ Field '{field}' updated to '{new_val}'. Approving modified action.[/bold cyan]")
            return True, f"Modified {field} to {new_val}", payload
        
        elif choice == "r":
            rule_feedback = Prompt.ask("Enter the rule/preference to record in organizational memory")
            self.console.print(f"[bold magenta]✓ Rule recorded: '{rule_feedback}'. Proceeding with action.[/bold magenta]")
            return True, f"LEARNED_RULE:{rule_feedback}", payload

        return False, "Aborted", payload
