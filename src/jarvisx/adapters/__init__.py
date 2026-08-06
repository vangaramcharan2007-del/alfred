"""Adapters Package for Jarvis X (Layer 5 - Infrastructure Layer).

Exposes zero-fluff cloud federation engines, FinOps resource optimizers, and external adapters.
"""

from jarvisx.adapters.federate import FederationNode, FederationSyncEngine
from jarvisx.adapters.finops import FinOpsOptimizer
from jarvisx.adapters.remote_sync_engine import RemoteSyncEngine

__all__ = ["FederationNode", "FederationSyncEngine", "FinOpsOptimizer", "RemoteSyncEngine"]
