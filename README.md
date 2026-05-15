# 🗳️ Kubernetes Vote App — Pod-to-Pod Communication Demo

A hands-on demo project that shows how pods communicate with each other inside a Kubernetes cluster using **ClusterIP Services** and **Kubernetes DNS (CoreDNS)**.

Built for students learning Docker → ECR → Kubernetes (EKS) workflows.

---

## 📌 What This Project Demonstrates

| Concept | How it's shown |
|---|---|
| Dockerizing apps | Separate Dockerfiles for frontend and backend |
| Pushing images to ECR | Both images pushed to AWS ECR |
| Kubernetes Deployments | 2 deployments — frontend and backend |
| Pod-to-Pod communication | Frontend pod calls backend pod via ClusterIP service name |
| Service types | `LoadBalancer` (public) vs `ClusterIP` (internal only) |
| Kubernetes DNS | `backend-service` resolves automatically via CoreDNS |

---

## 🏗️ Architecture

```
Internet / User
      │
      ▼
┌─────────────────────────────────┐
│  frontend-service (LoadBalancer)│  ← Exposes port 80 to internet via AWS ELB
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   Frontend Pod (React / Nginx)  │  ← Deployment: vote-frontend
│   Image pulled from ECR         │
└────────────────┬────────────────┘
                 │
                 │  HTTP → http://backend-service:5000
                 │  (Kubernetes DNS resolves service name)
                 ▼
┌─────────────────────────────────┐
│  backend-service (ClusterIP)    │  ← Internal only, NOT exposed to internet
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   Backend Pod (Python Flask)    │  ← Deployment: vote-backend
│   Image pulled from ECR         │
└─────────────────────────────────┘
```

> **Key insight:** The frontend pod never uses a Pod IP address to reach the backend. It uses the service name `backend-service` — Kubernetes CoreDNS resolves this automatically, even if pods restart and get new IPs.

---

## 📁 Project Structure

```
k8s-pod-to-pod-demo/
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   └── nginx.conf
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
└── k8s-manifests/
    ├── 01-backend-deployment.yaml
    ├── 02-backend-service.yaml       ← ClusterIP (pod-to-pod communication)
    ├── 03-frontend-deployment.yaml
    └── 04-frontend-service.yaml      ← LoadBalancer (internet access)
```

---

## ⚙️ Prerequisites

Before you begin, make sure the following are installed and configured:

