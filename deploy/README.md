# Deploy — demo-agent

One-command-ish path to a single GCP VM running the full stack.

## What ships
- `deploy/Dockerfile` — multi-stage backend image (serves API on :8000)
- `deploy/gcp-vm-startup.sh` — boots the VM, installs Docker, runs compose
- `deploy/terraform/main.tf` — e2e VM + firewall rule (Cloud SQL optional)
- `deploy/cloudbuild.yaml` — builds + pushes image to Artifact Registry

## Quick path (manual VM)
1. `gcloud compute instances create demo-agent-vm --machine-type=e2-small --metadata-from-file=startup-script=deploy/gcp-vm-startup.sh`
2. `gcloud compute firewall-rules create allow-demo-agent-8000 --allow tcp:8000 --target-tags=demo-agent`
3. Open `http://<vm-ip>:8000/health`

## Terraform
```
cd deploy/terraform
terraform init && terraform apply -var project_id=<YOUR_GCP_PROJECT>
```

Secrets stay in `.env`; never commit. Set `DATABASE_URL` to Cloud SQL when used.
