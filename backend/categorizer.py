import re

# ---------- 1. The rules: category -> keywords ----------
# Categories are checked from top to bottom, and the first match wins.
# Specific categories go first (e.g. "amazon prime" must be checked
# before the general word "amazon").

RULES = {
    "Subscriptions": [
        "netflix", "spotify", "hotstar", "disney", "prime video", "amazon prime",
        "youtube", "jiosaavn", "zee5", "sonyliv", "sony liv", "icloud",
        "apple music", "google one", "canva", "chatgpt", "subscription",
    ],
    "Entertainment": [
        "bookmyshow", "pvr", "inox", "cinepolis", "cinema", "movie", "movies",
        "concert", "gaming", "steam", "playstation", "xbox", "arcade",
        "bowling", "amusement", "water park", "zoo",
    ],
    "Food": [
        "zomato", "swiggy", "uber eats", "dominos", "domino's", "pizza",
        "mcdonald", "mcdonald's", "kfc", "burger", "subway", "cafe", "starbucks",
        "canteen", "mess", "restaurant", "dhaba", "biryani", "chai", "tea",
        "coffee", "bakery", "haldiram", "sweets", "juice", "ice cream", "momos",
        "snacks", "tiffin", "food", "blinkit", "zepto", "instamart", "bigbasket",
        "grocery", "vegetables", "fruits", "milk",
    ],
    "Travel": [
        "uber", "ola", "rapido", "metro", "dmrc", "irctc", "redbus", "railway",
        "railways", "bus", "cab", "taxi", "auto", "rickshaw", "fuel", "petrol",
        "diesel", "fastag", "makemytrip", "goibibo", "indigo", "air india",
        "parking",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "meesho", "nykaa", "decathlon",
        "zudio", "lifestyle", "shoppers stop", "westside", "croma", "mall",
        "clothes", "shoes", "fashion",
    ],
    "Education": [
        "xerox", "photocopy", "stationery", "stationary", "print", "printing",
        "printout", "udemy", "coursera", "unacademy", "byju", "nptel", "book",
        "books", "bookstore", "college", "tuition", "library", "exam", "course",
        "notebook",
    ],
    "Health": [
        "pharmacy", "medical", "medicine", "medicines", "apollo", "1mg",
        "pharmeasy", "netmeds", "medplus", "hospital", "clinic", "doctor",
        "gym", "cult fit", "cultfit", "fitness", "dental", "diagnostic",
        "practo",
    ],
    "Bills": [
        "recharge", "jio", "airtel", "vodafone", "bsnl", "electricity", "bill",
        "broadband", "wifi", "postpaid", "prepaid", "dth", "tata play", "gas",
        "rent", "hostel",
    ],
}


# ---------- 2. Turn each keyword list into one search pattern ----------

def build_patterns():
    patterns = []
    for category, keywords in RULES.items():
        escaped = [re.escape(word) for word in keywords]
        pattern = re.compile(r"\b(?:" + "|".join(escaped) + r")\b", re.IGNORECASE)
        patterns.append((category, pattern))
    return patterns


PATTERNS = build_patterns()


# ---------- 3. The function app.py calls ----------

def categorize(merchant, description=""):
    text = f"{merchant or ''} {description or ''}"
    text = " ".join(text.split())

    if not text:
        return "Others"

    for category, pattern in PATTERNS:
        if pattern.search(text):
            return category

    return "Others"