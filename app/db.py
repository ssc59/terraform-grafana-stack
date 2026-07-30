import os

from sqlalchemy import create_engine, text


DB_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
)

def init_db():
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    user_id VARCHAR(8) NOT NULL UNIQUE,
                    name VARCHAR(100) NOT NULL,
                    account VARCHAR(20) NOT NULL,
                    proc VARCHAR(20) NOT NULL,
                    emp_num INTEGER NOT NULL UNIQUE,
                    zos_uid INTEGER NOT NULL UNIQUE
                )
                """
            )
        )

def set_user(user_id, name, account, proc, emp_num, zos_uid):
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO employees (
                    user_id,
                    name,
                    account,
                    proc,
                    emp_num,
                    zos_uid
                )
                VALUES (:user_id, :name, :account, :proc, :emp_num, :zos_uid)
                """
            ),
            {
                "user_id": user_id,
                "name": name,
                "account": account,
                "proc": proc,
                "emp_num": emp_num,
                "zos_uid": zos_uid,
            }
        )

def get_user(emp_num):
    with engine.connect() as conn:
        user = conn.execute(
            text("SELECT * FROM employees WHERE emp_num = :emp_num"),
            {"emp_num": emp_num},
        ).mappings().first()

        return dict(user) if user else None

def get_all_users():
    with engine.connect() as conn:

        users = conn.execute(
            text("SELECT * FROM employees")
        ).mappings().all()

        return [dict(user) for user in users]

def delete_user(emp_num: str) -> bool:
    with engine.begin() as conn:
        cursor = conn.execute(
            text("DELETE FROM employees WHERE emp_num = :emp_num"),
            {"emp_num": emp_num},
        )

        return cursor.rowcount > 0
    
def get_next_employee_number():
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT MAX(emp_num) FROM employees")
        ).fetchone()

    return (row[0] or 60000) + 1


def get_next_zos_uid():
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT MAX(zos_uid) FROM employees")
        ).fetchone()

    return (row[0] or 8040) + 1

init_db()