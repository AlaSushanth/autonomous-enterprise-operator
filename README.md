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

## 📋 Evaluation Questionnaire Responses

### 1. What parts of your system are genuinely autonomous?
* **Multi-Step Goal Decomposition:** Autonomously scans input directories, parses varied JSON/document formats, matches corresponding purchase orders, and orchestrates actions across files, databases, and web browsers.
* **Semantic DOM Discovery:** Discovers and interacts with form controls on the fly using runtime AXTree mapping rather than rigid scraping scripts.
* **Self-Healing Loop:** Automatically catches form validation errors on the webpage, re-evaluates file context for missing fields, and completes submissions without human intervention.
* **Stopping & Completion Logic:** Assesses ground-truth status and decides when the global objective has been fulfilled.

### 2. What is currently hardcoded or manually configured?
* **Policy Thresholds:** Operational limits (e.g. `$1,000` approval threshold) are declared in policy configuration.
* **Tool Schemas:** Atomic action definitions (`BROWSE`, `FILL_FORM`, `QUERY_DB`) are strictly typed to enforce safety boundaries.
* **Environment Endpoints:** Base URLs and database paths are configured via environment parameters.

### 3. What models, frameworks, APIs, and libraries did you use?
* **Language & Runtime:** Python 3.11 with Pydantic for strict schema contracts.
* **Browser Automation:** Playwright for headless/headful browser automation and visual capture.
* **Backend & Mock ERP:** FastAPI + Uvicorn + SQLite3.
* **CLI & Telemetry:** Rich console for structured human-in-the-loop interactions and execution tables.

### 4. What is the biggest technical limitation of your current solution?
* **Single-Process Execution:** Long-horizon workflows run in a single process. In high-scale production, process restarts require a distributed durable execution engine (e.g. Temporal.io) to resume from exact checkpoints.
* **Obfuscated Desktop UI:** While web applications are natively supported via AXTree/DOM, native desktop applications without accessibility trees would require a hybrid multi-modal coordinate-grounding model.

### 5. What are the key assumptions made while building the solution?
* **Local Sandbox Network:** Assumed the target enterprise ERP is accessible locally (`http://127.0.0.1:8000`) or within an internal network/VPC without third-party CAPTCHAs.
* **Semi-Structured Document Inputs:** Assumed incoming vendor invoices arrive as JSON/PDF structured documents with identifiable key metadata (invoice number, vendor name, amount, purchase order reference).
* **Deterministic Policy Limits:** Assumed financial risk can be bounded by clear deterministic thresholds (e.g., transactions $\ge \$1,000$ mandate human authorization, whereas smaller amounts follow pre-approved operational workflows).

### 6. If you had another 2 weeks, what would you build/change next?
1. **Durable Task Orchestration:** Integrate **Temporal.io** or **DBOS** to make agent workflows durable, replayable, and horizontally scalable across distributed worker pools.
2. **Hybrid Vision Grounding:** Combine AXTree with multi-modal coordinate click/type capabilities to operate non-web legacy desktop applications.
3. **Graph-Based Organizational Memory:** Upgrade the persistent memory store into a combined Vector + Knowledge Graph store to index complex enterprise operating procedures.
4. **Sandboxed MicroVM Isolation:** Run browser sessions inside isolated microVMs (Firecracker / Docker) with strict egress filtering for SOC2/HIPAA enterprise compliance.
