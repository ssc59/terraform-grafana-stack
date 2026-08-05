from flask import (
    Flask,
    Response,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from pathlib import Path
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from worker import run_employee_worker
import db
import time


app = Flask(__name__)

LOG_DIR = Path("/tmp/employee-worker-logs")


# Prometheus metrics
HTTP_REQUESTS_TOTAL = Counter(
    "flask_http_requests_total",
    "Total number of HTTP requests received by the Flask application.",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "flask_http_request_duration_seconds",
    "Time spent processing Flask HTTP requests.",
    ["method", "endpoint"],
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "flask_http_requests_in_progress",
    "Number of Flask HTTP requests currently being processed.",
)

USERS_CREATED_TOTAL = Counter(
    "employee_users_created_total",
    "Total number of employee user provisioning requests created.",
)

USER_CREATION_FAILURES_TOTAL = Counter(
    "employee_user_creation_failures_total",
    "Total number of employee user creation failures.",
)

WORKER_STARTS_TOTAL = Counter(
    "employee_worker_starts_total",
    "Total number of employee provisioning workers started.",
)

EMPLOYEE_PROVISIONING_STATUS = Gauge(
    "employee_provisioning_status",
    (
        "Provisioning status for an employee. "
        "1 means the employee currently has this status."
    ),
    ["employee_number", "status"],
)


@app.before_request
def start_request_timer():
    """
    Record when each request starts.
    """
    g.request_started_at = time.perf_counter()
    HTTP_REQUESTS_IN_PROGRESS.inc()


@app.after_request
def record_request_metrics(response):
    """
    Record request count, status code, and processing duration.
    """
    endpoint = request.endpoint or "unknown"

    started_at = getattr(
        g,
        "request_started_at",
        time.perf_counter(),
    )

    duration = time.perf_counter() - started_at

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=endpoint,
        status=str(response.status_code),
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=request.method,
        endpoint=endpoint,
    ).observe(duration)

    return response


@app.teardown_request
def finish_request_metrics(exception=None):
    """
    Ensure the in-progress request gauge is reduced even when an error occurs.
    """
    HTTP_REQUESTS_IN_PROGRESS.dec()


@app.route("/")
def home():
    """
    Add-user page.
    """
    return render_template("index.html")


@app.route("/health")
def health():
    """
    Health-check endpoint used by Docker, Prometheus, and deployment workflows.
    """
    return {
        "status": "healthy",
        "service": "terraform-docker-app",
    }, 200


@app.route("/metrics")
def metrics():
    """
    Prometheus metrics endpoint.
    """
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST,
    )


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

        update_provisioning_metric(
            employee_number,
            status,
        )

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
    """
    Add an employee to the database and start provisioning.
    """
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

        USERS_CREATED_TOTAL.inc()

    except Exception as error:
        USER_CREATION_FAILURES_TOTAL.inc()

        return render_template(
            "result.html",
            success=False,
            message=str(error),
        ), 500

    try:
        run_employee_worker(str(employee_number))
        WORKER_STARTS_TOTAL.inc()

        update_provisioning_metric(
            employee_number,
            "Provisioning...",
        )

    except Exception as error:
        USER_CREATION_FAILURES_TOTAL.inc()

        update_provisioning_metric(
            employee_number,
            "Failed",
        )

        return render_template(
            "result.html",
            success=False,
            message=f"User was created, but provisioning failed: {error}",
        ), 500

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
    except OSError:
        return "Provisioning..."

    if "Worker completed successfully." in log_text:
        return "Completed"

    if "WORKER FAILED" in log_text:
        return "Failed"

    return "Provisioning..."


def update_provisioning_metric(employee_number, current_status):
    """
    Update the Prometheus provisioning status metric.

    Only one status is set to 1 for each employee.
    All other statuses are set to 0.
    """
    statuses = [
        "Provisioning",
        "Completed",
        "Failed",
    ]

    normalized_status = current_status.replace("...", "")

    for status in statuses:
        EMPLOYEE_PROVISIONING_STATUS.labels(
            employee_number=str(employee_number),
            status=status,
        ).set(
            1 if status == normalized_status else 0
        )


@app.route("/logs/<employee_number>")
def worker_log(employee_number):
    """
    Return the current worker log for a user.
    The frontend polls this endpoint while the modal is open.
    """
    if not employee_number.isdigit():
        return "Invalid employee number.", 400

    log_path = (
        LOG_DIR
        / f"employee-{employee_number}.log"
    )

    if not log_path.exists():
        return "Worker has not produced a log yet.", 404

    try:
        return log_path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError as error:
        return f"Unable to read worker log: {error}", 500


if __name__ == "__main__":
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )