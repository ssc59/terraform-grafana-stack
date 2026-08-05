from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from worker import run_employee_worker
import db


app = Flask(__name__)

LOG_DIR = Path("/tmp/employee-worker-logs")


@app.route("/")
def home():
    """
    Add-user page.
    """
    return render_template("index.html")


@app.route("/users")
def users():
    """
    Display all users and their provisioning status.
    """
    employees = db.get_all_users()

    user_data = []

    for employee in employees:
        employee_number = employee["emp_num"]

        status = get_worker_status(employee_number)

        user_data.append({
            "user_id": employee["user_id"],
            "name": employee["name"],
            "account": employee["account"],
            "proc": employee["proc"],
            "employee_number": employee_number,
            "zos_uid": employee["zos_uid"],
            "status": status,
        })

    return render_template(
        "users.html",
        employees=user_data,
    )


@app.route("/create-user", methods=["POST"])
def create_user():

    user_id = request.form["user_id"].strip().upper()
    name = request.form["name"].strip()
    account = request.form["account"].strip()
    procedure = request.form["procedure"].strip()

    # Automatically generate the next employee number and z/OS UID.
    employee_number = db.get_next_employee_number()
    zos_uid = db.get_next_zos_uid()

    try:
        # Add the employee to the database.
        db.set_user(
            user_id,
            name,
            account,
            procedure,
            employee_number,
            zos_uid,
        )

    except Exception as e:
        return render_template(
            "result.html",
            success=False,
            message=str(e),
        )

    # Start the existing provisioning workflow.
    run_employee_worker(str(employee_number))

    # Go directly to the user/provisioning dashboard.
    return redirect(url_for("users"))


def get_worker_status(employee_number):
    """
    Determine the current provisioning status from the worker log.
    """

    log_path = (
        LOG_DIR
        / f"employee-{employee_number}.log"
    )

    if not log_path.exists():
        return "Provisioning..."

    try:
        log_text = log_path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        return "Provisioning..."

    if "Worker completed successfully." in log_text:
        return "Completed"

    if "WORKER FAILED" in log_text:
        return "Failed"

    return "Provisioning..."


@app.route("/logs/<employee_number>")
def worker_log(employee_number):
    """
    Return the current worker log for a user.
    The frontend polls this endpoint while the modal is open.
    """

    log_path = (
        LOG_DIR
        / f"employee-{employee_number}.log"
    )

    if not log_path.exists():
        return "Worker has not produced a log yet."

    return log_path.read_text(
        encoding="utf-8",
        errors="replace",
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )