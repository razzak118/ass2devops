# Agile Assignment No. 2 — Student Score Prediction DevOps Project

This is a **standalone project**. It does not use or depend on another application or Git repository.

## Application scenario

A small Flask web app estimates an exam score from the number of hours a student studies per day. It uses a teaching-only linear regression model trained on illustrative data. It is not an academic assessment tool.

## What is included

- **Q1 — CI/CD:** Flask application, automated pytest tests, Dockerfile, Docker Compose and GitHub Actions workflow (`.github/workflows/ci.yml`).
- **Q2 — ML lifecycle and monitoring:** MLflow experiment tracking, parameter and metric logging, model registration/versioning and model serving; Prometheus metrics and a pre-provisioned Grafana dashboard.
- **Q3 — End-to-end DevOps:** `architecture.svg` shows Agile planning, Git/GitHub, CI/CD, Docker Compose, MLflow and monitoring.

## 1. Run locally on Ubuntu

Install prerequisites if needed:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git unzip curl docker.io docker-compose-v2
sudo systemctl enable --now docker
```

Create an isolated virtual environment, install dependencies and run tests:

```bash
cd ~/student-score-devops
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

Run the website directly:

```bash
python app.py
```

Open `http://localhost:5000`, enter study hours, and submit. In a second terminal test the API:

```bash
curl -s http://localhost:5000/health
curl -s -X POST http://localhost:5000/predict -H 'Content-Type: application/json' -d '{"study_hours": 4}'
```

Stop the local server with `Ctrl+C` before starting Docker Compose to free host port 5100.

## 2. Docker Compose deployment (Q1)

From the project root:

```bash
sudo docker compose up --build -d
sudo docker compose ps
curl -s http://localhost:5000/health
curl -s -X POST http://localhost:5000/predict -H 'Content-Type: application/json' -d '{"study_hours": 4}'
```

Generate sample traffic for the dashboard:

```bash
for i in {1..20}; do curl -s http://localhost:5000/ >/dev/null; done
echo 'Sample requests completed'
```

URLs:

- App: http://localhost:5000
- Prometheus targets: http://localhost:9090/targets
- Prometheus expression UI: http://localhost:9090
- Grafana: http://localhost:3000 (initial login: `admin` / `admin`; change the password if prompted)

Grafana has a provisioned **Student Score Monitoring** dashboard. It shows request rate, 95th percentile request latency, total requests and the Prometheus target state.

Useful checks:

```bash
sudo docker compose logs --tail=50
sudo docker compose ps
```

To stop the local deployment:

```bash
sudo docker compose down
```

## 3. MLflow lifecycle (Q2)

Run MLflow from its own virtual environment. Keep it separate from the Flask app environment:

```bash
cd ~/student-score-devops/mlflow_demo
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python train.py
```

The script logs parameters and MAE/RMSE/R² metrics to the `Student Score Prediction` experiment, registers `StudentScoreModel`, and writes the latest registered model version to `model_version.txt`.

Start MLflow UI in the same `mlflow_demo` directory:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5050
```

Open http://localhost:5050 and inspect the experiment run and registered model.

For model serving, open another terminal and run:

```bash
cd ~/student-score-devops/mlflow_demo
source .venv/bin/activate
VERSION=$(cat model_version.txt)
MLFLOW_TRACKING_URI=sqlite:///mlflow.db mlflow models serve --model-uri "models:/StudentScoreModel/${VERSION}" --host 127.0.0.1 --port 5001 --no-conda
```

When the serving terminal reports that it is listening, use a third terminal:

```bash
curl -s -X POST http://127.0.0.1:5001/invocations \
  -H 'Content-Type: application/json' \
  -d '{"inputs": [[4.0]]}'
```

If the model server reports a missing Python package, install the package it names into the same `mlflow_demo/.venv` and retry. The model artifacts use cloudpickle serialization; only load the local model artifacts created by this assignment.

## 4. Git and GitHub Actions (Q1 and Q3)

This folder is separate from existing work. Initialize its own Git repository:

```bash
cd ~/student-score-devops
git init -b main
git add .
git commit -m "Initial Student Score Prediction DevOps project"
```

Create a **new empty GitHub repository** called `student-score-devops` from GitHub's website. Do not select README, license or .gitignore when creating the remote (this project already contains them). Replace `<YOUR_GITHUB_USERNAME>` below:

```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/student-score-devops.git
git push -u origin main
```

Open the new repository → **Actions** → **Student Score CI Pipeline**. The workflow installs dependencies, runs pytest, validates Docker Compose configuration, and builds the Docker image. Capture the successful run for the assignment.

If you make changes later:

```bash
git add .
git commit -m "Describe the change"
git push
```

## 5. Architecture diagram (Q3)

Open `architecture.svg` in Firefox:

```bash
xdg-open ~/student-score-devops/architecture.svg
```

Take a screenshot for the report. The diagram is also suitable for explaining the workflow verbally.

## 6. Screenshot checklist

Capture real results from your own machine. Use `PrtSc` or `Shift+PrtSc`; save images in `~/student-score-devops/screenshots/`.

1. `01-tests.png` — pytest showing all tests passed.
2. `02-compose.png` — `sudo docker compose ps` showing the app, Prometheus and Grafana.
3. `03-app.png` — application page or prediction response.
4. `04-actions.png` — successful GitHub Actions workflow run.
5. `05-mlflow-run.png` — MLflow experiment with parameters/metrics.
6. `06-model-version.png` — registered model and version.
7. `07-model-serving.png` — successful prediction from MLflow model server.
8. `08-prometheus.png` — Prometheus target shows `UP`.
9. `09-grafana.png` — Student Score Monitoring dashboard.
10. `10-architecture.png` — architecture diagram.

Combine them into one PDF after saving them:

```bash
sudo apt install -y img2pdf
cd ~/student-score-devops
img2pdf screenshots/*.png -o AGILE_Assignment2_Evidence.pdf
```

Only include screenshots you actually captured. Review the resulting PDF before submission.

## Viva / explanation in simple words

- **Application:** Flask accepts study hours and returns an estimated score from a basic linear regression model.
- **Git:** tracks changes in source code; GitHub stores the independent repository.
- **CI/CD:** on a push or pull request, GitHub Actions installs dependencies, runs automated tests, checks Compose configuration and builds a Docker image.
- **Docker Compose:** runs the web app and the monitoring services together.
- **MLflow:** tracks the model experiment, records parameters/metrics, and registers a versioned model for serving.
- **Prometheus:** scrapes application metrics exposed at `/metrics`.
- **Grafana:** reads Prometheus data and displays request rate, latency and target health.
- **End-to-end flow:** plan a task → commit/push code → run CI → build/deploy containers → track the ML model → monitor the live app.

**Note:** the toy dataset is illustrative. The ML score is for demonstrating tooling only, not for making real student decisions.
