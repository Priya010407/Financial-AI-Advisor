import json
import os
import re
import streamlit as st
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

# -------------------------------
# GEMINI API KEY
# -------------------------------

api_key = None

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# -------------------------------
# CLEAN AMOUNT
# -------------------------------

def clean_amount(value):

    try:

        if isinstance(value, (int, float)):
            return float(value)

        value = str(value)

        value = value.replace(",", "")
        value = value.replace("₹", "")
        value = value.replace("Rs.", "")
        value = value.replace("INR", "")
        value = value.strip()

        match = re.search(r"\d+(\.\d+)?", value)

        if match:
            return float(match.group())

    except:
        pass

    return 0.0


# -------------------------------
# PARSE RECEIPT
# -------------------------------

def parse_receipt(uploaded_file):

    try:

        image = Image.open(uploaded_file)

        prompt = """
You are an expert AI receipt analyzer.

The image may be:

- Google Pay
- PhonePe
- Paytm
- Amazon Pay
- Bank Receipt
- Shopping Receipt
- Restaurant Bill
- Grocery Bill

Return ONLY valid JSON.

{
"merchant":"",
"amount":0,
"category":"",
"date":"",
"payment_method":"",
"receipt_type":"",
"currency":"INR",
"confidence":95
}

IMPORTANT RULES

1. Amount MUST be FINAL PAID AMOUNT ONLY.
2. Ignore:
- UPI ID
- Transaction ID
- Reference Number
- Bank Balance
- Cashback
- Rewards
- Phone Numbers
- Account Numbers
3. Never combine digits.
4. Never guess.
5. Merchant should be business/shop name only.
6. Currency must be INR.
7. Payment Method:
UPI
Cash
Card
Net Banking
Wallet
8. Categories:
Food & Dining
Shopping
Groceries
Transportation
Medical
Entertainment
Utilities
Other

Return ONLY JSON.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                image
            ]
        )

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "")
            text = text.replace("```", "").strip()

        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        data = json.loads(text)

        amount = clean_amount(
            data.get("amount", 0)
        )

        data["amount"] = amount

        if amount == 0:

            # fallback extraction
            numbers = re.findall(
                r"\d+\.\d+|\d+",
                text
            )

            if numbers:

                try:
                    data["amount"] = max(
                        [float(x) for x in numbers]
                    )
                except:
                    pass

        data.setdefault(
            "merchant",
            "Unknown"
        )

        data.setdefault(
            "category",
            "Other"
        )

        data.setdefault(
            "date",
            ""
        )

        data.setdefault(
            "payment_method",
            "UPI"
        )

        data.setdefault(
            "receipt_type",
            "Digital Payment"
        )

        data.setdefault(
            "currency",
            "INR"
        )

        data.setdefault(
            "confidence",
            90
        )

        return data

    except Exception as e:

        return {

            "merchant": "Unknown",

            "amount": 0.0,

            "category": "Other",

            "date": "",

            "payment_method": "Unknown",

            "receipt_type": "Unknown",

            "currency": "INR",

            "confidence": 0,

            "error": str(e)

        }