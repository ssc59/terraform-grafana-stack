from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "demo_app_requests_total",
    "Total number of requests received by the demo application",
    ["endpoint"],
)


@app.route("/")
def home():
    REQUEST_COUNT.labels(endpoint="/").inc()

    return """
    <html>
        <head>
            <title>Terraform Docker Monitoring App</title>
        </head>
        <body style="font-family: Arial; text-align: center; margin-top: 80px;">
            <h1>Docker Application Is Running</h1>
            <p>This application was deployed using:</p>
            <p><strong>Terraform + Amazon ECR + Docker + Ansible</strong></p>
            <p><a href="/health">Health Check</a></p>
            <p><a href="/metrics">Prometheus Metrics</a></p>
        </body>
    </html>
    """


@app.route("/health")
def health():
    REQUEST_COUNT.labels(endpoint="/health").inc()

    return jsonify(
        {
            "status": "healthy",
            "service": "terraform-docker-app",
        }
    )


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )
