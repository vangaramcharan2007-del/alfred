#!/bin/bash
set -e

echo "Starting Jarvis X System..."
# Run any database migrations if necessary (we use SQLite and auto-create)
# Start the main API
exec python -m jarvisx --serve --host 0.0.0.0 --port 8765
