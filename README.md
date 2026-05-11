# Flask Portfolio — DevOps Project

A multi-app Flask project containerized with Docker, migrated to PostgreSQL,
deployed to Kubernetes (minikube + AKS), and automated with an Azure DevOps CI/CD pipeline.

---

## Applications Included

| App | Route | Description |
|-----|-------|-------------|
| Portfolio | `/` | Personal portfolio with skills and projects |
| E-Commerce | `/ecommerce` | Product listing, cart, checkout, order confirmation |
| Flask Blog | `/flaskwebsite` | Blog with user auth, comments, role-based access |

All three apps run under one Flask server using `DispatcherMiddleware`.

---

## ELI5 — Explain Like I'm 5

| Term | ELI5 |
|------|------|
| **Docker** | A lunchbox that packs your app with everything it needs so it runs anywhere |
| **Docker Image** | The recipe for the lunchbox |
| **Docker Hub** | A shop where you store and share your lunchbox recipes |
| **Kubernetes** | A manager that runs and watches your lunchboxes — restarts them if they crash |
| **Pod** | One running lunchbox (container) inside Kubernetes |
| **Service** | The address/door to reach your pod from outside |
| **Deployment** | Tells Kubernetes how many pods to run and which image to use |
| **Secret** | A locked safe in Kubernetes that stores passwords and connection strings |
| **PVC** | A USB drive that persists data even if the pod restarts |
| **CI/CD Pipeline** | An automatic robot that builds, tests, and deploys your code on every push |
| **Self-hosted Agent** | Your own PC acting as the robot that runs the pipeline |
| **PostgreSQL** | A proper database that stores data permanently (replaces SQLite) |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3 |
| Framework | Flask, Flask-SQLAlchemy, Flask-Login |
| Database | PostgreSQL (migrated from SQLite) |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes (minikube locally, AKS in cloud) |
| Container Registry | Docker Hub (`elynfoo/devops-flaskapp`) |
| CI/CD | Azure DevOps Pipelines (self-hosted agent) |
| Cloud | Azure Kubernetes Service (AKS) |

---

## Project Structure

```
devops/
├── app.py                    # Entry point — combines all 3 Flask apps
├── ecommerce_app.py          # E-commerce Flask app
├── myportfolio.py            # Portfolio Flask app
├── flaskb_app.py             # Blog Flask app
├── aboutme_app.py            # About me app
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image build instructions
├── docker-compose.yml        # Local development with PostgreSQL
├── azure-pipelines.yml       # CI/CD pipeline definition
├── k8s/
│   ├── deployment.yaml       # Flask app Kubernetes Deployment
│   ├── service.yaml          # LoadBalancer Service (port 5000)
│   ├── postgres.yaml         # PostgreSQL Deployment + PVC + Service
│   └── secret.yaml           # Database credentials secret
└── templates/
    ├── ecommerce/            # E-commerce HTML templates
    ├── flaskwebsite/         # Blog HTML templates
    └── portfolio/            # Portfolio HTML templates
```

---

## Workflow Overview

```
Developer pushes code
        ↓
Azure DevOps detects push (trigger: main, feature/*)
        ↓
Self-hosted Agent (local PC) runs pipeline
        ↓
Stage 1 — BUILD:
  docker login → docker build → docker push to Docker Hub
        ↓
Stage 2 — DEPLOY:
  kubectl set image → kubectl rollout status
        ↓
Kubernetes pulls new image from Docker Hub
        ↓
App live at http://<public-ip>:5000
```

---

## Database Migration (SQLite → PostgreSQL)

All three apps were migrated from SQLite to PostgreSQL.

**Before:**
```python
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
```

**After:**
```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{database_path}")
```

`DATABASE_URL` is injected as an environment variable from Kubernetes Secret.

---

## Docker Setup

### Dockerfile
Builds the Flask multi-app image. Pushed to Docker Hub as `elynfoo/devops-flaskapp:latest`.

### docker-compose.yml
Used for **local development** only. Spins up two services:
- `db` — PostgreSQL 15 with health check
- `flaskapp` — Flask app connected to PostgreSQL

```bash
# Start locally
docker compose up --build

# Stop
docker compose down
```

---

## Kubernetes Setup

### Secret (`k8s/secret.yaml`)
Stores database credentials — never hardcoded in code:
```yaml
DATABASE_URL: postgresql://flaskuser:flaskpass@postgres-service:5432/flaskapp
```

