# 🐧 JARVIS X: UBUNTU LAB VM DEPLOYMENT & ONBOARDING GUIDE

Follow these 4 simple steps to provision and attach any Ubuntu Virtual Machine, lab workstation, or cluster node into the **Jarvis X Distributed AI Mesh**.

---

## 📋 Prerequisites
* Ubuntu 22.04 / 24.04 LTS (x86_64)
* Python 3.10+
* Dedicated GPU (NVIDIA/AMD) or High-Core CPU
* Tailscale installed on both Master (Yoga 7i) and the VM.

---

## ⚡ Step 1: Install Tailscale & Connect to Tailnet
On the Ubuntu VM:
```bash
# 1. Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# 2. Authenticate to your Tailnet
sudo tailscale up

# 3. Check your VM's Tailscale IP
tailscale ip -4
# Example Output: 100.88.19.42
```

---

## 🦙 Step 2: Install Ollama & Pull Desired Models
```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Ensure Ollama listens on Tailscale network interface
sudo mkdir -p /etc/systemd/system/ollama.service.d
echo '[Service]' | sudo tee /etc/systemd/system/ollama.service.d/environment.conf
echo 'Environment="OLLAMA_HOST=0.0.0.0:11434"' | sudo tee -a /etc/systemd/system/ollama.service.d/environment.conf
sudo systemctl daemon-reload
sudo systemctl restart ollama

# 3. Pull required model families
ollama pull qwen2.5-coder:1.5b
ollama pull qwen2.5-coder:7b
ollama pull llama3.2:latest
```

---

## 🔑 Step 3: Issue an Enrollment Token on Master Coordinator
On Master (Lenovo Yoga 7i):
```powershell
# Open Jarvis X FastMCP or run Python token generator:
python -c "from jarvisx.mesh.auto_enrollment import TokenSecurityManager; print('TOKEN:', TokenSecurityManager().issue_token(label='LAB-VM-01'))"
# Example Output: TOKEN: 7f8a12b394c8e71...
```

---

## 🚀 Step 4: Run the One-Liner Worker Bootstrapper
On the Ubuntu VM:
```bash
# Download and execute the zero-dependency bootstrapper
python3 scripts/mesh_join_worker.py \
    --master 100.105.164.83 \
    --worker-id LAB-VM-01 \
    --name "Lab Ubuntu VM 01 (RTX 4070)" \
    --ip $(tailscale ip -4) \
    --token <YOUR_ENROLLMENT_TOKEN>
```

---

## 🟢 Verification in Jarvis X Dashboard
Once executed, the VM will:
1. Probe its local hardware & GPU specs.
2. Run synthetic calibration on `qwen2.5-coder:1.5b` (measuring local TTFT and tokens/sec).
3. Validate its one-time token with Master.
4. Appear in the **Jarvis X AI Mesh Observability Dashboard** as `🟢 ONLINE`.
5. Immediately begin accepting distributed inference workloads!
