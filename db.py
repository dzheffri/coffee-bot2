import sqlite3
import uuid

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# таблиця користувачів
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    cups INTEGER DEFAULT 0,
    qr_token TEXT UNIQUE,
    total_scans INTEGER DEFAULT 0,
    free_coffee_count INTEGER DEFAULT 0
)
""")
conn.commit()


def ensure_column_exists(column_name, column_type, default_value):
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if column_name not in columns:
        cursor.execute(
            f"ALTER TABLE users ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
        )
        conn.commit()


ensure_column_exists("total_scans", "INTEGER", 0)
ensure_column_exists("free_coffee_count", "INTEGER", 0)
ensure_column_exists("free_coffee_balance", "INTEGER", 0)
ensure_column_exists("total_free_coffee_earned", "INTEGER", 0)
ensure_column_exists("total_free_coffee_redeemed", "INTEGER", 0)

cursor.execute("""
UPDATE users
SET free_coffee_balance = free_coffee_count,
    total_free_coffee_earned = free_coffee_count
WHERE free_coffee_count > 0
  AND free_coffee_balance = 0
  AND total_free_coffee_earned = 0
""")
conn.commit()

# таблиця адміністраторів
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()


def add_user(user_id: int):
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone():
        return

    token = str(uuid.uuid4())

    cursor.execute(
        "INSERT INTO users (user_id, qr_token) VALUES (?, ?)",
        (user_id, token)
    )
    conn.commit()


def get_user_token(user_id: int):
    cursor.execute("SELECT qr_token FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None


def get_cups(user_id: int):
    cursor.execute("SELECT cups FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0


def get_user_by_token(token: str):
    cursor.execute("SELECT user_id FROM users WHERE qr_token=?", (token,))
    row = cursor.fetchone()
    return row[0] if row else None


def get_cups_by_token(token: str):
    cursor.execute("SELECT cups FROM users WHERE qr_token=?", (token,))
    row = cursor.fetchone()
    return row[0] if row else 0


def add_cup(user_id: int):
    cursor.execute(
        """
        UPDATE users
        SET cups = cups + 1,
            total_scans = total_scans + 1
        WHERE user_id=?
        """,
        (user_id,)
    )
    conn.commit()


def add_cup_by_token(token: str):
    cursor.execute(
        """
        UPDATE users
        SET cups = cups + 1,
            total_scans = total_scans + 1
        WHERE qr_token=?
        """,
        (token,)
    )
    conn.commit()


def award_free_coffee(user_id: int):
    cursor.execute(
        """
        UPDATE users
        SET cups = 0,
            free_coffee_balance = free_coffee_balance + 1,
            total_free_coffee_earned = total_free_coffee_earned + 1
        WHERE user_id=?
        """,
        (user_id,)
    )
    conn.commit()


def get_free_coffee_balance(user_id: int):
    cursor.execute("SELECT free_coffee_balance FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0


def get_free_coffee_balance_by_token(token: str):
    cursor.execute("SELECT free_coffee_balance FROM users WHERE qr_token=?", (token,))
    row = cursor.fetchone()
    return row[0] if row else 0


def redeem_free_coffee_by_token(token: str):
    cursor.execute(
        "SELECT user_id, free_coffee_balance FROM users WHERE qr_token=?",
        (token,)
    )
    row = cursor.fetchone()

    if not row:
        return "NOT_FOUND"

    user_id, balance = row

    if balance <= 0:
        return "EMPTY"

    cursor.execute(
        """
        UPDATE users
        SET free_coffee_balance = free_coffee_balance - 1,
            total_free_coffee_redeemed = total_free_coffee_redeemed + 1
        WHERE qr_token=?
        """,
        (token,)
    )
    conn.commit()

    return "OK"


def get_total_users():
    cursor.execute("SELECT COUNT(*) FROM users")
    row = cursor.fetchone()
    return row[0] if row else 0


def get_active_users():
    cursor.execute("SELECT COUNT(*) FROM users WHERE cups > 0")
    row = cursor.fetchone()
    return row[0] if row else 0


def get_total_scans():
    cursor.execute("SELECT COALESCE(SUM(total_scans), 0) FROM users")
    row = cursor.fetchone()
    return row[0] if row else 0


def get_total_free_coffee_available():
    cursor.execute("SELECT COALESCE(SUM(free_coffee_balance), 0) FROM users")
    row = cursor.fetchone()
    return row[0] if row else 0


def get_total_free_coffee_earned():
    cursor.execute("SELECT COALESCE(SUM(total_free_coffee_earned), 0) FROM users")
    row = cursor.fetchone()
    return row[0] if row else 0


def get_total_free_coffee_redeemed():
    cursor.execute("SELECT COALESCE(SUM(total_free_coffee_redeemed), 0) FROM users")
    row = cursor.fetchone()
    return row[0] if row else 0


def add_admin(user_id: int):
    cursor.execute(
        "INSERT OR IGNORE INTO admins (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()


def remove_admin(user_id: int):
    cursor.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    conn.commit()


def is_admin(user_id: int):
    cursor.execute("SELECT user_id FROM admins WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None


def get_all_admins():
    cursor.execute("SELECT user_id FROM admins ORDER BY user_id")
    return [row[0] for row in cursor.fetchall()]


def get_all_user_ids():
    cursor.execute("SELECT user_id FROM users ORDER BY user_id")
    return [row[0] for row in cursor.fetchall()]