Apply with:
```bash
kubectl apply -f k8s/secret.yaml
```

### PostgreSQL (`k8s/postgres.yaml`)
- Deployment: `postgres:15-alpine`
- PVC: 1Gi persistent storage
- Service: `ClusterIP` on port 5432
- `PGDATA=/var/lib/postgresql/data/pgdata` — fixes lost+found conflict on AKS

### Flask App (`k8s/deployment.yaml`)
- Image: `elynfoo/devops-flaskapp:latest`
- `imagePullPolicy: Always` — always pulls latest from Docker Hub
- `imagePullSecrets: dockerhub-secret` — allows pulling from private registry
- Reads `DATABASE_URL` from `flask-db-secret`

### Service (`k8s/service.yaml`)
- Type: `LoadBalancer` — exposes app on public IP
- Port: 5000

---

## CI/CD Pipeline (`azure-pipelines.yml`)

```yaml
trigger: main, feature/*
pool: Default (self-hosted agent)
```

### Stage 1 — Build
1. Docker login using secret variables `$(DOCKER_USERNAME)` and `$(DOCKER_PASSWORD)`
2. Build image tagged with `$(Build.BuildId)` and `latest`
3. Push both tags to Docker Hub

### Stage 2 — Deploy
1. `kubectl set image` — updates the deployment with new build ID tag
2. `kubectl rollout status` — waits and confirms deployment succeeded

### Secret Variables (Azure DevOps)
| Variable | Value |
|----------|-------|
| `DOCKER_USERNAME` | `elynfoo` |
| `DOCKER_PASSWORD` | Docker Hub password (masked) |

---

## Local Kubernetes (Minikube)

```bash
# Start minikube
minikube start --driver=docker

# Apply all manifests
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Expose LoadBalancer (separate terminal)
minikube tunnel

# Check pods
kubectl get pods
kubectl get services
```

---

## AKS Deployment (Azure)

```bash
# Login
az login

# Create AKS cluster (Standard_B2als_v2 = AMD64, cheapest available)
az aks create \
  --resource-group flask-portfolio-rg \
  --name flask-portfolio-aks \
  --node-count 1 \
  --node-vm-size Standard_B2als_v2 \
  --location southeastasia \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group flask-portfolio-rg --name flask-portfolio-aks

# Apply manifests
kubectl apply -f k8s/

# Create Docker Hub pull secret
kubectl create secret docker-registry dockerhub-secret \
  --docker-username=elynfoo \
  --docker-password=<password> \
  --docker-server=https://index.docker.io/v1/

# Get public IP
kubectl get service flask-service
```

AKS Public IP: **40.90.189.161**
Live App: http://40.90.189.161:5000

---

## Errors Encountered and Fixed

| Error | Cause | Fix |
|-------|-------|-----|
| App bound to 127.0.0.1 | Two `run_simple` calls — first blocked second | Removed 127.0.0.1 call, kept 0.0.0.0 only |
| Page still loading after fix | Container not rebuilt | `docker compose down && docker compose up --build` |
| `ErrImageNeverPull` | Wrong image name in k8s manifest | Updated image name to match Docker Hub |
| `dockerhub-secret` missing | Backtick line continuation failed in Git Bash | Used single-line kubectl command |
| No hosted parallelism | Azure DevOps free account limitation | Set up self-hosted agent at `C:\agent` |
| Agent can't access Docker | Ran as NETWORK SERVICE account | Stopped service, ran `.\run.cmd` interactively |
| PostgreSQL PGDATA error | `lost+found` in PVC mount on AKS | Added `PGDATA=/var/lib/postgresql/data/pgdata` |
| Exec format error on AKS | `Standard_B2pls_v2` is ARM64, image is AMD64 | Recreated cluster with `Standard_B2als_v2` |
| Products not showing | Sample data only seeded in `__main__` block | Moved seeding to `with app.app_context()` block |

---

## Key Learnings

- Always bind Flask to `0.0.0.0` inside Docker, not `127.0.0.1`
- Use `imagePullPolicy: Always` so Kubernetes fetches the latest image
- Never hardcode secrets — use Kubernetes Secrets and env vars
- `PGDATA` must be set to a subdirectory to avoid conflicts with PVC mount
- AKS node VM architecture must match Docker image architecture (AMD64 vs ARM64)
- Self-hosted agents need interactive session to access Docker Desktop
- Sample data must be seeded inside `app.app_context()` not `__main__`
