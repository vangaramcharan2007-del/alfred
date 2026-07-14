# Antigravity Node 001 - Deployment Instructions

## Prerequisites
* Python 3.11+
* SQLite (bundled with Python)

## Installation
1. Navigate to the `project-jarvis-x` root directory.
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn psutil
   ```
   *(Note: `psutil` and `fastapi` are optional for the script to run in fallback/mock mode, but highly recommended for full functionality).*

## Running the Node
Start the bootstrap runtime using standard python module execution or uvicorn:

```bash
# Direct python execution
python -m jarvisx.node_runtime.runtime_bootstrap

# Or via uvicorn
uvicorn jarvisx.node_runtime.runtime_bootstrap:app --host 127.0.0.1 --port 8000
```

## Validation
To verify health, visit:
`http://127.0.0.1:8000/health`
