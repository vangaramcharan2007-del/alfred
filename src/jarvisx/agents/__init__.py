"""Operational Agent Workforce and Registry for Jarvis X (Layer 3).

Exposes standard agent frameworks, discovery catalogs, and specialized worker implementations.
"""

from jarvisx.agents.base import OperationalAgent
from jarvisx.agents.registry import AgentRegistry
from jarvisx.agents.research import ResearchAgent
from jarvisx.agents.testing import TestingAgent
from jarvisx.agents.coding import CodingAgent
from jarvisx.agents.productivity import ProductivityAgent
from jarvisx.agents.guardian import GuardianAgent
from jarvisx.agents.devops import DevOpsAgent

__all__ = [
    "OperationalAgent",
    "AgentRegistry",
    "ResearchAgent",
    "TestingAgent",
    "CodingAgent",
    "ProductivityAgent",
    "GuardianAgent",
    "DevOpsAgent",
]
