# Debugging

Project Jarvis X is designed to make failures traceable.

## Structured logs

The CLI writes JSON lines to `var/log/jarvisx.jsonl`.

Each record includes:

- `timestamp`
- `level`
- `message`
- `trace_id`
- contextual fields such as `agent_id`, `event_type`, or `tool_name`

The Alfred REST API also writes `alfred.api.request` records for local HTTP calls. API clients should pass a stable trace ID when they need to correlate a mobile request with Hermes events and agent/tool logs.

## Health checks

`HealthMonitor` runs independent checks for Hermes, the agent registry, and tools. New adapters should register their own health checks before being used by an agent.

The Memory Tool health check verifies that the configured Obsidian vault exists and that required folders can be created or repaired.

## Memory logs

Memory reads and writes are logged as structured JSON records:

- `memory.write`
- `memory.read`
- `memory.lookup.failed`

Each Memory Agent call passes the Hermes trace ID into the tool so failed lookups and vault errors can be correlated with the originating user task.

## Failure reports

Use `FailureReport.from_exception(...)` to normalize errors:

```python
report = FailureReport.from_exception(
    exc,
    agent_id="debug",
    tool_name="file_tool",
    proposed_fix="Check file permissions and retry.",
)
```

Reports are serializable dictionaries and can be routed to the Debug Agent.
