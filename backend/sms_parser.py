import re
from datetime import date

# ---------- 1. Patterns (the "search rules") ----------

AMOUNT_PATTERN = re.compile(
    r"(?:(?<![A-Za-z])(?:rs\.?|inr)|₹)\s*([\d,]+(?:\.\d{1,2})?)",
    re.IGNORECASE,
)

NUMERIC_DATE = re.compile(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})\b")

NAMED_DATE = re.compile(
    r"\b(\d{1,2})[-\s]([A-Za-z]{3})[A-Za-z]*[-\s,]+(\d{2,4})\b"
)

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

MERCHANT_PATTERN = re.compile(
    r"\b(?:to|at)\s+(?:VPA\s+)?(.+?)"
    r"(?=\s+(?:on|via|using|ref|from|for)\b|\s*\(|[,;]|\.(?:\s|$)|$)",
    re.IGNORECASE,
)

INCOMING = re.compile(r"\b(credited|received|deposited|refund(?:ed)?|cashback)\b", re.IGNORECASE)
OUTGOING = re.compile(r"\b(debited|spent|paid|sent|purchase[d]?|withdrawn|payment)\b", re.IGNORECASE)


# ---------- 2. Small helper functions ----------

def find_amount(text):
    match = AMOUNT_PATTERN.search(text)
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:
        return None


def find_date(text):
    day = month = year = None

    match = NUMERIC_DATE.search(text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
    else:
        match = NAMED_DATE.search(text)
        if match:
            day = int(match.group(1))
            month = MONTHS.get(match.group(2).lower())
            year = int(match.group(3))

    if day is None or month is None:
        return date.today().isoformat()

    if year < 100:
        year += 2000

    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return date.today().isoformat()


def find_merchant(text):
    match = MERCHANT_PATTERN.search(text)
    if not match:
        return "Unknown"

    name = match.group(1).strip()
    name = name.split("@")[0]
    name = re.sub(r"\.(com|in|co|net|org)\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[_\-.]+", " ", name).strip()

    if not name:
        return "Unknown"
    if name.replace(" ", "").isdigit():
        return "UPI Contact"
    return name.title()


def find_payment_mode(text):
    lowered = text.lower()
    if "upi" in lowered or "vpa" in lowered or "@" in lowered:
        return "UPI"
    if "card" in lowered:
        return "Card"
    if "atm" in lowered or "cash" in lowered:
        return "Cash"
    return "Other"


# ---------- 3. The main function app.py calls ----------

def parse_sms(text):
    if not text or not text.strip():
        return None

    text = " ".join(text.split())

    if INCOMING.search(text) and not OUTGOING.search(text):
        return None

    amount = find_amount(text)
    if amount is None or amount <= 0:
        return None

    return {
        "amount": amount,
        "merchant": find_merchant(text),
        "date": find_date(text),
        "payment_mode": find_payment_mode(text),
    }