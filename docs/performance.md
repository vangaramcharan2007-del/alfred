# Jarvis X - Performance Tuning

## Latency Budgets
- **Voice Activation:** < 300ms
- **TTS Synthesis:** < 1000ms (Streamed)
- **Local LLM Routing:** < 500ms
- **Memory Retrieval:** < 100ms (via Local SQLite)

## OmniRoute Streaming
To ensure conversational fluidity, the system uses asynchronous chunk streaming (`stream_chat`) in `llm_router.py`. This ensures voice output begins processing the first token without waiting for the full generation to complete.

## Resource Management
The `diagnose.py` checks for excessive resource consumption. Jarvis X unloads unused skills dynamically. Long-running missions are shifted to background tasks and polled lazily.
