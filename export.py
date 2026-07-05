import sqlite3
import pandas as pd
from fpdf import FPDF

DB_NAME = "expenses.db"


# ------------------------------------------
# EXPORT EXCEL
# ------------------------------------------

def export_to_excel(user_id):

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        """
        SELECT
            merchant,
            amount,
            category,
            receipt_date,
            payment_method,
            receipt_type,
            currency,
            advice
        FROM expenses
        WHERE user_id=?
        ORDER BY id DESC
        """,
        conn,
        params=(user_id,)
    )

    conn.close()

    file_name = "expenses.xlsx"

    df.to_excel(
        file_name,
        index=False
    )

    return file_name


# ------------------------------------------
# EXPORT PDF
# ------------------------------------------

def export_to_pdf(user_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        merchant,
        amount,
        category,
        receipt_date
    FROM expenses
    WHERE user_id=?
    ORDER BY id DESC
    """, (user_id,))

    rows = cursor.fetchall()

    conn.close()

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        "B",
        16
    )

    pdf.cell(
        200,
        10,
        txt="Financial AI Advisor",
        ln=True,
        align="C"
    )

    pdf.ln(5)

    pdf.set_font(
        "Arial",
        "",
        12
    )

    total = 0

    for row in rows:

        merchant = row[0]
        amount = row[1]
        category = row[2]
        date = row[3]

        total += amount

        pdf.multi_cell(
            0,
            8,
            txt=f"""
Merchant : {merchant}

Amount : ₹{amount:.2f}

Category : {category}

Date : {date}
-----------------------------------------
"""
        )

    pdf.ln(5)

    pdf.set_font(
        "Arial",
        "B",
        14
    )

    pdf.cell(
        0,
        10,
        txt=f"Total Expense : ₹{total:.2f}",
        ln=True
    )

    file_name = "expenses.pdf"

    pdf.output(file_name)

    return file_name