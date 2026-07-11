#!/usr/bin/env bash
# GCP VM startup script for demo-agent
set -euo pipefail
apt-get update && apt-get install -y docker.io docker-compose-plugin
systemctl enable --now docker
mkdir -p /opt/demo-agent
cat > /opt/demo-agent/docker-compose.yml <<'YAML'
services:
  backend:
    image: gcr.io/${PROJECT_ID}/demo-agent-backend:latest
    ports: ["8000:8000"]
    env_file: .env
YAML
cd /opt/demo-agent && docker compose up -d
