variable "project_id" { type = string }
variable "region" { default = "us-central1" }

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_compute_instance" "demo_agent" {
  name         = "demo-agent-vm"
  machine_type = "e2-small"
  zone         = "${var.region}-a"
  tags         = ["demo-agent"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }

  network_interface {
    network = "default"
    access_config { }
  }

  metadata = {
    startup-script = file("${path.module}/../gcp-vm-startup.sh")
  }
}

resource "google_compute_firewall" "allow_demo_agent_8000" {
  name    = "allow-demo-agent-8000"
  network = "default"
  target_tags = ["demo-agent"]
  allow {
    protocol = "tcp"
    ports    = ["8000"]
  }
  source_ranges = ["0.0.0.0/0"]
}
