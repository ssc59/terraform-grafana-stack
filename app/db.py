from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent / "app.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                user_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                account TEXT NOT NULL,
                procedure TEXT NOT NULL,
                emp_num INTEGER NOT NULL UNIQUE,
                zos_uid INTEGER NOT NULL UNIQUE
            )
        """)

def set_user(user_id, name, account, procedure, emp_num, zos_uid):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO employees (
                user_id,
                name,
                account,
                procedure,
                emp_num,
                zos_uid
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, account, procedure, emp_num, zos_uid)
        )

def get_user(emp_num):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM employees WHERE emp_num = ?",
            (emp_num,)
        ).fetchone()

def get_all_users():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        users = conn.execute(
            "SELECT * FROM employees"
        ).fetchall()

        return [dict(user) for user in users]

def delete_user(employee_number: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM employees WHERE emp_num = ?",
            (employee_number,),
        )
        conn.commit()

        return cursor.rowcount > 0
    
def get_next_employee_number():
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT MAX(emp_num) FROM employees"
        ).fetchone()

    return (row[0] or 60000) + 1


def get_next_zos_uid():
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT MAX(zos_uid) FROM employees"
        ).fetchone()

    return (row[0] or 8040) + 1

init_db()