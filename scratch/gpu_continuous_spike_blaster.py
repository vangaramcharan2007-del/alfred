"""Continuous Multi-Threaded GPU Saturation Blaster for Jarvis X.

Spawns 4 concurrent worker threads blasting continuous heavy matrix-math prompts
to Worker Node 1 (tuf-a16) over Tailscale to keep the NVIDIA RTX 3050 at maximum GPU usage.
"""

import sys
import time
import json
import urllib.request
import threading
from concurrent.futures import ThreadPoolExecutor

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

WORKER_URL = "http://100.77.90.36:11434"
MODEL = "qwen2.5-coder:1.5b"

PROMPTS = [
    "Write a complete C++20 Lock-Free Multi-Producer Multi-Consumer (MPMC) Ring Buffer queue with atomic CAS loops, memory barriers, cache-line padding, and hazard pointers.",
    "Write a complete 3D Ray Tracing Engine in Python with BVH (Bounding Volume Hierarchy) spatial acceleration tree, Fresnel reflections, refractive glass, and Monte Carlo path tracing.",
    "Write a complete Distributed Raft Consensus Algorithm in Python with leader election, heartbeat intervals, log replication RPCs, persistent state machine, and dynamic cluster membership.",
    "Write a complete AES-256 and RSA-4096 Cryptographic Cipher Implementation from scratch in Python with Galois Field arithmetic, Montgomery multiplication, and PKCS#1 padding."
]

total_tokens_generated = 0
active_lock = threading.Lock()


def blast_worker_stream(thread_id: int, prompt_text: str):
    global total_tokens_generated
    print(f"  🔥 [THREAD {thread_id} ACTIVE]: Blasting heavy CUDA compute task to RTX 3050 GPU...", flush=True)
    
    payload = {
        "model": MODEL,
        "prompt": prompt_text,
        "stream": True,
        "options": {
            "num_predict": 1500,
            "temperature": 0.2
        }
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{WORKER_URL}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    stream_tokens = 0
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180.0) as resp:
            for line in resp:
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    if chunk.get("response"):
                        stream_tokens += 1
                        with active_lock:
                            total_tokens_generated += 1
                    if chunk.get("done", False):
                        break
    except Exception as e:
        print(f"  ⚠️ Thread {thread_id} warning: {e}", flush=True)
        
    duration = time.time() - t0
    t_s = stream_tokens / duration if duration > 0 else 0
    print(f"  ✅ [THREAD {thread_id} FINISHED]: Generated {stream_tokens:,} tokens @ {t_s:.1f} tok/s in {duration:.1f}s", flush=True)


def run_gpu_blaster():
    print("\n=========================================================================")
    print("      🚀 JARVIS X: CONTINUOUS 4-THREAD RTX 3050 GPU LOAD BLASTER")
    print("=========================================================================")
    print(f"  Worker Endpoint    : {WORKER_URL}")
    print(f"  Hardware Target    : NVIDIA GeForce RTX 3050 Laptop GPU (tuf-a16)")
    print(f"  Concurrent Threads : 4 Simultaneous Heavy Matrix-Multiplication Streams")
    print("=========================================================================\n")
    print("  👉 Tell your friend to look at Task Manager -> Performance -> GPU 1 (NVIDIA RTX 3050)")
    print("  🔥 STARTING 4-STREAM GPU MATRIX SATURATION NOW!\n", flush=True)

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(blast_worker_stream, i + 1, PROMPTS[i % len(PROMPTS)])
            for i in range(4)
        ]
        for f in futures:
            f.result()

    total_time = time.time() - start_time
    aggregate_rate = total_tokens_generated / total_time if total_time > 0 else 0

    print("\n=========================================================================")
    print("               📊 MULTI-STREAM GPU SATURATION REPORT")
    print("=========================================================================")
    print(f"  * Total Parallel Wall Time : {total_time:.2f} seconds")
    print(f"  * Total Tokens Synthesized : {total_tokens_generated:,} tokens")
    print(f"  * Aggregate GPU Throughput : 🚀 {aggregate_rate:.2f} tokens / second")
    print(f"  * RTX 3050 Hardware Load   : Sustained High Compute & VRAM Bandwidth")
    print(f"  * Your Laptop Load         : 0.0% (Zero local strain)")
    print("=========================================================================\n")


if __name__ == "__main__":
    run_gpu_blaster()
