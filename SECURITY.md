# Security & Trust Policy — Jarvis X v1.0

Jarvis X v1.0 operates on a **Default-Denial Zero-Trust Architecture**.

---

## 🔒 Security Principles

1. **Default-Denial:** Unknown actors and scopes are rejected by default.
2. **Multi-Factor Risk Scoring:**
   $$\text{Risk Score} = \text{Base} + \text{Sensitivity} + \text{Privilege} + \text{Blast Radius} + \text{Irreversibility}$$
   - Actions with risk $\ge 70$ require explicit confirmation.
3. **AES-GCM 256-bit Secret Vault:**
   - Keys derived using PBKDF2 (`100,000` iterations).
   - Zero plaintext token leakage in memory, logs, or UI outputs.
4. **Cryptographic SHA-256 Merkle Audit Chain:**
   - Append-only database records linked cryptographically.
   - Any manual database tampering breaks chain verification.
5. **Hardware Sandbox Guardrails:**
   - Strict path boundary clamping prevents directory traversal escapes (`../../`).
   - Destructive command patterns (`rm -rf /`, `format c:`) are unconditionally blocked.
