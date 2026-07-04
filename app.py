import streamlit as st
import pandas as pd
import plotly.express as px

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

# ----------------------------------------------------
# DATABASE
# ----------------------------------------------------

create_database()

# ----------------------------------------------------
# PAGE
# ----------------------------------------------------

st.set_page_config(
    page_title="Financial AI Advisor",
    page_icon="💰",
    layout="wide"
)

# ----------------------------------------------------
# SESSION
# ----------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

# ----------------------------------------------------
# LOGIN
# ----------------------------------------------------

if not st.session_state.logged_in:

    st.title("💰 Financial AI Advisor")

    st.caption("AI Powered Expense Tracker")

    login_tab, signup_tab = st.tabs(
        [
            "🔑 Login",
            "📝 Sign Up"
        ]
    )

    # ---------------- LOGIN ----------------

    with login_tab:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True,
            key="login_btn"
        ):

            user = auth.login_user(
                email,
                password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.user = user

                st.success("Login Successful")

                st.rerun()

            else:

                st.error(
                    "Invalid Email or Password"
                )

    # ---------------- SIGNUP ----------------

    with signup_tab:

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

        if st.button(
            "Create Account",
            use_container_width=True,
            key="signup_btn"
        ):

            ok = auth.register_user(
                name,
                new_email,
                new_password
            )

            if ok:

                st.success(
                    "Account Created Successfully"
                )

            else:

                st.error(
                    "Email already exists"
                )

    st.stop()

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------

st.sidebar.title("💰 Financial AI Advisor")

st.sidebar.success(
    f"Welcome {st.session_state.user[1]}"
)

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

if st.sidebar.button("🗑 Clear History"):

    clear_expenses()

    st.success("History Cleared")

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False

    st.session_state.user = None

    st.rerun()

# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------

df = get_expenses_df()

# ----------------------------------------------------
# DASHBOARD
# ----------------------------------------------------

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

        c1.metric(
            "Total Expense",
            f"₹{total:.2f}"
        )

        c2.metric(
            "Transactions",
            transactions
        )

        c3.metric(
            "Highest Expense",
            f"₹{highest:.2f}"
        )

        c4.metric(
            "Average",
            f"₹{average:.2f}"
        )

        st.divider()

        st.subheader("Budget Status")

        category_df = (

            df.groupby("category")["amount"]

            .sum()

            .reset_index()

        )

        for _, row in category_df.iterrows():

            limit = get_budget(
                row["category"]
            )

            st.write(
                f"**{row['category']}**"
            )

            st.progress(
                min(row["amount"]/limit,1.0)
            )

            st.caption(
                f"₹{row['amount']:.2f} / ₹{limit}"
            )

        st.divider()

        col1,col2 = st.columns(2)

        with col1:

            st.subheader("Expense Distribution")

            fig = px.pie(
                category_df,
                names="category",
                values="amount",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            st.subheader("Category Spending")

            fig2 = px.bar(
                category_df,
                x="category",
                y="amount"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

            # ----------------------------------------------------
# RECEIPT SCANNER
# ----------------------------------------------------

elif menu == "🧾 Receipt Scanner":

    st.title("🧾 AI Receipt Scanner")

    uploaded_file = st.file_uploader(
        "Upload Receipt",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:

        col1, col2 = st.columns([1,2])

        with col1:

            st.image(
                uploaded_file,
                use_container_width=True
            )

        with col2:

            with st.spinner("Analyzing Receipt..."):

                receipt = parse_receipt(uploaded_file)

            merchant = receipt.get("merchant","Unknown")

            amount = float(
                receipt.get("amount",0)
            )

            category = receipt.get(
                "category",
                "Other"
            )

            receipt_date = receipt.get(
                "date",
                ""
            )

            payment_method = receipt.get(
                "payment_method",
                "Unknown"
            )

            receipt_type = receipt.get(
                "receipt_type",
                "Other"
            )

            currency = receipt.get(
                "currency",
                "INR"
            )

            confidence = receipt.get(
                "confidence",
                0
            )

            st.success("Receipt Successfully Analyzed")

            st.write("### Receipt Details")

            st.write(f"**Merchant :** {merchant}")

            st.write(f"**Amount : ₹{amount}")

            st.write(f"**Category :** {category}")

            st.write(f"**Date :** {receipt_date}")

            st.write(f"**Payment :** {payment_method}")

            st.write(f"**Receipt Type :** {receipt_type}")

            st.progress(confidence/100)

            st.caption(
                f"Confidence : {confidence}%"
            )

            advice = get_advice(

                merchant,

                category,

                amount,

                payment_method

            )

            st.divider()

            st.subheader("🤖 AI Financial Advice")

            st.info(advice)

            st.divider()

            budget = get_budget(category)

            st.metric(

                "Recommended Budget",

                f"₹{budget}"

            )

            if st.button(

                "💾 Save Expense",

                use_container_width=True

            ):

                save_expense(

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

# ----------------------------------------------------
# VOICE EXPENSE
# ----------------------------------------------------

elif menu == "🎤 Voice Expense":

    st.title("🎤 Voice Expense")

    audio_file = st.file_uploader(

        "Upload Voice",

        type=["wav"]

    )

    if audio_file:

        result = transcribe_audio_file(

            audio_file

        )

        if result["status"] == "success":

            st.success("Voice Recognized")

            st.write(result["text"])

            expense = parse_voice_expense(

                result["text"]

            )

            st.divider()

            st.subheader("Detected Expense")

            st.write(

                f"Amount : ₹{expense['amount']}"

            )

            st.write(

                f"Category : {expense['category']}"

            )

            if st.button(

                "Save Voice Expense",

                use_container_width=True

            ):

                save_expense(

                    "Voice Expense",

                    expense["amount"],

                    expense["category"],

                    "",

                    "Voice",

                    "Voice",

                    "INR",

                    100,

                    "Added through Voice"

                )

                st.success("Expense Saved")

        else:

            st.error(result["text"])

            # ----------------------------------------------------
# EXPENSE HISTORY
# ----------------------------------------------------

elif menu == "📋 Expense History":

    st.title("📋 Expense History")

    df = get_expenses_df()

    if df.empty:

        st.warning("No Expenses Found")

    else:

        search = st.text_input(
            "🔍 Search Merchant"
        )

        if search:

            df = df[
                df["merchant"]
                .str.contains(
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

            delete_expense(expense_id)

            st.success(
                "Expense Deleted Successfully"
            )

            st.rerun()


# ----------------------------------------------------
# ANALYTICS
# ----------------------------------------------------

elif menu == "📊 Analytics":

    st.title("📊 Expense Analytics")

    df = get_expenses_df()

    if df.empty:

        st.warning("No Data Available")

    else:

        st.subheader("Category Wise Expenses")

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

        st.subheader("Monthly Expense Trend")

        if "receipt_date" in df.columns:

            timeline = (
                df.groupby("receipt_date")["amount"]
                .sum()
                .reset_index()
            )

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

        st.subheader("Top 5 Merchants")

        merchant_df = (
            df.groupby("merchant")["amount"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(5)
            .reset_index()
        )

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


# ----------------------------------------------------
# EXPORT
# ----------------------------------------------------

elif menu == "📤 Export":

    st.title("📤 Export Expenses")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📊 Export Excel",
            use_container_width=True
        ):

            file = export_to_excel()

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

            file = export_to_pdf()

            with open(file, "rb") as f:

                st.download_button(

                    "⬇ Download PDF",

                    data=f,

                    file_name="expenses.pdf",

                    mime="application/pdf"

                )


# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------

st.markdown("---")

st.caption(
    "💰 Financial AI Advisor | Powered by Gemini 2.5 Flash"
)