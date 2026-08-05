"""Adapters Package for Jarvis X (Layer 5 - Infrastructure Layer).

Exposes zero-fluff cloud federation engines and external system communication adapters.
"""

from jarvisx.adapters.federate import FederationNode, FederationSyncEngine

__all__ = ["FederationNode", "FederationSyncEngine"]
