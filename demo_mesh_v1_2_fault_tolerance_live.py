"""
Live Demonstration & 5-Mode Chaos Recovery Benchmark of Distributed AI Mesh v1.2.
Demonstrates:
1. 5 Injected Chaos Failure Modes (Worker Crash, Network Drop, Bad Model, Security Rejection, Timeout).
2. Real-Time Token Generation & Latency Telemetry (TTFT, tokens/sec, prompt tokens).
3. Self-Healing Failover, Dynamic Model Fallback & Automated Prompt Sanitization.
4. Multi-Node Observability Dashboard across all 5 Mesh Workers.
5. Tamper-Evident SHA-256 Cryptographic Audit Proofs.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root / "friday-tony-stark-demo"))

from jarvisx.mesh.fault_tolerant_queue import FailureMode, FaultJobState, FaultTolerantJob, FaultTolerantMeshManager


def run_live_mesh_v1_2_demo():
    print("=" * 110)
    print(" [JARVIS X] DISTRIBUTED AI MESH v1.2: REAL TELEMETRY & 5-MODE CHAOS FAULT TOLERANCE")
    print("=" * 110)

    manager = FaultTolerantMeshManager()

    # 1. Define 10 real mission tasks with injected chaos on first 5 jobs
    jobs = [
        FaultTolerantJob(
            job_id="job_01",
            task_name="auth_middleware",
            prompt="Implement secure JWT auth middleware with token revocation.",
            target_model="qwen2.5-coder:7b",
            injected_failure=FailureMode.WORKER_CRASH,
        ),
        FaultTolerantJob(
            job_id="job_02",
            task_name="cache_sync",
            prompt="Build high-throughput Redis buffer for microgrid telemetry.",
            target_model="qwen2.5-coder:7b",
            injected_failure=FailureMode.NETWORK_TIMEOUT,
        ),
        FaultTolerantJob(
            job_id="job_03",
            task_name="sql_migrator",
            prompt="Generate zero-downtime SQLite migration schema.",
            target_model="nonexistent-model:99b",
            injected_failure=FailureMode.INVALID_MODEL,
        ),
        FaultTolerantJob(
            job_id="job_04",
            task_name="api_gateway",
            prompt="Create payment gateway client with auth credentials.",
            target_model="qwen2.5-coder:7b",
            injected_failure=FailureMode.SECURITY_REJECTION,
        ),
        FaultTolerantJob(
            job_id="job_05",
            task_name="vector_indexer",
            prompt="Index 1,000 spatial telemetry frames into ChromaDB.",
            target_model="qwen2.5-coder:7b",
            injected_failure=FailureMode.INFERENCE_TIMEOUT,
        ),
        # Regular successful baseline jobs
        FaultTolerantJob(
            job_id="job_06",
            task_name="event_dispatcher",
            prompt="Build async event bus with priority queues.",
            target_model="qwen2.5-coder:7b",
        ),
        FaultTolerantJob(
            job_id="job_07",
            task_name="hud_renderer",
            prompt="Render 60fps holographic aperture HUD canvas.",
            target_model="qwen2.5-coder:7b",
        ),
        FaultTolerantJob(
            job_id="job_08",
            task_name="health_probe",
            prompt="Probe Tailscale node latency and GPU temperature.",
            target_model="qwen2.5-coder:7b",
        ),
        FaultTolerantJob(
            job_id="job_09",
            task_name="audit_stargazer",
            prompt="Verify SHA-256 hash chains across SQLite ledgers.",
            target_model="qwen2.5-coder:7b",
        ),
        FaultTolerantJob(
            job_id="job_10",
            task_name="release_gate",
            prompt="Format semantic release changelog and bump version tag.",
            target_model="qwen2.5-coder:7b",
        ),
    ]

    print(f"\n[STEP 1] [+] Dispatching 10 Distributed Jobs with Injected 5-Mode Chaos Suite...")
    print(f"  [+] Injected Failures: [job_01: CRASH] [job_02: TIMEOUT] [job_03: BAD_MODEL] [job_04: REJECT] [job_05: SLA_TIMEOUT]")

    report = manager.run_chaos_test_suite(jobs)

    # 2. Print Chaos Recovery Log
    print("\n[STEP 2] [+] Inspecting Self-Healing Chaos Recovery Actions:\n")
    print(f"{'JOB ID':<8} {'FAILURE INJECTED':<22} {'FINAL WORKER':<16} {'RETRIES':<8} {'SELF-HEALING ACTION'}")
    print("-" * 110)
    for rec in report.fault_recovery_log:
        print(f"{rec['job_id']:<8} {rec['failure_mode']:<22} {rec['final_worker']:<16} {rec['retries']:<8} {rec['recovery_action']}")

    assert len(report.fault_recovery_log) == 5, f"Expected 5 recoveries, got {len(report.fault_recovery_log)}"
    assert report.completed_jobs == 10, f"Expected 10/10 completed jobs, got {report.completed_jobs}"
    assert report.failed_jobs == 0, f"Expected 0 failed jobs, got {report.failed_jobs}"

    # 3. Print Real Inference Telemetry & Token Throughput
    print("\n[STEP 3] [+] Real Inference Telemetry & Token Generation Breakdown:\n")
    print(f"{'JOB ID':<8} {'WORKER':<14} {'TTFT':<10} {'LATENCY':<12} {'TOKENS':<10} {'TPS':<12} {'REVIEW':<10} {'AUDIT HASH'}")
    print("-" * 110)
    for j in jobs:
        tel = j.telemetry
        if tel:
            ttft_str = f"{tel.ttft_ms:.1f}ms"
            lat_str = f"{tel.total_latency_ms:.1f}ms"
            tps_str = f"{tel.tokens_per_sec:.1f} tok/s"
            hash_str = j.audit_hash[:12] + "..." if j.audit_hash else "-"
            print(f"{j.job_id:<8} {tel.worker_id:<14} {ttft_str:<10} {lat_str:<12} {tel.tokens_generated:<10} {tps_str:<12} {j.review_decision:<10} {hash_str}")

    # 4. Multi-Node Cluster Observability Dashboard
    print("\n[STEP 4] [+] AI Mesh Cluster Observability & Node Health Summary:\n")
    print("=" * 110)
    print(f" 🌐 JARVIS X: AI MESH v1.2 CLUSTER OBSERVABILITY DASHBOARD")
    print(f" Total Workload: 10 Jobs | Completed: {report.completed_jobs}/10 | Total Cluster Tokens: {report.aggregate_tokens} tok")
    print(f" Wall Clock Time: {report.wall_clock_time_ms:.2f}ms | Cluster Generation Throughput: {report.cluster_tokens_per_sec} tok/sec")
    print("-" * 110)
    print(f"{'NODE ID':<16} {'COMPLETED':<12} {'TOKENS GEN':<14} {'AVG LATENCY':<16} {'AVG TPS':<14} {'HEALTH STATE'}")
    print("-" * 110)
    for node, stats in report.node_telemetry_summary.items():
        if stats["completed"] > 0:
            avg_lat = f"{stats['total_lat_ms'] / stats['completed']:.1f}ms"
            avg_tps = f"{sum(stats['tps_list']) / len(stats['tps_list']):.1f} tok/s" if stats["tps_list"] else "0.0"
            print(f"{node:<16} {stats['completed']:<12} {stats['total_tokens']:<14} {avg_lat:<16} {avg_tps:<14} 🟢 HEALTHY (PROVED)")
        else:
            print(f"{node:<16} {stats['completed']:<12} {stats['total_tokens']:<14} {'-':<16} {'-':<14} 🟡 STANDBY")
    print("=" * 110)

    # 5. Verify Cryptographic Audit Ledger
    integrity = manager.audit_ledger.verify_integrity()
    print(f"\n[STEP 5] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 110)
    print(" [OK] DISTRIBUTED AI MESH v1.2: REAL TELEMETRY & 5-MODE CHAOS RECOVERY FULLY PROVEN!")
    print("=" * 110)


if __name__ == "__main__":
    run_live_mesh_v1_2_demo()
