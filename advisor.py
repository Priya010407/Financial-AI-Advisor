import streamlit as st
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

# -----------------------------------
# GEMINI API KEY
# -----------------------------------

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# -----------------------------------
# AI ADVICE
# -----------------------------------

def get_advice(merchant, category, amount, payment_method):

    try:

        prompt = f"""
You are a friendly personal finance coach.

Expense Details

Merchant: {merchant}
Category: {category}
Amount: ₹{amount}
Payment Method: {payment_method}

Write advice in simple English.

Rules:

- Maximum 4 short points.
- Use emojis.
- Mention the amount.
- Tell whether spending is Good, Average or High.
- Give one useful saving tip.
- End with one motivational sentence.
- No markdown.
- No JSON.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()

    except:

        if amount <= 500:
            level = "🟢 Good"
        elif amount <= 2000:
            level = "🟡 Average"
        else:
            level = "🔴 High"

        tips = {
            "Food & Dining": "🍔 Cooking at home a few times a week can save more money.",
            "Shopping": "🛍 Compare prices before buying and avoid impulse purchases.",
            "Groceries": "🛒 Prepare a shopping list before visiting the store.",
            "Transportation": "🚌 Use public transport or carpool when possible.",
            "Medical": "🏥 Health comes first. Keep medical bills safely.",
            "Entertainment": "🎬 Set a monthly entertainment budget.",
            "Utilities": "💡 Save electricity and water to reduce bills.",
            "Other": "💰 Track every expense to improve your savings."
        }

        return f"""
💸 You spent ₹{amount:.2f} at {merchant}.

{level} Spending Level

💡 {tips.get(category, tips["Other"])}

😊 Every small saving helps build a better financial future!
"""