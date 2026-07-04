import streamlit as st
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def get_advice(merchant, category, amount, payment_method):

    try:

        prompt = f"""
You are a friendly personal finance coach.

Expense Details

Merchant: {merchant}
Category: {category}
Amount: ₹{amount}
Payment Method: {payment_method}

Write advice for a normal person.

Rules:

- Maximum 4 short points.
- Use very simple English.
- Use emojis.
- Mention the amount.
- Tell whether spending is Good, Average or High.
- Give one money-saving tip.
- End with one positive sentence.
- Never use difficult financial words.
- Don't use markdown.
- Don't return JSON.

Example style:

🍔 You spent ₹450 on food.

🟢 Spending Level: Good

💡 Tip:
Cooking at home a few times a week can save more money.

😊 Keep tracking your expenses. Every small saving matters!

Only return the advice.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()

    except:

        # Offline fallback (works even if Gemini fails)

        if amount <= 500:

            level = "🟢 Good"

        elif amount <= 2000:

            level = "🟡 Average"

        else:

            level = "🔴 High"

        tips = {

            "Food & Dining":
            "🍔 Try cooking at home more often to save money.",

            "Shopping":
            "🛍 Buy only what you really need and compare prices first.",

            "Groceries":
            "🛒 Making a shopping list helps avoid unnecessary purchases.",

            "Transportation":
            "🚗 Using public transport sometimes can reduce travel costs.",

            "Medical":
            "🏥 Health is important. Keep all medical bills for future reference.",

            "Entertainment":
            "🎬 Set a monthly entertainment budget to avoid overspending.",

            "Utilities":
            "💡 Saving electricity and water can lower your monthly bills.",

            "Other":
            "💰 Track your daily expenses regularly to save more money."

        }

        return f"""
You spent ₹{amount:.2f} at {merchant}.

Spending Level: {level}

Tip:
{tips.get(category, tips["Other"])}

Keep tracking your expenses. Small savings become big savings over time.
"""