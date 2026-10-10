from datetime import date

from flask import Flask, jsonify, request
from flask_cors import CORS

from categorizer import categorize
from db import get_db, init_db
from insights import get_insights
from sms_parser import parse_sms

app = Flask(__name__)
CORS(app)
init_db()


def save_expense(data):
    category = data.get("category") or categorize(
        data.get("merchant", ""), data.get("description", "")
    )
    db = get_db()
    cur = db.execute(
        "INSERT INTO expenses (amount, merchant, category, payment_mode, description, date) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            data["amount"],
            data.get("merchant", ""),
            category,
            data.get("payment_mode", "Other"),
            data.get("description", ""),
            data.get("date") or date.today().isoformat(),
        ),
    )
    db.commit()
    new_id = cur.lastrowid
    db.close()
    return {"id": new_id, "category": category}


@app.get("/")
def home():
    return "WalletWise backend is running!"


@app.post("/api/expense")
def add_expense():
    data = request.get_json(silent=True) or {}
    try:
        data["amount"] = float(data.get("amount", 0))
    except (TypeError, ValueError):
        data["amount"] = 0
    if data["amount"] <= 0:
        return jsonify(error="A valid amount is required"), 400
    result = save_expense(data)
    return jsonify(result), 201


@app.get("/api/expenses")
def list_expenses():
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    category = request.args.get("category")
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    if category:
        query += " AND category = ?"
        params.append(category)
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)

    query += " ORDER BY date DESC, id DESC"

    db = get_db()
    rows = db.execute(query, params).fetchall()
    db.close()
    return jsonify([dict(row) for row in rows])


@app.delete("/api/expense/<int:expense_id>")
def delete_expense(expense_id):
    db = get_db()
    cur = db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    deleted = cur.rowcount
    db.close()
    if deleted == 0:
        return jsonify(error="Expense not found"), 404
    return jsonify(deleted=expense_id)


@app.post("/api/budget")
def set_budget():
    data = request.get_json(silent=True) or {}
    month = data.get("month")
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        amount = 0
    if not month or amount <= 0:
        return jsonify(error="Month (like 2026-10) and a positive amount are required"), 400

    db = get_db()
    db.execute("INSERT OR REPLACE INTO budgets (month, amount) VALUES (?, ?)", (month, amount))
    db.commit()
    db.close()
    return jsonify(month=month, amount=amount)


@app.get("/api/budget")
def get_budget():
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    db = get_db()
    row = db.execute("SELECT amount FROM budgets WHERE month = ?", (month,)).fetchone()
    db.close()
    return jsonify(month=month, amount=row["amount"] if row else None)


@app.get("/api/summary")
def summary():
    db = get_db()
    rows = db.execute(
        "SELECT category, ROUND(SUM(amount), 2) AS total "
        "FROM expenses GROUP BY category ORDER BY total DESC"
    ).fetchall()
    db.close()
    by_category = [dict(row) for row in rows]
    total = round(sum(item["total"] for item in by_category), 2)
    return jsonify(total=total, by_category=by_category)


@app.post("/api/parse-sms")
def parse_and_save():
    data = request.get_json(silent=True) or {}
    sms = data.get("sms", "")
    parsed = parse_sms(sms)
    if not parsed:
        return jsonify(error="Couldn't read an expense from this message"), 422
    saved = save_expense(parsed)
    return jsonify({**parsed, **saved}), 201


@app.get("/api/insights")
def insights():
    return jsonify(get_insights())


if __name__ == "__main__":
    app.run(debug=True)