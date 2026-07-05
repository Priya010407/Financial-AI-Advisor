import json
import os
import re

import streamlit as st
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

# ------------------------------------
# GEMINI API KEY
# ------------------------------------

api_key = None

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("GEMINI_API_KEY not found.")

client = genai.Client(api_key=api_key)


# ------------------------------------
# CLEAN AMOUNT
# ------------------------------------

def clean_amount(value):

    if value is None:
        return 0.0

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

    return 0.0


# ------------------------------------
# PARSE RECEIPT
# ------------------------------------

def parse_receipt(uploaded_file):

    try:

        image = Image.open(uploaded_file)

        prompt = """
You are an expert OCR AI.

Read this receipt or payment screenshot carefully.

The image may be from:
- Google Pay
- PhonePe
- Paytm
- Amazon Pay
- Bank App
- Shopping Receipt
- Restaurant Bill

Return ONLY valid JSON.

{
    "merchant":"",
    "amount":0,
    "category":"",
    "date":"",
    "payment_method":"",
    "receipt_type":"",
    "currency":"INR",
    "confidence":100
}

IMPORTANT:

1. Amount = BIGGEST payment amount shown with ₹.
2. Ignore:
   - UPI ID
   - Transaction ID
   - Google Transaction ID
   - Account Number
   - Phone Number
   - Rewards
   - Cashback
   - Balance
3. Merchant = receiver name only.
4. amount MUST be numeric.
5. Currency = INR.
6. Payment Method:
   - UPI
   - Card
   - Cash
   - Wallet
   - Net Banking
7. Categories:
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

        print("\n========== GEMINI RESPONSE ==========")
        print(response.text)
        print("=====================================\n")

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        # Extract JSON if Gemini adds extra text

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            text = match.group()

        data = json.loads(text)

        amount = clean_amount(data.get("amount"))

        # Backup amount detection

        if amount == 0:

            all_numbers = re.findall(
                r"₹?\s?(\d+(?:\.\d+)?)",
                text
            )

            if all_numbers:

                amount = max(
                    [float(x) for x in all_numbers]
                )

        data["amount"] = amount

        if not data.get("merchant"):
            data["merchant"] = "Unknown"

        if not data.get("category"):
            data["category"] = "Other"

        if not data.get("date"):
            data["date"] = ""

        if not data.get("payment_method"):
            data["payment_method"] = "UPI"

        if not data.get("receipt_type"):
            data["receipt_type"] = "Digital Payment"

        if not data.get("currency"):
            data["currency"] = "INR"

        if not data.get("confidence"):
            data["confidence"] = 90

        return data

    except Exception as e:

        print("Receipt Parser Error:", e)

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