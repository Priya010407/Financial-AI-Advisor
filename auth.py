import sqlite3
import hashlib

DB_NAME = "expenses.db"


# -------------------------------
# PASSWORD SECURITY
# -------------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# -------------------------------
# REGISTER USER
# -------------------------------

def register_user(name, email, password):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO users (
            name,
            email,
            password
        )
        VALUES (?, ?, ?)
        """, (
            name,
            email,
            hash_password(password)
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


# -------------------------------
# LOGIN USER
# -------------------------------

def login_user(email, password):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email
        FROM users
        WHERE email = ?
        AND password = ?
    """, (
        email,
        hash_password(password)
    ))

    user = cursor.fetchone()
    conn.close()

    return user


# -------------------------------
# CHECK USER EXISTS
# -------------------------------

def user_exists(email):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM users WHERE email = ?
    """, (email,))

    data = cursor.fetchone()

    conn.close()

    return data is not None