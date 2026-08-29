#!/usr/bin/env bash
# ==============================================================================
# JARVIS X: 1-CLICK PHYSICAL LAB VM DEPLOYMENT SCRIPT (LAB-VM-01)
# Installs Tailscale Mesh, NVIDIA GPU CUDA Support, Ollama & 24/7 Systemd Service
# ==============================================================================

set -e

echo "=================================================================="
echo " [JARVIS X] DEPLOYING PHYSICAL LAB COMPUTE NODE (LAB-VM-01)"
echo "=================================================================="

# 1. Update and install base prerequisites
echo "[1/5] Updating system packages & dependencies..."
sudo apt-get update -y && sudo apt-get install -y curl wget git htop ufw net-tools

# 2. Setup Tailscale Secure WireGuard Mesh
echo "[2/5] Installing and configuring Tailscale..."
if ! command -v tailscale &> /dev/null; then
    curl -fsSL https://tailscale.com/install.sh | sh
fi
sudo tailscale up --accept-routes --hostname=lab-vm-01

# 3. Setup Ollama GPU Compute Engine
echo "[3/5] Installing Ollama Compute Engine..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 4. Pull High-Speed Inference Models
echo "[4/5] Pulling distributed worker models..."
ollama serve &
sleep 3
ollama pull qwen2.5-coder:1.5b
ollama pull deepseek-r1:1.5b

# 5. Create 24/7 Systemd Worker Service
echo "[5/5] Configuring 24/7 systemd worker daemon..."
sudo bash -c 'cat <<EOF > /etc/systemd/system/jarvisx-worker.service
[Unit]
Description=Jarvis X Distributed GPU Worker Daemon
After=network.target ollama.service

[Service]
Type=simple
User=$USER
Environment="OLLAMA_HOST=0.0.0.0:11434"
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable --now jarvisx-worker

IP_ADDR=$(tailscale ip -4 || hostname -I | awk '{print $1}')

echo "=================================================================="
echo " [OK] LAB-VM-01 DEPLOYED SUCCESSFULLY!"
echo " Tailscale Node IP: $IP_ADDR"
echo " Ollama Endpoint  : http://$IP_ADDR:11434"
echo "=================================================================="
