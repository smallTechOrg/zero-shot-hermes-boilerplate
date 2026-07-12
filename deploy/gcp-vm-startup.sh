#!/usr/bin/env bash
# GCP VM startup script for demo-agent
set -euo pipefail
apt-get update && apt-get install -y docker.io docker-compose
systemctl enable --now docker
mkdir -p /opt/demo-agent
# Pull from Artifact Registry (image pushed by deploy/Dockerfile + cloudbuild/manual push).
# REGION/AR_REPO/IMAGE can be overridden via instance metadata if needed.
REGION="${REGION:-us-central1}"
AR_REPO="${AR_REPO:-demo-agent}"
IMAGE="${IMAGE:-demo-agent-backend}"
FULL="us-central1-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${IMAGE}:latest"
# Default .env (stub mode). Add LLM_API_KEY / GEMINI_API_KEY here for live mode.
if [ ! -f /opt/demo-agent/.env ]; then
  cat > /opt/demo-agent/.env <<ENV
DATABASE_URL=sqlite:///./data/app.db
LLM_PROVIDER=gemini
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
LLM_MODEL=gemini-2.5-flash
ENV
fi
cat > /opt/demo-agent/docker-compose.yml <<YAML
services:
  backend:
    image: ${FULL}
    ports: ["8000:8000"]
    env_file: .env
YAML
cd /opt/demo-agent && docker-compose up -d
