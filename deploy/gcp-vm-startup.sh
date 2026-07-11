#!/usr/bin/env bash
# GCP VM startup script for demo-agent
set -euo pipefail
apt-get update && apt-get install -y docker.io docker-compose-plugin
systemctl enable --now docker
mkdir -p /opt/demo-agent
# Pull from Artifact Registry (image pushed by deploy/Dockerfile + cloudbuild/manual push).
# REGION/REPO/IMAGE must match where the backend image was published.
REGION="${REGION:-us-central1}"
AR_REPO="${AR_REPO:-demo-agent}"
IMAGE="${IMAGE:-demo-agent-backend}"
FULL="us-central1-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${IMAGE}:latest"
cat > /opt/demo-agent/docker-compose.yml <<YAML
services:
  backend:
    image: ${FULL}
    ports: ["8000:8000"]
    env_file: .env
YAML
cd /opt/demo-agent && docker compose up -d
