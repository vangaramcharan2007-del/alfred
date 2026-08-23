# 🐧 JARVIS X: LAB-PROOF UBUNTU VM DEPLOYMENT & ONBOARDING GUIDE

> **Status:** Deployment-Ready for Controlled Lab Testing  
> **Prerequisites Checklist:** Ubuntu 22.04/24.04 LTS, Tailscale, Ollama, Python 3.10+, and an enrollment token.

---

## 🛠️ Step 0: Ensure Essential Networking Tools Exist
Fresh minimal Ubuntu VM images in campus labs often lack `curl`. Run this first:
```bash
sudo apt update && sudo apt install -y curl wget git python3 python3-pip python3-venv
```

---

## ⚡ Step 1: Install Tailscale & Connect to Tailnet

### Option A: Standard Installer (if `curl` works)
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

### Option B: `wget` Fallback (if `curl` fails or hangs)
```bash
wget -qO- https://tailscale.com/install.sh | sh
```

### Option C: Direct APT Repository (if script pipes fail)
```bash
sudo mkdir -p --mode=0755 /etc/apt/keyrings
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/$(lsb_release -cs).noarmor.gpg | sudo tee /etc/apt/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/$(lsb_release -cs).tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt update && sudo apt install -y tailscale
```

### Connect to Tailnet:
```bash
sudo tailscale up
# Verify your Tailscale IPv4 address:
tailscale ip -4
# e.g., 100.88.19.42
```

---

## 🦙 Step 2: Install Ollama (Secure Localhost Loopback)

### Install & Start Ollama:
```bash
# Using curl:
curl -fsSL https://ollama.com/install.sh | sh
# OR using wget:
wget -qO- https://ollama.com/install.sh | sh
```
> [!NOTE]
> **Security Best Practice:** Ollama stays bound to `127.0.0.1:11434` (localhost loopback only). It is **never exposed on 0.0.0.0/LAN**. The `Jarvis Worker` agent runs locally on the VM, communicates with Ollama over loopback, and exposes the authenticated Tailscale interface to Master.

### Pull the lightweight, high-performance base model:
```bash
ollama pull qwen2.5-coder:1.5b
# Optional (if GPU VRAM > 6GB):
ollama pull qwen2.5-coder:7b
```


---

## 🔑 Step 3: Issue an Enrollment Token on Master (Yoga 7i)
On your Yoga 7i laptop, generate a one-time single-use HMAC token:
```powershell
python -c "from jarvisx.mesh.auto_enrollment import TokenSecurityManager; print('TOKEN:', TokenSecurityManager().issue_token(label='LAB-VM-01'))"
# Output example: TOKEN: a89f14b29c017d...
```

---

## 🚀 Step 4: Run the One-Liner Worker Bootstrapper
On the Ubuntu VM:
```bash
# Clone the Alfred/Jarvis repository or copy the standalone bootstrapper:
git clone https://github.com/vangaramcharan2007-del/alfred.git /tmp/jarvis-worker
cd /tmp/jarvis-worker

# Run the bootstrapper:
python3 scripts/mesh_join_worker.py \
    --master 100.105.164.83 \
    --worker-id LAB-VM-01 \
    --name "Lab Ubuntu VM 01 (RTX 4070)" \
    --ip $(tailscale ip -4) \
    --token <YOUR_ENROLLMENT_TOKEN>
```

---

## 🟢 Step 5: Verification on Master Dashboard
Look at the **Jarvis X AI Mesh Observability Hub** on your Yoga 7i:
1. `LAB-VM-01` will transition from `🟡 STANDBY` to `🟢 ONLINE`.
2. Calibration will report: `TTFT: ~30-45ms`, `TPS: ~40-60 tok/s` (depending on VM GPU).
3. The adaptive scheduler will immediately start offloading coding and research tasks to `LAB-VM-01`!
