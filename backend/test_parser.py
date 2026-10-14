from sms_parser import parse_sms

tests = [
    "Rs.250.00 debited from A/c XX1234 on 05-10-26 to VPA zomato@icici (UPI Ref 123456789).",
    "Paid Rs 120 to Uber on 06/10/2026 via UPI.",
    "INR 499.00 spent at AMAZON on 07-10-2026.",
    "Rs.5000 credited to your account on 01-10-26.",
    "Rs 1,250.50 paid to Swiggy Instamart on 08-Oct-2026 using UPI",
    "Rs.80 debited to VPA 9876543210@ybl on 09-10-26",
    "Thank you for shopping! Hello there",
    "Rs 45 sent to chai_wala@paytm on 10/10/26. Avl bal Rs 4,500.00",
    "",
    "Rs 0 paid to Test on 01-01-26",
    "Rs 300 paid to amazon.in on 31-02-2026 via UPI",
    "₹75 paid to Metro Card on 5 Oct 2026",
    "Your a/c debited Rs.999 at NETFLIX.COM. Ref 12345",
    "Refund of Rs 200 received from Myntra on 02-10-26",
]

for message in tests:
    print(repr(message[:60]))
    print("   ->", parse_sms(message))