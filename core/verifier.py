import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.schema import VerificationResult, AuditEvidencePack

class GroundTruthVerifier:
    """
    Independent verification layer that validates whether the requested outcome
    was actually achieved in the database and target environment.
    """
    def __init__(self, db_path: Path, evidence_dir: Path):
        self.db_path = db_path
        self.evidence_dir = evidence_dir
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def verify_invoice_in_db(self, invoice_id: str, expected_amount: float, expected_po: str) -> VerificationResult:
        """
        Directly queries the database to confirm record insertion and exact value match.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            SELECT invoice_id, po_number, vendor_name, amount, payment_terms, status, created_at
            FROM invoices WHERE invoice_id = ?
        """, (invoice_id,))
        row = c.fetchone()
        conn.close()

        passed = []
        failed = []

        if not row:
            failed.append(f"Invoice record '{invoice_id}' NOT FOUND in SQLite ERP database.")
            return VerificationResult(
                verified=False,
                target_id=invoice_id,
                checks_passed=passed,
                checks_failed=failed,
                evidence_payload={"error": "Record missing from database"}
            )

        passed.append(f"Found record in ERP database: ID '{row[0]}'")
        
        # Verify amount match (with float tolerance)
        db_amount = float(row[3])
        if abs(db_amount - expected_amount) < 0.01:
            passed.append(f"Amount verified: ${db_amount:,.2f} matches expected ${expected_amount:,.2f}")
        else:
            failed.append(f"Amount mismatch: DB=${db_amount:,.2f} vs Expected=${expected_amount:,.2f}")

        # Verify PO match
        db_po = row[1]
        if db_po == expected_po:
            passed.append(f"PO Number verified: '{db_po}' matches expected '{expected_po}'")
        else:
            failed.append(f"PO mismatch: DB='{db_po}' vs Expected='{expected_po}'")

        # Verify status is submitted
        db_status = row[5]
        if db_status == "SUBMITTED":
            passed.append(f"Status verified: '{db_status}'")
        else:
            failed.append(f"Status invalid: '{db_status}'")

        is_valid = len(failed) == 0
        evidence = {
            "invoice_id": row[0],
            "po_number": row[1],
            "vendor_name": row[2],
            "amount": row[3],
            "payment_terms": row[4],
            "status": row[5],
            "created_at": row[6]
        }

        return VerificationResult(
            verified=is_valid,
            target_id=invoice_id,
            checks_passed=passed,
            checks_failed=failed,
            evidence_payload=evidence
        )

    def generate_audit_report(self, pack: AuditEvidencePack) -> Path:
        """
        Saves a structured markdown and JSON audit evidence report.
        """
        report_path = self.evidence_dir / "audit_evidence_report.md"
        json_path = self.evidence_dir / "audit_evidence_pack.json"

        # Save JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(pack.model_dump(), f, indent=2)

        # Build Markdown
        md_lines = [
            "# 🛡️ Autonomous Operator Execution & Evidence Report",
            f"**Task Goal:** {pack.task_goal}",
            f"**Overall Status:** `{pack.status}`",
            f"**Total Steps Executed:** {pack.steps_executed} | **Self-Healing Retries:** {pack.retries_performed} | **Human Interventions:** {pack.human_interventions}",
            "",
            "## 🔍 Ground-Truth Verifications",
        ]

        for v in pack.verifications:
            status_icon = "✅" if v.verified else "❌"
            md_lines.append(f"### {status_icon} Verification Target: `{v.target_id}`")
            md_lines.append(f"- **Verification State:** `{'PASS' if v.verified else 'FAIL'}`")
            if v.checks_passed:
                md_lines.append("- **Passed Checks:**")
                for p in v.checks_passed:
                    md_lines.append(f"  - ✓ {p}")
            if v.checks_failed:
                md_lines.append("- **Failed Checks:**")
                for f in v.checks_failed:
                    md_lines.append(f"  - ✗ {f}")
            md_lines.append(f"```json\n{json.dumps(v.evidence_payload, indent=2)}\n```")
            md_lines.append("")

        md_lines.append("## 📜 Execution Timeline & Audit Trace")
        md_lines.append("| Step | Action | Status | Notes |")
        md_lines.append("| :--- | :--- | :--- | :--- |")
        for item in pack.execution_timeline:
            md_lines.append(f"| {item.get('step_id', '-')} | `{item.get('action', '-')}` | `{item.get('status', '-')}` | {item.get('notes', '-')} |")

        md_lines.append("")
        md_lines.append("## 📸 Captured Artifacts & Proofs")
        for a in pack.artifacts:
            md_lines.append(f"- `[{a}]`")

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return report_path
