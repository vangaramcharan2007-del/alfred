from __future__ import annotations
import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.coding.architecture_memory import ArchitectureMemory

@dataclass
class ADRRecord:
    decision_id: str
    title: str
    date: str
    status: str  # "Accepted", "Proposed", "Deprecated", "Superseded"
    context: str
    decision: str
    reasoning: str = ""
    consequences: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "title": self.title,
            "date": self.date,
            "status": self.status,
            "context": self.context,
            "decision": self.decision,
            "reasoning": self.reasoning,
            "consequences": self.consequences,
            "alternatives": self.alternatives
        }


class ADRManager:
    def __init__(self, architecture_memory: Optional[ArchitectureMemory] = None):
        self.arch_memory = architecture_memory or ArchitectureMemory()
        self.adrs: Dict[str, ADRRecord] = {}
        self._counter = 1

    async def create_adr(
        self,
        title: str,
        context: str,
        decision: str,
        reasoning: str = "",
        consequences: Optional[List[str]] = None,
        alternatives: Optional[List[str]] = None,
        status: str = "Accepted"
    ) -> ADRRecord:
        decision_id = f"ADR-{self._counter:03d}"
        self._counter += 1
        date_str = datetime.date.today().isoformat()

        record = ADRRecord(
            decision_id=decision_id,
            title=title,
            date=date_str,
            status=status,
            context=context,
            decision=decision,
            reasoning=reasoning,
            consequences=consequences or [],
            alternatives=alternatives or []
        )


        self.adrs[decision_id] = record

        # Persist in ArchitectureMemory
        await self.arch_memory.store_architecture_pattern(
            pattern_name=f"{decision_id}_{title.lower().replace(' ', '_')}",
            details=record.to_dict()
        )

        return record

    def get_adr(self, decision_id: str) -> Optional[ADRRecord]:
        return self.adrs.get(decision_id)

    def list_adrs(self) -> List[ADRRecord]:
        return list(self.adrs.values())

    def format_as_markdown(self, adr: ADRRecord) -> str:
        consequences_md = "\n".join(f"- {c}" for c in adr.consequences) if adr.consequences else "- None specified."
        alternatives_md = "\n".join(f"- {a}" for a in adr.alternatives) if adr.alternatives else "- None specified."

        return (
            f"# {adr.decision_id}: {adr.title}\n\n"
            f"**Date:** {adr.date}  \n"
            f"**Status:** {adr.status}  \n\n"
            f"## Context\n{adr.context}\n\n"
            f"## Decision\n{adr.decision}\n\n"
            f"## Alternatives Considered\n{alternatives_md}\n\n"
            f"## Consequences\n{consequences_md}\n"
        )
