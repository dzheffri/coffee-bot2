import uuid
from psycopg import connect

from config import DATABASE_URL


def get_connection():
    return connect(DATABASE_URL, autocommit=True)


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                cups INTEGER DEFAULT 0,
                qr_token TEXT UNIQUE,
                total_scans INTEGER DEFAULT 0,
                free_coffee_count INTEGER DEFAULT 0,
                free_coffee_balance INTEGER DEFAULT 0,
                total_free_coffee_earned INTEGER DEFAULT 0,
                total_free_coffee_redeemed INTEGER DEFAULT 0
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id BIGINT PRIMARY KEY
            )
            """)

            cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS total_scans INTEGER DEFAULT 0
            """)

            cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS free_coffee_count INTEGER DEFAULT 0
            """)

            cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS free_coffee_balance INTEGER DEFAULT 0
            """)

            cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS total_free_coffee_earned INTEGER DEFAULT 0
            """)

            cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS total_free_coffee_redeemed INTEGER DEFAULT 0
            """)

            cursor.execute("""
            UPDATE users
            SET free_coffee_balance = free_coffee_count,
                total_free_coffee_earned = free_coffee_count
            WHERE free_coffee_count > 0
              AND free_coffee_balance = 0
              AND total_free_coffee_earned = 0
            """)


init_db()


def add_user(user_id: int):
    token = str(uuid.uuid4())

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO users (user_id, qr_token)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
            """, (user_id, token))


def get_user_token(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT qr_token FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None


def get_cups(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT cups FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else 0


def get_user_by_token(token: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM users WHERE qr_token = %s",
                (token,)
            )
            row = cursor.fetchone()
            return row[0] if row else None


def get_cups_by_token(token: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT cups FROM users WHERE qr_token = %s",
                (token,)
            )
            row = cursor.fetchone()
            return row[0] if row else 0


def add_cup(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE users
            SET cups = cups + 1,
                total_scans = total_scans + 1
            WHERE user_id = %s
            """, (user_id,))


def add_cup_by_token(token: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE users
            SET cups = cups + 1,
                total_scans = total_scans + 1
            WHERE qr_token = %s
            """, (token,))


def add_cups_by_token(token: str, count: int):
    if count <= 0:
        raise ValueError("count must be > 0")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT user_id, cups, free_coffee_balance
            FROM users
            WHERE qr_token = %s
            """, (token,))
            row = cursor.fetchone()

            if not row:
                return None

            user_id, current_cups, current_free_balance = row

            total_cups = current_cups + count
            earned_free = total_cups // 7
            remaining_cups = total_cups % 7
            new_free_balance = current_free_balance + earned_free

            cursor.execute("""
            UPDATE users
            SET cups = %s,
                total_scans = total_scans + %s,
                free_coffee_balance = free_coffee_balance + %s,
                total_free_coffee_earned = total_free_coffee_earned + %s
            WHERE qr_token = %s
            """, (
                remaining_cups,
                count,
                earned_free,
                earned_free,
                token
            ))

            return {
                "user_id": user_id,
                "cups": remaining_cups,
                "earned_free": earned_free,
                "free_balance": new_free_balance
            }


def award_free_coffee(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE users
            SET cups = 0,
                free_coffee_balance = free_coffee_balance + 1,
                total_free_coffee_earned = total_free_coffee_earned + 1
            WHERE user_id = %s
            """, (user_id,))


def get_free_coffee_balance(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT free_coffee_balance FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else 0


def get_free_coffee_balance_by_token(token: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT free_coffee_balance FROM users WHERE qr_token = %s",
                (token,)
            )
            row = cursor.fetchone()
            return row[0] if row else 0


def redeem_free_coffee_by_token(token: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT user_id, free_coffee_balance
            FROM users
            WHERE qr_token = %s
            """, (token,))
            row = cursor.fetchone()

            if not row:
                return "NOT_FOUND"

            user_id, balance = row

            if balance <= 0:
                return "EMPTY"

            cursor.execute("""
            UPDATE users
            SET free_coffee_balance = free_coffee_balance - 1,
                total_free_coffee_redeemed = total_free_coffee_redeemed + 1
            WHERE qr_token = %s
            """, (token,))

            return "OK"


def get_total_users():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users")
            row = cursor.fetchone()
            return row[0] if row else 0


def get_active_users():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE cups > 0")
            row = cursor.fetchone()
            return row[0] if row else 0


def get_total_scans():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COALESCE(SUM(total_scans), 0) FROM users")
            row = cursor.fetchone()
            return row[0] if row else 0


def get_total_free_coffee_available():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COALESCE(SUM(free_coffee_balance), 0) FROM users")
            row = cursor.fetchone()
            return row[0] if row else 0


def get_total_free_coffee_earned():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COALESCE(SUM(total_free_coffee_earned), 0) FROM users")
            row = cursor.fetchone()
            return row[0] if row else 0


def get_total_free_coffee_redeemed():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COALESCE(SUM(total_free_coffee_redeemed), 0) FROM users")
            row = cursor.fetchone()
            return row[0] if row else 0


def add_admin(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO admins (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
            """, (user_id,))


def remove_admin(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM admins WHERE user_id = %s",
                (user_id,)
            )


def is_admin(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM admins WHERE user_id = %s",
                (user_id,)
            )
            return cursor.fetchone() is not None


def get_all_admins():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM admins ORDER BY user_id")
            return [row[0] for row in cursor.fetchall()]


def get_all_user_ids():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users ORDER BY user_id")
            return [row[0] for row in cursor.fetchall()]
