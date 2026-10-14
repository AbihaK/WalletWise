from datetime import date, timedelta

from categorizer import categorize
from db import get_db, init_db

# (days ago, amount, merchant, payment mode)  -- all made-up demo data
SAMPLE = [
    (0, 180, "Zomato", "UPI"), (0, 40, "Metro Card", "Card"),
    (1, 60, "Chai Wala", "UPI"), (1, 250, "College Canteen", "Cash"),
    (2, 120, "Uber", "UPI"), (2, 799, "Myntra", "UPI"),
    (3, 90, "Xerox Shop", "Cash"), (3, 210, "Swiggy", "UPI"),
    (4, 149, "Netflix", "UPI"), (4, 35, "Rapido", "UPI"),
    (5, 320, "Starbucks", "UPI"), (5, 80, "Chai Wala", "Cash"),
    (6, 450, "Amazon", "UPI"), (6, 55, "Metro Card", "Card"),
    (7, 140, "Zomato", "UPI"), (8, 70, "Uber", "UPI"),
    (8, 100, "College Canteen", "Cash"), (9, 399, "Jio Recharge", "UPI"),
    (10, 160, "Swiggy", "UPI"), (10, 45, "Rapido", "UPI"),
    (11, 220, "Apollo Pharmacy", "UPI"), (12, 85, "Chai Wala", "Cash"),
    (13, 300, "BookMyShow", "UPI"), (13, 130, "Zomato", "UPI"),
]

init_db()
db = get_db()
db.execute("DELETE FROM expenses")
db.execute("DELETE FROM budgets")

today = date.today()
for days_ago, amount, merchant, mode in SAMPLE:
    day = (today - timedelta(days=days_ago)).isoformat()
    db.execute(
        "INSERT INTO expenses (amount, merchant, category, payment_mode, description, date) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (amount, merchant, categorize(merchant), mode, "", day),
    )

db.execute("INSERT INTO budgets (month, amount) VALUES (?, ?)", (today.strftime("%Y-%m"), 6000))
db.commit()
db.close()
print(f"Loaded {len(SAMPLE)} sample expenses and a budget of 6000 for {today.strftime('%Y-%m')}.")