import re


def extract_amount(text):
    """
    Extract the actual payment amount from receipt text.
    Ignores UPI IDs, phone numbers, invoice numbers, etc.
    """

    patterns = [

        r"total\s*[:\-]?\s*₹?\s*([\d,]+\.?\d*)",

        r"amount\s*[:\-]?\s*₹?\s*([\d,]+\.?\d*)",

        r"paid\s*[:\-]?\s*₹?\s*([\d,]+\.?\d*)",

        r"net amount\s*[:\-]?\s*₹?\s*([\d,]+\.?\d*)",

        r"grand total\s*[:\-]?\s*₹?\s*([\d,]+\.?\d*)",

        r"₹\s*([\d,]+\.?\d*)"

    ]

    text = text.lower()

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            amount = match.group(1)

            amount = amount.replace(",", "")

            try:
                return float(amount)
            except:
                pass

    return 0.0