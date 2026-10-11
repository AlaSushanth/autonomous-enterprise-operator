# CentrAlign AI — Autonomous Enterprise Operator (`centra-operator`)



---

### The 8-Step Autonomous Execution Cycle:

**Goal** ➔ **Context & Plan** ➔ **Policy Gate (HITL)** ➔ **Execute** ➔ **Observe** ➔ **Self-Heal** ➔ **Verify** ➔ **Evidence**

| Step | Stage Name | What Happens |
| :---: | :--- | :--- |
| **1** | **Goal** | Receives natural language objective (*"Process incoming vendor invoices and submit to ERP"*). |
| **2** | **Context & Plan** | Ingests invoice files, checks PO budgets, and plans the sequence of actions. |
| **3** | **Policy Gate** | Auto-approves small bills (< $1,000) or intercepts high-value bills (≥ $1,000) for human approval. |
| **4** | **Execute** | Navigates the ERP web portal via Playwright using semantic AXTree element locators. |
| **5** | **Observe** | Inspects page DOM responses, status banners, and error messages. |
| **6** | **Self-Heal** | If a submission fails (e.g. missing address), re-evaluates source metadata and auto-recovers. |
| **7** | **Verify** | Independently queries the SQLite database to confirm record insertion and amount accuracy. |
| **8** | **Evidence** | Emits an audit report with before/after state diffs, database assertions, and screenshot proofs. |

```
┌────────────────────────────────────────────────────────────────────────┐
│                       CENTRA OPERATOR RUNTIME                          │
│                                                                        │
│  [ Business Goal ] ──> [ Context & Organizational Memory ]             │
│                               │                                        │
│                               ▼                                        │
│                    [ Goal Decomposer & Plan ]                          │
│                               │                                        │
│                               ▼                                        │
│               [ Enterprise Policy & HITL Guard ]                       │
│                   ├── Auto-Approved (< $1,000)                         │
│                   └── Human Gate (>= $1,000 / High Risk)               │
│                               │                                        │
│                               ▼                                        │
│           [ Playwright AXTree & Semantic DOM Engine ]                  │
│                               │                                        │
│                               ▼                                        │
│               [ Dynamic Self-Healing & Recovery ]                      │
│                               │                                        │
│                               ▼                                        │
│             [ Independent Ground-Truth Verifier ]                      │
│                               │                                        │
│                               ▼                                        │
│          [ Audit Evidence Pack (Diffs, DB, Screenshots) ]              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Technical Differentiators

1. **AXTree Semantic DOM Grounding (No Fragile CSS Selectors):**
   * Dynamically inspects the live page to generate an indexed Accessibility Tree (`[1] Submit`, `[2] Amount`). Interacts deterministically across shifting layouts without brittle hardcoded selectors.
2. **Enterprise Policy & Risk-Based HITL Intercept:**
   * Automatically classifies read vs write operations and enforces organizational thresholds. High-value transactions trigger interactive Human-in-the-Loop review with exact diff previews.
3. **Dynamic Self-Healing & Error Recovery:**
   * When unexpected environmental constraints occur (e.g. ERP portal rejecting an invoice due to missing mandatory address metadata), the agent intercepts the failure observation, searches surrounding context/files for missing parameters, and re-executes.
4. **Independent Ground-Truth Verifier:**
   * Does not rely on LLM self-reporting. Validates actual database records, transaction hashes, and status codes post-execution.
5. **Organizational Memory Store:**
   * Retains organizational preferences and human corrections across runs, persisting them into `data/company_rules.json`.
6. **Auditable Evidence Pack:**
   * Generates a complete verification report containing before/after state diffs, database assertions, and screenshot artifacts.

---

## 🚀 Quickstart & Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Chrome / Chromium installed (for Playwright)

### 2. Installation
```bash
# Clone or navigate to the repository
cd centra-operator

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 3. Run the One-Click Demo
```bash
python run_demo.py
```

### 4. Run with Visible Browser (for Live Demos / Screen Recording)
```bash
# In terminal 1: Start mock ERP portal
uvicorn mock_env.server:app --port 8000

# In terminal 2: Run operator in headful mode
python cli.py --headful
```

---

## 🔍 Codebase Structure

```
centra-operator/
├── cli.py                     # Main CLI entrypoint
├── run_demo.py                # One-click demo launcher (starts server + operator)
├── requirements.txt           # Production dependencies
├── core/
│   ├── schema.py              # Pydantic models for plans, actions, policies, verifications
│   ├── runtime.py             # Main autonomous orchestrator state machine
│   ├── dom_grounding.py       # AXTree extractor & semantic Playwright interaction engine
│   ├── policy_engine.py       # Risk scoring and enterprise policy rules
│   ├── hitl.py                # Interactive CLI human-in-the-loop review interface
│   ├── verifier.py            # Independent ground-truth verifier & evidence generator
│   └── memory.py              # Long-term organizational memory & rule persistence
├── mock_env/
│   ├── server.py              # FastAPI mock enterprise ERP web portal with SQLite DB
│   └── incoming_invoices/     # Sample raw unstructured invoice files
├── data/
│   └── company_rules.json     # Persistent company policies and learned rules
└── evidence/                  # Generated audit evidence packs & proof screenshots
```

---


