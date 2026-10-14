from calendar import monthrange
from datetime import date, timedelta

from db import get_db


# ---------- 1. Small helpers ----------

def money(amount):
    return "₹" + f"{round(amount):,}"


def total_between(db, start, end):
    row = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE date BETWEEN ? AND ?",
        (start.isoformat(), end.isoformat()),
    ).fetchone()
    return row["total"]


# ---------- 2. The function app.py calls ----------

def get_insights(today=None):
    today = today or date.today()
    db = get_db()
    try:
        this_start = today - timedelta(days=6)
        last_start = today - timedelta(days=13)
        last_end = today - timedelta(days=7)

        this_week = total_between(db, this_start, today)
        last_week = total_between(db, last_start, last_end)

        tips = []
        alert = None

        # --- Tip 1: this week compared with last week ---
        if last_week > 0:
            change = round((this_week - last_week) / last_week * 100)
            if change == 0:
                tips.append("Your spending is about the same as last week.")
            elif change > 0:
                tips.append(f"You spent {change}% more than last week ({money(this_week)} vs {money(last_week)}).")
            else:
                tips.append(f"You spent {abs(change)}% less than last week ({money(this_week)} vs {money(last_week)}).")
        elif this_week > 0:
            tips.append("There is no spending from last week to compare with yet.")

        if this_week > 0:
            # --- Tip 2: top category and a rough saving estimate ---
            top = db.execute(
                "SELECT category, SUM(amount) AS total FROM expenses "
                "WHERE date BETWEEN ? AND ? GROUP BY category ORDER BY total DESC LIMIT 1",
                (this_start.isoformat(), today.isoformat()),
            ).fetchone()
            top_name = top["category"] or "Others"
            top_total = top["total"]
            share = round(top_total / this_week * 100)

            if top_name == "Others":
                tips.append(
                    f"Most of your spending this week ({share}%) is uncategorized. "
                    "Adding clearer merchant names gives better insights."
                )
            else:
                tips.append(f"{top_name} is your top category this week: {money(top_total)} ({share}% of spending).")
                tips.append(
                    f"If you cut {top_name} spending by 20%, you could save about "
                    f"{money(top_total * 4 * 0.2)} a month (rough estimate based on this week)."
                )

            # --- Tip 3: biggest single expense ---
            count = db.execute(
                "SELECT COUNT(*) AS n FROM expenses WHERE date BETWEEN ? AND ?",
                (this_start.isoformat(), today.isoformat()),
            ).fetchone()["n"]
            if count >= 2:
                big = db.execute(
                    "SELECT merchant, amount FROM expenses WHERE date BETWEEN ? AND ? "
                    "ORDER BY amount DESC LIMIT 1",
                    (this_start.isoformat(), today.isoformat()),
                ).fetchone()
                where = f" at {big['merchant']}" if big["merchant"] else ""
                tips.append(f"Your biggest expense this week was {money(big['amount'])}{where}.")

            # --- Tip 4: daily average ---
            tips.append(f"You spent about {money(this_week / 7)} per day over the last 7 days.")

        # --- Tips 5 and 6: monthly budget ---
        month_key = today.strftime("%Y-%m")
        budget_row = db.execute("SELECT amount FROM budgets WHERE month = ?", (month_key,)).fetchone()

        if budget_row:
            budget = budget_row["amount"]
            days_in_month = monthrange(today.year, today.month)[1]
            month_start = today.replace(day=1)
            month_end = today.replace(day=days_in_month)
            spent = total_between(db, month_start, month_end)
            percent = round(spent / budget * 100)
            days_left = days_in_month - today.day

            if spent >= budget:
                if spent > budget:
                    alert = "You have gone over this month's budget."
                    tips.append(f"You are {money(spent - budget)} over this month's budget of {money(budget)}.")
                else:
                    alert = "You have used up this month's budget."
                    tips.append("You have used your whole budget for this month.")
            else:
                if percent >= 80:
                    alert = f"You have used {percent}% of this month's budget."
                remaining = budget - spent
                if days_left > 0:
                    tips.append(
                        f"You have {money(remaining)} left this month, "
                        f"about {money(remaining / days_left)} per day for the next {days_left} days."
                    )
                else:
                    tips.append(f"You have {money(remaining)} left of this month's budget.")

                if today.day >= 5 and spent > 0:
                    projected = spent / today.day * days_in_month
                    if projected > budget:
                        tips.append(
                            f"At this pace you would spend about {money(projected)} this month, "
                            f"which is over your {money(budget)} budget."
                        )

        return {
            "this_week": round(this_week, 2),
            "last_week": round(last_week, 2),
            "insights": tips,
            "alert": alert,
        }
    finally:
        db.close()