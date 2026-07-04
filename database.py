import sqlite3
import pandas as pd

DB_NAME = "expenses.db"


# -------------------------------
# CREATE DATABASE
# -------------------------------

def create_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant TEXT,
        amount REAL,
        category TEXT,
        receipt_date TEXT,
        payment_method TEXT,
        receipt_type TEXT,
        currency TEXT,
        confidence INTEGER,
        advice TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# -------------------------------
# SAVE EXPENSE
# -------------------------------

def save_expense(
    merchant,
    amount,
    category,
    receipt_date,
    payment_method,
    receipt_type,
    currency,
    confidence,
    advice
):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO expenses(
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
    VALUES(?,?,?,?,?,?,?,?,?)
    """,(
        merchant,
        amount,
        category,
        receipt_date,
        payment_method,
        receipt_type,
        currency,
        confidence,
        advice
    ))

    conn.commit()
    conn.close()


# -------------------------------
# GET EXPENSES (Tuple)
# -------------------------------

def get_expenses():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM expenses
    ORDER BY id DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# -------------------------------
# GET DATAFRAME
# -------------------------------

def get_expenses_df():

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        "SELECT * FROM expenses",
        conn
    )

    conn.close()

    return df


# -------------------------------
# DELETE ONE EXPENSE
# -------------------------------

def delete_expense(expense_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id=?",
        (expense_id,)
    )

    conn.commit()

    conn.close()


# -------------------------------
# CLEAR ALL
# -------------------------------

def clear_expenses():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses")

    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name='expenses'"
    )

    conn.commit()

    conn.close()