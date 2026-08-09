"""Knowledge Domain Models for Jarvis X Knowledge Acquisition & Obsidian Vault Layer."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class KnowledgeSensitivity(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    PRIVATE_NOTES = "PRIVATE_NOTES"
    SENSITIVE_MEMORY = "SENSITIVE_MEMORY"


class VaultCategory(str, Enum):
    INBOX = "00_Inbox"
    GOALS = "01_Goals"
    LEARNING = "02_Learning"
    PROJECTS = "03_Projects"
    REFERENCES = "04_References"
    MEMORY = "05_Memory"
    GENERAL = "General"


@dataclass
class DocumentMetadata:
    source_file: str
    source_type: str  # "markdown", "pdf", "text", "web"
    category: VaultCategory
    sensitivity: KnowledgeSensitivity
    content_hash: str
    title: str = ""
    tags: List[str] = field(default_factory=list)
    wikilinks: List[str] = field(default_factory=list)
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    file_size_bytes: int = 0
    created_at: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_file": self.source_file,
            "source_type": self.source_type,
            "category": self.category.value if isinstance(self.category, VaultCategory) else str(self.category),
            "sensitivity": self.sensitivity.value if isinstance(self.sensitivity, KnowledgeSensitivity) else str(self.sensitivity),
            "content_hash": self.content_hash,
            "title": self.title,
            "tags": self.tags,
            "wikilinks": self.wikilinks,
            "frontmatter": self.frontmatter,
            "file_size_bytes": self.file_size_bytes,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
        }


@dataclass
class KnowledgeChunk:
    id: str
    source_file: str
    chunk_index: int
    content: str
    heading_path: str  # e.g., "# DSA > ## Binary Trees > ### Traversals"
    content_hash: str
    tags: List[str] = field(default_factory=list)
    wikilinks: List[str] = field(default_factory=list)
    sensitivity: KnowledgeSensitivity = KnowledgeSensitivity.INTERNAL
    category: VaultCategory = VaultCategory.GENERAL
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_file": self.source_file,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "heading_path": self.heading_path,
            "content_hash": self.content_hash,
            "tags": self.tags,
            "wikilinks": self.wikilinks,
            "sensitivity": self.sensitivity.value if isinstance(self.sensitivity, KnowledgeSensitivity) else str(self.sensitivity),
            "category": self.category.value if isinstance(self.category, VaultCategory) else str(self.category),
            "created_at": self.created_at,
        }


@dataclass
class SearchResult:
    chunk_id: str
    source_file: str
    content: str
    heading_path: str
    score: float
    relevance_reason: str
    sensitivity: KnowledgeSensitivity
    tags: List[str] = field(default_factory=list)
    provenance_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source_file": self.source_file,
            "content": self.content,
            "heading_path": self.heading_path,
            "score": round(self.score, 4),
            "relevance_reason": self.relevance_reason,
            "sensitivity": self.sensitivity.value if isinstance(self.sensitivity, KnowledgeSensitivity) else str(self.sensitivity),
            "tags": self.tags,
            "provenance_hash": self.provenance_hash,
        }


@dataclass
class IngestionReport:
    total_files_scanned: int = 0
    files_indexed: int = 0
    files_skipped_unchanged: int = 0
    files_deleted_purged: int = 0
    total_chunks_created: int = 0
    duration_sec: float = 0.0
    status: str = "SUCCESS"
    details: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_files_scanned": self.total_files_scanned,
            "files_indexed": self.files_indexed,
            "files_skipped_unchanged": self.files_skipped_unchanged,
            "files_deleted_purged": self.files_deleted_purged,
            "total_chunks_created": self.total_chunks_created,
            "duration_sec": round(self.duration_sec, 3),
            "status": self.status,
            "details": self.details,
        }
