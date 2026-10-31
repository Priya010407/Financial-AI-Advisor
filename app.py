```python
import streamlit as st
import pandas as pd
import plotly.express as px
import re

import auth

from database import (
    create_database,
    save_expense,
    get_expenses,
    get_expenses_df,
    delete_expense,
    clear_expenses
)

from receipt_parser import parse_receipt
from advisor import get_advice
from budget import get_budget
from export import export_to_excel, export_to_pdf
from voice_parser import (
    transcribe_audio_file,
    parse_voice_expense
)

# -------------------------------------
# PAGE CONFIG
# -------------------------------------

st.set_page_config(
    page_title="Financial AI Advisor",
    page_icon="💰",
    layout="wide"
)

# -------------------------------------
# DATABASE
# -------------------------------------

create_database()

# -------------------------------------
# AMOUNT HELPER
# -------------------------------------

def clean_amount(value):

    if value is None:
        return 0.0

    text = str(value)

    text = text.replace(",", "")
    text = text.replace("₹", "")
    text = text.replace("INR", "")
    text = text.replace("Rs.", "")
    text = text.strip()

    match = re.search(r'\d+(?:\.\d{1,2})?', text)

    if match:
        return float(match.group())

    return 0.0


# -------------------------------------
# SESSION
# -------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# -------------------------------------
# LOGIN / SIGNUP
# -------------------------------------

if not st.session_state.logged_in:

    st.title("💰 Financial AI Advisor")

    tab1, tab2 = st.tabs(
        ["🔑 Login", "📝 Sign Up"]
    )

    with tab1:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):

            user = auth.login_user(email, password)

            if user:

                st.session_state.logged_in = True
                st.session_state.user = user

                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid Email or Password")

    with tab2:

        name = st.text_input(
            "Full Name",
            key="signup_name"
        )

        new_email = st.text_input(
            "Email",
            key="signup_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        if st.button("Create Account", use_container_width=True):

            ok = auth.register_user(
                name,
                new_email,
                new_password
            )

            if ok:
                st.success("Account Created")

            else:
                st.error("Email already exists")

    st.stop()


# -------------------------------------
# CURRENT USER
# -------------------------------------

user_id = st.session_state.user[0]
user_name = st.session_state.user[1]


# -------------------------------------
# SIDEBAR
# -------------------------------------

st.sidebar.title("💰 Financial AI Advisor")

st.sidebar.success(f"Welcome {user_name}")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🧾 Receipt Scanner",
        "🎤 Voice Expense",
        "📋 Expense History",
        "📊 Analytics",
        "📤 Export"
    ]
)

st.sidebar.markdown("---")

if st.sidebar.button("🗑 Clear My History"):

    clear_expenses(user_id)

    st.success("History Cleared")
    st.rerun()

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False
    st.session_state.user = None

    st.rerun()


# -------------------------------------
# LOAD USER DATA
# -------------------------------------

df = get_expenses_df(user_id)


# -------------------------------------
# DASHBOARD
# -------------------------------------

if menu == "🏠 Dashboard":

    st.title("📊 Financial Dashboard")

    if df.empty:

        st.info("No Expenses Found")

    else:

        total = df["amount"].sum()
        highest = df["amount"].max()
        average = df["amount"].mean()
        transactions = len(df)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Expense", f"₹{total:.2f}")
        c2.metric("Transactions", transactions)
        c3.metric("Highest", f"₹{highest:.2f}")
        c4.metric("Average", f"₹{average:.2f}")

        st.divider()

        category_df = (
            df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        col1, col2 = st.columns(2)

        with col1:

            fig = px.pie(
                category_df,
                names="category",
                values="amount",
                hole=0.45
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            fig2 = px.bar(
                category_df,
                x="category",
                y="amount",
                text="amount"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        st.divider()

        st.subheader("Budget Status")

        for _, row in category_df.iterrows():

            limit = get_budget(row["category"])

            st.write(row["category"])

            if limit and float(limit) > 0:

                st.progress(
                    min(float(row["amount"]) / float(limit), 1.0)
                )

                st.caption(
                    f"₹{row['amount']:.2f} / ₹{limit}"
                )


# -------------------------------------
# RECEIPT SCANNER
# -------------------------------------

elif menu == "🧾 Receipt Scanner":

    st.title("🧾 AI Receipt Scanner")

    uploaded_file = st.file_uploader(
        "Upload Receipt / GPay Screenshot",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(
                uploaded_file,
                use_container_width=True
            )

        with col2:

            with st.spinner("Analyzing Receipt..."):

                receipt = parse_receipt(uploaded_file)

            merchant = receipt.get("merchant", "Unknown")

            # Extract detected amount
            detected_amount = clean_amount(
                receipt.get("amount", 0)
            )

            category = receipt.get("category", "Other")
            receipt_date = receipt.get("date", "")
            payment_method = receipt.get("payment_method", "UPI")
            receipt_type = receipt.get("receipt_type", "Other")
            currency = receipt.get("currency", "INR")

            try:
                confidence = int(receipt.get("confidence", 0))
            except:
                confidence = 0

            confidence = max(0, min(confidence, 100))

            st.success("Receipt Analyzed Successfully")

            st.write(f"### 🏪 Merchant: {merchant}")

            # ---------------------------------
            # AMOUNT CORRECTION
            # ---------------------------------

            st.write(
                f"Detected Amount: ₹{detected_amount:.2f}"
            )

            if detected_amount <= 0:

                st.warning(
                    "Amount could not be detected correctly. "
                    "Please enter the transaction amount manually."
                )

            amount = st.number_input(
                "💰 Verify / Correct Transaction Amount (₹)",
                min_value=0.0,
                value=float(detected_amount),
                step=1.0,
                format="%.2f",
                key="correct_receipt_amount"
            )

            st.write(f"### 📂 Category: {category}")
            st.write(f"### 💳 Payment: {payment_method}")
            st.write(f"### 📅 Date: {receipt_date}")

            st.progress(confidence / 100)

            # ---------------------------------
            # AI ADVICE
            # ---------------------------------

            if amount > 0:

                advice = get_advice(
                    merchant,
                    category,
                    amount,
                    payment_method
                )

                st.divider()

                st.subheader("🤖 AI Financial Advice")

                st.info(advice)

                # ---------------------------------
                # BUDGET
                # ---------------------------------

                budget = get_budget(category)

                st.metric(
                    "Recommended Budget",
                    f"₹{budget}"
                )

                # ---------------------------------
                # SAVE EXPENSE
                # ---------------------------------

                if st.button(
                    "💾 Save Expense",
                    use_container_width=True
                ):

                    save_expense(
                        user_id,
                        merchant,
                        amount,
                        category,
                        receipt_date,
                        payment_method,
                        receipt_type,
                        currency,
                        confidence,
                        advice
                    )

                    st.success("Expense Saved Successfully")
                    st.rerun()

            else:

                st.error(
                    "Please enter a valid transaction amount before saving."
                )


# -------------------------------------
# VOICE EXPENSE
# -------------------------------------

elif menu == "🎤 Voice Expense":

    st.title("🎤 Voice Expense")

    audio_file = st.file_uploader(
        "Upload WAV File",
        type=["wav"]
    )

    if audio_file:

        result = transcribe_audio_file(audio_file)

        if result["status"] == "success":

            st.success(result["text"])

            expense = parse_voice_expense(result["text"])

            amount = clean_amount(expense["amount"])
            category = expense["category"]

            st.metric("Amount", f"₹{amount:.2f}")

            st.write("Category:", category)

            if st.button(
                "Save Voice Expense",
                use_container_width=True
            ):

                advice = get_advice(
                    "Voice Expense",
                    category,
                    amount,
                    "Voice"
                )

                save_expense(
                    user_id,
                    "Voice Expense",
                    amount,
                    category,
                    "",
                    "Voice",
                    "Voice",
                    "INR",
                    100,
                    advice
                )

                st.success("Expense Saved")
                st.rerun()

        else:

            st.error(result["text"])


# -------------------------------------
# EXPENSE HISTORY
# -------------------------------------

elif menu == "📋 Expense History":

    st.title("📋 Expense History")

    df = get_expenses_df(user_id)

    if df.empty:

        st.info("No Expenses Found")

    else:

        search = st.text_input("🔍 Search Merchant")

        if search:

            df = df[
                df["merchant"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            df,
            use_container_width=True
        )

        st.divider()

        st.subheader("Delete Expense")

        expense_id = st.number_input(
            "Expense ID",
            min_value=1,
            step=1
        )

        if st.button(
            "🗑 Delete Expense",
            use_container_width=True
        ):

            delete_expense(
                user_id,
                expense_id
            )

            st.success("Expense Deleted")
            st.rerun()


# -------------------------------------
# ANALYTICS
# -------------------------------------

elif menu == "📊 Analytics":

    st.title("📊 Expense Analytics")

    df = get_expenses_df(user_id)

    if df.empty:

        st.warning("No Expenses Found")

    else:

        st.subheader("Category Wise Spending")

        category_df = (
            df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            category_df,
            x="category",
            y="amount",
            text="amount"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

        st.subheader("Expense Distribution")

        pie = px.pie(
            category_df,
            names="category",
            values="amount",
            hole=0.45
        )

        st.plotly_chart(
            pie,
            use_container_width=True
        )

        st.divider()

        if "receipt_date" in df.columns:

            timeline = (
                df.groupby("receipt_date")["amount"]
                .sum()
                .reset_index()
            )

            if not timeline.empty:

                st.subheader("Expense Timeline")

                fig2 = px.line(
                    timeline,
                    x="receipt_date",
                    y="amount",
                    markers=True
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

        st.divider()

        merchant_df = (
            df.groupby("merchant")["amount"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )

        st.subheader("Top 5 Merchants")

        fig3 = px.bar(
            merchant_df,
            x="merchant",
            y="amount",
            text="amount"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )


# -------------------------------------
# EXPORT
# -------------------------------------

elif menu == "📤 Export":

    st.title("📤 Export Your Expenses")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📊 Export Excel",
            use_container_width=True
        ):

            file = export_to_excel(user_id)

            with open(file, "rb") as f:

                st.download_button(
                    "⬇ Download Excel",
                    data=f,
                    file_name="expenses.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    with col2:

        if st.button(
            "📄 Export PDF",
            use_container_width=True
        ):

            file = export_to_pdf(user_id)

            with open(file, "rb") as f:

                st.download_button(
                    "⬇ Download PDF",
                    data=f,
                    file_name="expenses.pdf",
                    mime="application/pdf"
                )


# -------------------------------------
# FOOTER
# -------------------------------------

st.markdown("---")

st.caption(
    "💰 Financial AI Advisor | AI Powered Expense Tracker | Gemini 2.5 Flash"
)
```
