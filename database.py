import sqlite3
import pandas as pd

DB_NAME = "expenses.db"


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_connection():
    return sqlite3.connect(DB_NAME)


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Expenses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        merchant TEXT,
        amount REAL,
        category TEXT,
        receipt_date TEXT,
        payment_method TEXT,
        receipt_type TEXT,
        currency TEXT,
        confidence INTEGER,
        advice TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# SAVE EXPENSE
# --------------------------------------------------

def save_expense(
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
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO expenses(
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
    VALUES(?,?,?,?,?,?,?,?,?,?)
    """,(
        user_id,
        merchant,
        float(amount),
        category,
        receipt_date,
        payment_method,
        receipt_type,
        currency,
        int(confidence),
        advice
    ))

    conn.commit()
    conn.close()


# --------------------------------------------------
# GET EXPENSES
# --------------------------------------------------

def get_expenses(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM expenses
    WHERE user_id=?
    ORDER BY id DESC
    """,(user_id,))

    data = cursor.fetchall()

    conn.close()

    return data


# --------------------------------------------------
# DATAFRAME
# --------------------------------------------------

def get_expenses_df(user_id):

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM expenses
        WHERE user_id=?
        ORDER BY id DESC
        """,
        conn,
        params=(user_id,)
    )

    conn.close()

    return df


# --------------------------------------------------
# DELETE
# --------------------------------------------------

def delete_expense(user_id, expense_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM expenses
    WHERE id=? AND user_id=?
    """,(expense_id,user_id))

    conn.commit()
    conn.close()


# --------------------------------------------------
# CLEAR
# --------------------------------------------------

def clear_expenses(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM expenses
    WHERE user_id=?
    """,(user_id,))

    conn.commit()
    conn.close()