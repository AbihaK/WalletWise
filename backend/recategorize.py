from categorizer import categorize
from db import get_db, init_db

init_db()
db = get_db()

rows = db.execute(
    "SELECT id, merchant, description FROM expenses "
    "WHERE category = 'Others' OR category IS NULL OR category = ''"
).fetchall()

updated = 0
for row in rows:
    new_category = categorize(row["merchant"], row["description"])
    if new_category != "Others":
        db.execute("UPDATE expenses SET category = ? WHERE id = ?", (new_category, row["id"]))
        updated += 1

db.commit()
db.close()
print(f"Checked {len(rows)} uncategorized expenses, updated {updated}.")