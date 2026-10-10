from db import init_db, get_db

init_db()                      # create the tables
db = get_db()                  # open the database

# add one test expense
db.execute(
    "INSERT INTO expenses (amount, merchant, category, payment_mode, description, date) "
    "VALUES (?, ?, ?, ?, ?, ?)",
    (250, "Zomato", "Food", "UPI", "test", "2026-10-05"),
)
db.commit()

# read all expenses back
rows = db.execute("SELECT * FROM expenses").fetchall()
for row in rows:
    print(dict(row))

# remove the test row so your database stays clean
db.execute("DELETE FROM expenses WHERE description = 'test'")
db.commit()
db.close()
print("Database test finished.")