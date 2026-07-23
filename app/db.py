import sqlite3

DB_PATH = "app.db"

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

def get_user():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM employees WHERE emp_num = ?",
            (emp_num,)
        ).fetchone()

init_db()