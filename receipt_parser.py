import json
import os
import re
import streamlit as st
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

# Get API key from Streamlit Secrets first, then .env
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def clean_amount(value):
    """
    Convert Gemini amount into float safely
    """

    try:

        if isinstance(value, (int, float)):
            return float(value)

        value = str(value)

        value = value.replace(",", "")
        value = value.replace("₹", "")
        value = value.replace("Rs.", "")
        value = value.replace("INR", "")

        match = re.search(r"\d+(\.\d+)?", value)

        if match:
            return float(match.group())

    except:
        pass

    return 0.0


def parse_receipt(uploaded_file):

    try:

        image = Image.open(uploaded_file)

        prompt = """
You are an expert receipt analyzer.

Read this receipt or UPI payment screenshot carefully.

Return ONLY JSON.

{
"receipt_type":"",
"merchant":"",
"amount":0,
"category":"",
"date":"",
"payment_method":"",
"currency":"INR",
"confidence":95
}

IMPORTANT:

• Amount = FINAL PAID AMOUNT ONLY
• Never return transaction id
• Never return UPI id
• Never return account number
• Never return balance
• Never combine digits
• If amount is ₹521 return exactly 521
• Category:
Food & Dining
Shopping
Groceries
Transportation
Medical
Entertainment
Utilities
Other

Return JSON only.
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
            text = text.replace("```json", "").replace("```", "").strip()

        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        data = json.loads(text)

        data["amount"] = clean_amount(
            data.get("amount", 0)
        )

        if data["merchant"] == "":
            data["merchant"] = "Unknown"

        if data["category"] == "":
            data["category"] = "Other"

        if data["payment_method"] == "":
            data["payment_method"] = "Unknown"

        if data["currency"] == "":
            data["currency"] = "INR"

        return data

    except Exception as e:

        return {
            "receipt_type": "Other",
            "merchant": "Unknown",
            "amount": 0.0,
            "category": "Other",
            "date": "",
            "payment_method": "Unknown",
            "currency": "INR",
            "confidence": 0,
            "error": str(e)
        }