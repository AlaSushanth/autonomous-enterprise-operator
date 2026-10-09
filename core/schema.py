from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

class ActionRiskLevel(str, Enum):
    SAFE = "SAFE"                 # Read-only actions (read file, view page, query DB)
    MEDIUM = "MEDIUM"             # Staging, navigating, form filling
    HIGH = "HIGH"                 # Payment authorizations, record deletions, writes > threshold

class ActionType(str, Enum):
    READ_FILE = "READ_FILE"
    LIST_FILES = "LIST_FILES"
    BROWSE_URL = "BROWSE_URL"
    CLICK_ELEMENT = "CLICK_ELEMENT"
    FILL_FORM = "FILL_FORM"
    QUERY_DATABASE = "QUERY_DATABASE"
    REQUEST_APPROVAL = "REQUEST_APPROVAL"
    VERIFY_OUTCOME = "VERIFY_OUTCOME"

class SubGoal(BaseModel):
    id: str
    description: str
    action_type: ActionType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_level: ActionRiskLevel = ActionRiskLevel.SAFE
    requires_approval: bool = False
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED
    result: Optional[Any] = None
    error: Optional[str] = None

class ExecutionPlan(BaseModel):
    goal: str
    thought_process: str
    sub_goals: List[SubGoal] = Field(default_factory=list)

class StepObservation(BaseModel):
    step_id: str
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    dom_snapshot: Optional[str] = None
    screenshot_path: Optional[str] = None

class VerificationResult(BaseModel):
    verified: bool
    target_id: str
    checks_passed: List[str] = Field(default_factory=list)
    checks_failed: List[str] = Field(default_factory=list)
    evidence_payload: Dict[str, Any] = Field(default_factory=dict)

class AuditEvidencePack(BaseModel):
    task_goal: str
    status: str
    steps_executed: int
    retries_performed: int
    human_interventions: int
    verifications: List[VerificationResult] = Field(default_factory=list)
    execution_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
