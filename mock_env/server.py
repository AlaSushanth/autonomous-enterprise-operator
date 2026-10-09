import json
import sqlite3
import os
from pathlib import Path
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="NexusERP - Enterprise Management Portal")

DB_PATH = Path(__file__).parent / "erp.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Purchase Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_orders (
            po_number TEXT PRIMARY KEY,
            vendor_name TEXT NOT NULL,
            allocated_amount REAL NOT NULL,
            status TEXT NOT NULL,
            payment_terms TEXT NOT NULL
        )
    """)
    # Invoices/Bills table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            po_number TEXT NOT NULL,
            vendor_name TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_terms TEXT NOT NULL,
            vendor_address TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (po_number) REFERENCES purchase_orders (po_number)
        )
    """)
    # Audit log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Seed sample POs if empty
    cursor.execute("SELECT COUNT(*) FROM purchase_orders")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO purchase_orders (po_number, vendor_name, allocated_amount, status, payment_terms)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("PO-108", "Acme Logistics Corp", 1000.0, "APPROVED", "Immediate"),
            ("PO-112", "MegaTech Cloud Services", 5000.0, "APPROVED", "Net-30"),
            ("PO-119", "Global Office Supplies", 450.0, "APPROVED", "Net-15"),
        ])
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NexusERP Enterprise Portal</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }
        .container { max-width: 900px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
        h1 { margin-top: 0; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; }
        .nav { display: flex; gap: 15px; margin-bottom: 20px; border-bottom: 1px solid #cbd5e1; padding-bottom: 10px; }
        .nav a { text-decoration: none; color: #2563eb; font-weight: 600; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: 600; margin-bottom: 5px; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        button { background: #2563eb; color: #fff; border: none; padding: 12px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 14px; }
        button:hover { background: #1d4ed8; }
        .alert { padding: 12px; border-radius: 6px; margin-bottom: 20px; }
        .alert-success { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
        .alert-error { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #e2e8f0; padding: 10px; text-align: left; }
        th { background: #f1f5f9; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-success { background: #bbf7d0; color: #15803d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/invoices/new">Submit Invoice</a>
            <a href="/invoices">View Completed Invoices</a>
            <a href="/purchase-orders">Purchase Orders</a>
        </div>
        {{ content | safe }}
    </div>
</body>
</html>
"""

from jinja2 import Template

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM invoices")
    inv_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM purchase_orders")
    po_count = c.fetchone()[0]
    conn.close()
    
    content = f"""
    <h1>NexusERP Operational Dashboard</h1>
    <p>Welcome to the Nexus Enterprise Resource Planning interface.</p>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
        <div style="padding: 20px; background: #eff6ff; border-radius: 8px;">
            <h3>Active Purchase Orders</h3>
            <p style="font-size: 28px; font-weight: bold; margin: 0;">{po_count}</p>
        </div>
        <div style="padding: 20px; background: #f0fdf4; border-radius: 8px;">
            <h3>Processed Invoices</h3>
            <p style="font-size: 28px; font-weight: bold; margin: 0;">{inv_count}</p>
        </div>
    </div>
    <div style="margin-top: 30px;">
        <a href="/invoices/new"><button id="btn-submit-invoice">Process New Invoice</button></a>
    </div>
    """
    return Template(HTML_TEMPLATE).render(content=content)

@app.get("/invoices/new", response_class=HTMLResponse)
async def new_invoice_form(error: str = None):
    error_banner = f'<div class="alert alert-error" id="error-banner">{error}</div>' if error else ""
    content = f"""
    <h1>Submit Vendor Invoice</h1>
    {error_banner}
    <form action="/invoices/submit" method="post" id="invoice-form">
        <div class="form-group">
            <label for="invoice_id">Invoice ID / Number *</label>
            <input type="text" id="invoice_id" name="invoice_id" placeholder="e.g. INV-9021" required>
        </div>
        <div class="form-group">
            <label for="po_number">Purchase Order (PO) Number *</label>
            <input type="text" id="po_number" name="po_number" placeholder="e.g. PO-108" required>
        </div>
        <div class="form-group">
            <label for="vendor_name">Vendor Name *</label>
            <input type="text" id="vendor_name" name="vendor_name" placeholder="e.g. Acme Logistics Corp" required>
        </div>
        <div class="form-group">
            <label for="amount">Invoice Total Amount ($) *</label>
            <input type="number" step="0.01" id="amount" name="amount" placeholder="e.g. 750.00" required>
        </div>
        <div class="form-group">
            <label for="payment_terms">Payment Terms</label>
            <select id="payment_terms" name="payment_terms">
                <option value="Immediate">Immediate</option>
                <option value="Net-15">Net-15</option>
                <option value="Net-30">Net-30</option>
                <option value="Net-60">Net-60</option>
            </select>
        </div>
        <!-- Dynamic field: requirement enforced on amounts > $1000 for realistic validation testing -->
        <div class="form-group" id="address-group">
            <label for="vendor_address">Vendor Physical / Remittance Address (Required for high-value bills)</label>
            <input type="text" id="vendor_address" name="vendor_address" placeholder="123 Business Way, Suite 400">
        </div>
        <button type="submit" id="submit-btn">Authorize & Post Invoice</button>
    </form>
    """
    return Template(HTML_TEMPLATE).render(content=content)

@app.post("/invoices/submit", response_class=HTMLResponse)
async def submit_invoice(
    invoice_id: str = Form(...),
    po_number: str = Form(...),
    vendor_name: str = Form(...),
    amount: float = Form(...),
    payment_terms: str = Form(...),
    vendor_address: str = Form("")
):
    # Dynamic business validation for testing self-healing
    if amount >= 1000.0 and not vendor_address.strip():
        return await new_invoice_form(error="Validation Error: High-value invoices ($1,000+) require a valid Vendor Physical Address.")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Verify PO exists
    c.execute("SELECT po_number, allocated_amount FROM purchase_orders WHERE po_number = ?", (po_number,))
    po = c.fetchone()
    if not po:
        conn.close()
        return await new_invoice_form(error=f"Rejection: Purchase Order '{po_number}' does not exist in ERP database.")
    
    try:
        c.execute("""
            INSERT INTO invoices (invoice_id, po_number, vendor_name, amount, payment_terms, vendor_address, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (invoice_id, po_number, vendor_name, amount, payment_terms, vendor_address, "SUBMITTED"))
        
        c.execute("""
            INSERT INTO audit_logs (action, details)
            VALUES (?, ?)
        """, ("INVOICE_CREATED", f"Invoice {invoice_id} for ${amount} created under {po_number}"))
        
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return await new_invoice_form(error=f"Duplicate Error: Invoice ID '{invoice_id}' already exists.")
    
    conn.close()
    
    content = f"""
    <div class="alert alert-success" id="confirmation-banner">
        <h2>✓ Invoice Successfully Posted & Authorized</h2>
        <p>Transaction Reference: <strong>REC-{invoice_id}</strong></p>
        <p>Vendor: <strong>{vendor_name}</strong> | Total: <strong>${amount:,.2f}</strong> | PO: <strong>{po_number}</strong></p>
        <p>Status: <span class="badge badge-success">POSTED</span></p>
    </div>
    <div style="margin-top: 20px;">
        <a href="/invoices"><button id="btn-view-all">View All Invoices</button></a>
        <a href="/invoices/new" style="margin-left: 10px;">Post Another Invoice</a>
    </div>
    """
    return Template(HTML_TEMPLATE).render(content=content)

@app.get("/invoices", response_class=HTMLResponse)
async def list_invoices():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT invoice_id, po_number, vendor_name, amount, payment_terms, status, created_at FROM invoices ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    
    table_rows = ""
    for r in rows:
        table_rows += f"""
        <tr>
            <td><strong>{r[0]}</strong></td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>${r[3]:,.2f}</td>
            <td>{r[4]}</td>
            <td><span class="badge badge-success">{r[5]}</span></td>
            <td>{r[6]}</td>
        </tr>
        """
    
    content = f"""
    <h1>Completed Invoices & Payments</h1>
    <table id="invoices-table">
        <thead>
            <tr>
                <th>Invoice ID</th>
                <th>PO #</th>
                <th>Vendor</th>
                <th>Amount</th>
                <th>Terms</th>
                <th>Status</th>
                <th>Timestamp</th>
            </tr>
        </thead>
        <tbody>
            {table_rows if table_rows else '<tr><td colspan="7">No invoices processed yet.</td></tr>'}
        </tbody>
    </table>
    <div style="margin-top: 20px;">
        <a href="/invoices/new"><button>+ New Invoice</button></a>
    </div>
    """
    return Template(HTML_TEMPLATE).render(content=content)

@app.get("/purchase-orders", response_class=HTMLResponse)
async def list_pos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT po_number, vendor_name, allocated_amount, status, payment_terms FROM purchase_orders")
    rows = c.fetchall()
    conn.close()
    
    table_rows = "".join([
        f"<tr><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>${r[2]:,.2f}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
        for r in rows
    ])
    
    content = f"""
    <h1>Company Purchase Orders</h1>
    <table id="po-table">
        <thead>
            <tr><th>PO Number</th><th>Vendor</th><th>Allocated Budget</th><th>Status</th><th>Standard Terms</th></tr>
        </thead>
        <tbody>{table_rows}</tbody>
    </table>
    """
    return Template(HTML_TEMPLATE).render(content=content)

# API Endpoint for Verification and Querying
@app.get("/api/invoices/{invoice_id}")
async def get_invoice_api(invoice_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT invoice_id, po_number, vendor_name, amount, payment_terms, vendor_address, status FROM invoices WHERE invoice_id = ?", (invoice_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {
        "invoice_id": row[0],
        "po_number": row[1],
        "vendor_name": row[2],
        "amount": row[3],
        "payment_terms": row[4],
        "vendor_address": row[5],
        "status": row[6]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
