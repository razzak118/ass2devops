"""Student Score Prediction demo used for Agile Assignment No. 2."""
from __future__ import annotations

import time
import os
from functools import lru_cache
from flask import Flask, jsonify, request, render_template_string, g
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest
from model_utils import build_model, predict_score

REQUEST_COUNT = Counter(
    "student_score_http_requests_total",
    "Total HTTP requests received by the Student Score Prediction app",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "student_score_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint"],
)

HTML = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Student Score Predictor</title>
<style>
body{font-family:Arial,sans-serif;max-width:760px;margin:50px auto;padding:0 20px;color:#172033;background:#f5f7fb}
main{background:white;padding:32px;border-radius:14px;box-shadow:0 4px 20px #17203312}
h1{margin-top:0;color:#214e8a}label{display:block;margin:18px 0 8px;font-weight:bold}
input,button{font-size:16px;padding:10px;border-radius:7px}input{border:1px solid #b8c4d6;width:170px}
button{background:#214e8a;color:white;border:0;cursor:pointer;margin-left:8px}
.note{color:#56647b;font-size:14px}.result{font-size:22px;font-weight:bold;color:#16744a;margin-top:20px}
.links a{margin-right:16px}
</style></head>
<body><main><h1>Student Score Predictor</h1>
<p>Enter daily study hours to estimate an exam score using a simple regression model.</p>
<form method="post" action="/predict"><label for="study_hours">Study hours per day (0 to 16)</label>
<input id="study_hours" name="study_hours" type="number" min="0" max="16" step="0.5" required value="{{ hours if hours is not none else 4 }}">
<button type="submit">Predict score</button></form>
{% if score is not none %}<p class="result">Estimated score: {{ score }} / 100</p>{% endif %}
<p class="note">Educational demo only. This estimate is not a real academic assessment.</p>
<div class="links"><a href="/health">Health</a><a href="/metrics">Metrics</a></div>
</main></body></html>"""


def create_app() -> Flask:
    app = Flask(__name__)

    @app.before_request
    def start_timer():
        g.request_start = time.perf_counter()

    @app.after_request
    def record_metrics(response):
        endpoint = request.endpoint or "unknown"
        REQUEST_COUNT.labels(request.method, endpoint, str(response.status_code)).inc()
        elapsed = time.perf_counter() - getattr(g, "request_start", time.perf_counter())
        REQUEST_LATENCY.labels(endpoint).observe(elapsed)
        return response

    @app.get("/")
    def index():
        return render_template_string(HTML, hours=None, score=None)

    @app.post("/predict")
    def predict():
        if request.is_json:
            payload = request.get_json(silent=True) or {}
            raw_hours = payload.get("study_hours")
        else:
            raw_hours = request.form.get("study_hours")
        try:
            hours = float(raw_hours)
        except (TypeError, ValueError):
            if request.is_json:
                return jsonify(error="study_hours must be a number"), 400
            return render_template_string(HTML, hours="", score=None), 400
        if not 0 <= hours <= 16:
            if request.is_json:
                return jsonify(error="study_hours must be between 0 and 16"), 400
            return render_template_string(HTML, hours=hours, score=None), 400
        score = round(predict_score(build_model(), hours), 1)
        if request.is_json:
            return jsonify(study_hours=hours, predicted_score=score)
        return render_template_string(HTML, hours=hours, score=score)

    @app.get("/health")
    def health():
        return jsonify(status="healthy", application="student-score-predictor")

    @app.get("/metrics")
    def metrics():
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
