import psutil
import os
import sys

print("==================================================")
print("             SYSTEM RESOURCE AUDIT")
print("==================================================")

cpu_pct = psutil.cpu_percent(interval=1)
mem = psutil.virtual_memory()
print(f"Total CPU Usage : {cpu_pct}%")
print(f"Total RAM Usage : {mem.used / (1024**3):.2f} GB / {mem.total / (1024**3):.2f} GB ({mem.percent}%)\n")

print("--- Top 10 RAM Consumers ---")
procs = []
for p in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
    try:
        mem_rss = p.info['memory_info'].rss if p.info['memory_info'] else 0
        procs.append((p.info['pid'], p.info['name'], mem_rss, p.info['cpu_percent']))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

procs.sort(key=lambda x: x[2], reverse=True)
for pid, name, rss, cpu in procs[:10]:
    print(f"PID {pid:6d} | {name:25s} | RAM: {rss / (1024**2):7.1f} MB | CPU: {cpu or 0}%")

print("\n--- Python Processes (Jarvis X / Background Tasks) ---")
current_pid = os.getpid()
py_procs = []
for p in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
    try:
        if 'python' in (p.info['name'] or '').lower() and p.info['pid'] != current_pid:
            cmd = " ".join(p.info['cmdline'] or [])
            rss = p.info['memory_info'].rss if p.info['memory_info'] else 0
            py_procs.append((p.info['pid'], cmd, rss))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

for pid, cmd, rss in py_procs:
    cmd_short = (cmd[:70] + '...') if len(cmd) > 70 else cmd
    print(f"PID {pid:6d} | RAM: {rss / (1024**2):6.1f} MB | {cmd_short}")

print("\n--- Ollama / LLM Inference Processes ---")
ollama_procs = []
for p in psutil.process_iter(['pid', 'name', 'memory_info']):
    try:
        if any(k in (p.info['name'] or '').lower() for k in ('ollama', 'llama', 'whisper')):
            rss = p.info['memory_info'].rss if p.info['memory_info'] else 0
            ollama_procs.append((p.info['pid'], p.info['name'], rss))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

for pid, name, rss in ollama_procs:
    print(f"PID {pid:6d} | {name:25s} | RAM: {rss / (1024**2):6.1f} MB")
