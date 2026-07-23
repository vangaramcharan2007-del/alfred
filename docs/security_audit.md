# Jarvis X - Security Audit

## 1. Local-First Philosophy
Jarvis X defaults to running all ML models (Ollama, PiperTTS, Whisper) entirely locally. No telemetry or PII is sent to external servers unless explicitly configured by the user via the `OMNIROUTE_HOST` gateway.

## 2. API Key Management
The `.env` file must never be committed to source control (ignored in `.gitignore`). All external integrations (e.g. Supabase, ElevenLabs) fetch credentials dynamically via `settings.py`.

## 3. Sandbox Execution
Tools that execute code (e.g., Python scripts or terminal commands) use basic sandboxing constraints to prevent destructive accidental actions. However, **users must run Jarvis X in a non-root environment**, as true sandboxing requires OS-level virtual machines (like WSL or Docker).

## 4. File System Boundaries
The `FileOps` tool restricts operations to the designated Jarvis X workspace, preventing the AI from traversing into sensitive parent directories (e.g. `C:\Windows\` or `/etc/`).
