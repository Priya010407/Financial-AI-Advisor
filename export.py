import pandas as pd
import sqlite3
from fpdf import FPDF
import os

DB_NAME = "expenses.db"


# -------------------------------
# GET EXPENSE DATA
# -------------------------------

def fetch_expenses():

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        "SELECT * FROM expenses ORDER BY id DESC",
        conn
    )

    conn.close()

    return df


# -------------------------------
# EXPORT TO EXCEL
# -------------------------------

def export_to_excel(filename="expenses.xlsx"):

    df = fetch_expenses()

    df.to_excel(filename, index=False)

    return filename


# -------------------------------
# EXPORT TO PDF
# -------------------------------

def export_to_pdf(filename="expenses.pdf"):

    df = fetch_expenses()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Financial AI Advisor - Expense Report", ln=True, align="C")
    pdf.ln(10)

    for i, row in df.iterrows():

        line = f"{row['merchant']} | {row['amount']} | {row['category']} | {row['receipt_date']}"

        pdf.cell(200, 10, txt=line[:90], ln=True)

    pdf.output(filename)

    return filename


# -------------------------------
# DELETE ALL EXPORT FILES (OPTIONAL)
# -------------------------------

def clear_exports():

    files = ["expenses.xlsx", "expenses.pdf"]

    for f in files:
        if os.path.exists(f):
            os.remove(f)