- [Docker](https://docs.docker.com/get-docker/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) (configured with `aws configure`)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- An active **EKS cluster**
- An **ECR repository** for each image (`demo/vote-frontend` and `demo/vote-backend`)
- demo/vote-backend
- demo/vote-frontend

- You can create them with these commands:
- bash
- aws ecr create-repository --repository-name demo/vote-backend --region us-east-1
- aws ecr create-repository --repository-name demo/vote-frontend --region us-east-1

---

## 🚀 Step-by-Step Deployment

### Step 1 — Authenticate Docker with ECR

```bash
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS \
  --password-stdin 865189140490.dkr.ecr.us-east-1.amazonaws.com
```

---

### Step 2 — Build and Push the Backend Image

```bash
# Build
docker build -t vote-backend ./backend

# Tag
docker tag vote-backend:latest \
  865189140490.dkr.ecr.us-east-1.amazonaws.com/demo/vote-backend:v1

# Push
docker push 865189140490.dkr.ecr.us-east-1.amazonaws.com/demo/vote-backend:v1
```

---

### Step 3 — Build and Push the Frontend Image

```bash
# Build
docker build -t vote-frontend ./frontend

# Tag
docker tag vote-frontend:latest \
  865189140490.dkr.ecr.us-east-1.amazonaws.com/demo/vote-frontend:v1

# Push
docker push 865189140490.dkr.ecr.us-east-1.amazonaws.com/demo/vote-frontend:v1
```

---

### Step 4 — Apply Kubernetes Manifests

> ⚠️ Apply backend **before** frontend so the `backend-service` DNS name is available when the frontend pods start.

```bash
kubectl apply -f k8s-manifests/01-backend-deployment.yaml
kubectl apply -f k8s-manifests/02-backend-service.yaml
kubectl apply -f k8s-manifests/03-frontend-deployment.yaml
kubectl apply -f k8s-manifests/04-frontend-service.yaml
```

---

### Step 5 — Verify Everything is Running

```bash
# Check all pods are in Running state
kubectl get pods

# Check both services
kubectl get services

# Get the public URL of the frontend (copy the EXTERNAL-IP)
kubectl get service frontend-service
```

Expected output:
```
NAME               TYPE           CLUSTER-IP      EXTERNAL-IP          PORT(S)
backend-service    ClusterIP      10.100.45.12    <none>               5000/TCP
frontend-service   LoadBalancer   10.100.89.34    abc123.elb.amazonaws.com   80:31234/TCP
```

Open `http://<EXTERNAL-IP>` in your browser to see the Vote App.

---

## 🔍 How Pod-to-Pod Communication Works

The frontend pod calls the backend pod using this line in `index.html`:

```js
const BACKEND_URL = "http://backend-service:5000";
```

Here is what happens internally when you click a vote button:

```
1. Browser sends POST /vote/Dogs to the Frontend Pod (via LoadBalancer)
2. Frontend Pod makes HTTP call to http://backend-service:5000/vote/Dogs
3. CoreDNS resolves "backend-service" → ClusterIP (e.g. 10.100.45.12)
4. ClusterIP routes the request to one of the Backend Pods
5. Backend Pod increments the vote count and returns JSON
6. Frontend Pod sends the response back to the browser
```

> The backend pod IP can change anytime (e.g. after a restart). Because the frontend uses the **service name** and not the pod IP, it always reaches the right pod — this is **service discovery**.

---

## 🧪 Useful kubectl Commands for Demos

```bash
# Watch pods in real time
kubectl get pods -w

# Check logs of the backend pod
kubectl logs -l app=vote-backend

# Check logs of the frontend pod
kubectl logs -l app=vote-frontend

# Describe the ClusterIP service (see Endpoints = backend pod IPs)
kubectl describe service backend-service

# Test backend directly from inside the cluster (exec into a pod)
kubectl exec -it <frontend-pod-name> -- sh
curl http://backend-service:5000/votes

# Scale the backend to 4 replicas
kubectl scale deployment vote-backend --replicas=4

# Delete all resources
kubectl delete -f k8s-manifests/
```

---

## 📊 Service Types — Quick Reference

| Service Type | Accessible From | Used For |
|---|---|---|
| `ClusterIP` | Inside the cluster only | Pod-to-pod communication |
| `NodePort` | Inside VPC (via node IP) | Internal testing |
| `LoadBalancer` | Internet (via AWS ELB) | Public-facing apps |

In this project:
- `backend-service` is **ClusterIP** — the backend is never directly reachable from the internet
- `frontend-service` is **LoadBalancer** — only the frontend is exposed publicly

This is also a **security best practice**: never expose your backend/database pods directly to the internet.

---

## 🐛 Troubleshooting

**Pods are in `ImagePullBackOff` state**
- Check ECR login: `aws ecr get-login-password` and re-authenticate
- Verify the image URI in the deployment YAML matches your ECR repository exactly

**Frontend shows "Could not reach backend"**
- Make sure `02-backend-service.yaml` was applied before the frontend pods started
- Check backend pods are running: `kubectl get pods -l app=vote-backend`
- Exec into a frontend pod and test: `curl http://backend-service:5000/health`

**`kubectl get service frontend-service` shows `<pending>` for EXTERNAL-IP**
- Wait 2–3 minutes for AWS to provision the ELB
- Check your EKS cluster has the AWS Load Balancer Controller installed

---

## 📚 Concepts Covered

- **Docker multi-stage / lightweight images** — `nginx:alpine` and `python:3.12-alpine`
- **ECR** — private container registry on AWS
- **EKS** — managed Kubernetes on AWS
- **Deployments** — manage pod replicas and rolling updates
- **Services** — stable DNS name and load balancing across pods
- **ClusterIP** — virtual IP for internal cluster communication
- **CoreDNS** — built-in Kubernetes DNS that resolves service names to IPs
- **readinessProbe** — ensures traffic only goes to healthy pods

---

## 👨‍💻 Maintained by

**Hiqode DevOps Team**

Part of the Hiqode DevOps Training Series — Docker → ECR → Kubernetes (EKS).
