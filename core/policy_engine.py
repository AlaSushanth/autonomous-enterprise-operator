from typing import Dict, Any, Tuple
from core.schema import ActionRiskLevel, ActionType, SubGoal
from core.memory import OrganizationalMemory

class PolicyEngine:
    def __init__(self, memory: OrganizationalMemory):
        self.memory = memory
        self.high_value_threshold = 1000.0

    def evaluate_action(self, action_type: ActionType, params: Dict[str, Any]) -> Tuple[ActionRiskLevel, bool, str]:
        """
        Evaluates an action against company policies.
        Returns: (RiskLevel, RequiresHumanApproval, PolicyRationale)
        """
        if action_type in [ActionType.READ_FILE, ActionType.LIST_FILES, ActionType.QUERY_DATABASE, ActionType.VERIFY_OUTCOME]:
            return ActionRiskLevel.SAFE, False, "Read-only / Verification operations are pre-authorized."
        
        if action_type == ActionType.BROWSE_URL:
            return ActionRiskLevel.SAFE, False, "Web navigation within internal sandbox is permitted."
        
        if action_type in [ActionType.FILL_FORM, ActionType.CLICK_ELEMENT]:
            # Inspect amount if form submission or payment authorization
            amount = params.get("amount")
            if amount is not None:
                try:
                    num_amount = float(amount)
                    if num_amount >= self.high_value_threshold:
                        return (
                            ActionRiskLevel.HIGH,
                            True,
                            f"Action amount (${num_amount:,.2f}) meets or exceeds policy limit of ${self.high_value_threshold:,.2f}."
                        )
                except (ValueError, TypeError):
                    pass
            
            # Check for high-risk targets
            action_desc = params.get("description", "").lower()
            if "delete" in action_desc or "purge" in action_desc or "transfer" in action_desc:
                return ActionRiskLevel.HIGH, True, "Destructive or irrevocable operation requested."

            return ActionRiskLevel.MEDIUM, False, "Standard operational data entry."

        return ActionRiskLevel.SAFE, False, "Default safe policy."
