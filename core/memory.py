import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

DEFAULT_MEMORY_PATH = Path(__file__).parent.parent / "data" / "company_rules.json"

class OrganizationalMemory:
    def __init__(self, memory_path: Optional[Path] = None):
        self.memory_path = memory_path or DEFAULT_MEMORY_PATH
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.rules: List[Dict[str, Any]] = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if not self.memory_path.exists():
            default_rules = [
                {
                    "rule_id": "RULE-01",
                    "category": "APPROVAL_POLICY",
                    "condition": "invoice_amount < 1000.0",
                    "instruction": "Auto-approve without human intervention if PO is valid."
                },
                {
                    "rule_id": "RULE-02",
                    "category": "APPROVAL_POLICY",
                    "condition": "invoice_amount >= 1000.0",
                    "instruction": "Enforce Human-in-the-Loop manager approval with diff preview."
                }
            ]
            self._save(default_rules)
            return default_rules
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self, rules: List[Dict[str, Any]]):
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(rules, f, indent=2)

    def get_all_rules(self) -> List[Dict[str, Any]]:
        return self.rules

    def get_formatted_context(self) -> str:
        lines = ["=== Organizational Rules & Company Memory ==="]
        for r in self.rules:
            lines.append(f"[{r.get('rule_id', 'RULE')}] ({r.get('category', 'GENERAL')}) {r.get('instruction')}")
        return "\n".join(lines)

    def record_human_learning(self, category: str, feedback: str, context: Optional[Dict[str, Any]] = None):
        new_rule_id = f"RULE-{len(self.rules) + 1:02d}"
        new_rule = {
            "rule_id": new_rule_id,
            "category": category,
            "instruction": feedback,
            "context": context or {},
            "source": "HUMAN_OPERATOR_FEEDBACK"
        }
        self.rules.append(new_rule)
        self._save(self.rules)
        return new_rule
