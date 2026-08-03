from flask import Flask, render_template, request, Response
from pathlib import Path
from worker import run_employee_worker
import db


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create-user", methods=["POST"])
def create_user():

    user_id = request.form["user_id"].strip().upper()
    name = request.form["name"].strip()

    account = request.form["account"].strip()
    procedure = request.form["procedure"].strip()

    employee_number = db.get_next_employee_number()
    zos_uid = db.get_next_zos_uid()

    try:

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

    run_employee_worker(str(employee_number))

    return render_template(
        "result.html",
        success=True,
        user_id=user_id,
        name=name,
        employee_number=employee_number,
        zos_uid=zos_uid,
    )

@app.route("/logs/<employee_number>")
def worker_log(employee_number):
    log_path = (
        Path("/tmp/employee-worker-logs")
        / f"employee-{employee_number}.log"
    )

    if not log_path.exists():
        return Response(
            "Worker log does not exist yet.",
            status=404,
            mimetype="text/plain",
        )

    return Response(
        log_path.read_text(encoding="utf-8"),
        mimetype="text/plain",
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )