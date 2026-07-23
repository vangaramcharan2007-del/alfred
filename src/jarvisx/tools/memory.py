from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Iterable, Optional
from uuid import uuid4
import functools

from jarvisx.core.health import HealthStatus
from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.base import BaseTool, ToolResult


SUPPORTED_CATEGORIES = {
    "preference": "Preferences",
    "project": "Projects",
    "conversation": "Conversations",
    "architecture": "Architecture",
    "general": "Scratchpad",
}
REQUIRED_DIRECTORIES = (
    "Daily",
    "Projects",
    "Preferences",
    "Conversations",
    "Architecture",
    "Scratchpad",
)


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    content: str
    category: str
    created_at: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category,
            "created_at": self.created_at,
            "path": self.path,
        }


class LocalMemoryTool(BaseTool):
    name = "memory"

    def __init__(
        self,
        *,
        vault_path: Optional[Path] = None,
        logger: Optional[StructuredLogger] = None,
    ) -> None:
        self.vault_path = Path(vault_path or "var/obsidian-vault")
        self.logger = logger or StructuredLogger()
        self._recover_vault()

    def save_memory(
        self,
        text: str,
        category: str,
        *,
        trace_id: Optional[str] = None,
    ) -> ToolResult:
        clean_text = text.strip()
        normalized_category = self._normalize_category(category)
        if not normalized_category:
            self._log_failed_lookup("unsupported_category", trace_id=trace_id, category=category)
            return ToolResult(
                success=False,
                message=f"Unsupported memory category: {category}.",
                data={"supported_categories": sorted(SUPPORTED_CATEGORIES)},
            )
        if not clean_text:
            self.logger.write(
                "warning",
                "memory.write.failed",
                trace_id=trace_id,
                category=normalized_category,
                reason="empty_text",
            )
            return ToolResult(success=False, message="Memory content was empty.")

        try:
            self._recover_vault()
            record_id = uuid4().hex
            created_at = _utc_now()
            file_path = self._category_dir(normalized_category) / self._filename(
                created_at=created_at,
                text=clean_text,
                record_id=record_id,
            )
            record = MemoryRecord(
                id=record_id,
                content=clean_text,
                category=normalized_category,
                created_at=created_at,
                path=_relative_vault_path(file_path, self.vault_path),
            )
            file_path.write_text(_render_memory_markdown(record), encoding="utf-8")
            self.logger.write(
                "info",
                "memory.write",
                trace_id=trace_id,
                category=normalized_category,
                path=record.path,
            )
            return ToolResult(
                success=True,
                message="Memory stored.",
                data={"record": record.to_dict()},
            )
        except Exception as exc:
            self.logger.write(
                "error",
                "memory.write.failed",
                trace_id=trace_id,
                category=normalized_category,
                reason=str(exc),
            )
            return ToolResult(success=False, message=f"Memory write failed: {exc}")

    def search_memory(
        self,
        query: str,
        *,
        trace_id: Optional[str] = None,
        limit: int = 10,
    ) -> ToolResult:
        tokens = _keywords(query)
        if not tokens:
            self._log_failed_lookup("empty_query", trace_id=trace_id)
            return ToolResult(success=False, message="Search query was empty.")

        try:
            self._recover_vault()
            limited = self._cached_search(query, limit)
            if not limited:
                self._log_failed_lookup("no_matches", trace_id=trace_id, query=query)
            self.logger.write(
                "info",
                "memory.read",
                trace_id=trace_id,
                operation="search_memory",
                query=query,
                result_count=len(limited),
            )
            return ToolResult(
                success=True,
                message=f"Found {len(limited)} memory record(s).",
                data={"records": limited},
            )
        except Exception as exc:
            self._log_failed_lookup("read_error", trace_id=trace_id, query=query, reason=str(exc))
            return ToolResult(success=False, message=f"Memory search failed: {exc}")

    @functools.lru_cache(maxsize=128)
    def _cached_search(self, query: str, limit: int) -> ToolResult:
        tokens = _keywords(query)
        matches: list[dict[str, object]] = []
        for file_path in self._markdown_files():
            text = file_path.read_text(encoding="utf-8")
            haystack = text.lower()
            matched_tokens = [token for token in tokens if token in haystack]
            if len(matched_tokens) == len(tokens):
                matches.append(
                    {
                        "path": _relative_vault_path(file_path, self.vault_path),
                        "category": self._category_from_path(file_path),
                        "matches": matched_tokens,
                        "score": len(matched_tokens),
                        "content": text,
                    }
                )
        matches.sort(key=lambda item: (-int(item["score"]), str(item["path"])))
        return matches[:limit]

    def append_daily_note(self, text: str, *, trace_id: Optional[str] = None) -> ToolResult:
        clean_text = text.strip()
        if not clean_text:
            self.logger.write(
                "warning",
                "memory.write.failed",
                trace_id=trace_id,
                operation="append_daily_note",
                reason="empty_text",
            )
            return ToolResult(success=False, message="Daily note content was empty.")
        try:
            self._recover_vault()
            note_path = self._daily_note_path()
            self._ensure_daily_note(note_path)
            timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
            with note_path.open("a", encoding="utf-8") as handle:
                handle.write(f"\n- **{timestamp}** {clean_text}\n")
            relative_path = _relative_vault_path(note_path, self.vault_path)
            self.logger.write(
                "info",
                "memory.write",
                trace_id=trace_id,
                operation="append_daily_note",
                path=relative_path,
            )
            return ToolResult(
                success=True,
                message="Daily note updated.",
                data={"path": relative_path, "content": note_path.read_text(encoding="utf-8")},
            )
        except Exception as exc:
            self.logger.write(
                "error",
                "memory.write.failed",
                trace_id=trace_id,
                operation="append_daily_note",
                reason=str(exc),
            )
            return ToolResult(success=False, message=f"Daily note write failed: {exc}")

    def get_daily_note(self, *, trace_id: Optional[str] = None) -> ToolResult:
        try:
            self._recover_vault()
            note_path = self._daily_note_path()
            self._ensure_daily_note(note_path)
            relative_path = _relative_vault_path(note_path, self.vault_path)
            content = note_path.read_text(encoding="utf-8")
            self.logger.write(
                "info",
                "memory.read",
                trace_id=trace_id,
                operation="get_daily_note",
                path=relative_path,
            )
            return ToolResult(
                success=True,
                message="Daily note loaded.",
                data={"path": relative_path, "content": content},
            )
        except Exception as exc:
            self._log_failed_lookup("daily_note_read_error", trace_id=trace_id, reason=str(exc))
            return ToolResult(success=False, message=f"Daily note read failed: {exc}")
            
    def deduplicate_memories(self) -> ToolResult:
        """Finds and consolidates duplicate memories."""
        try:
            self._recover_vault()
            # Simple content hash based deduplication
            seen_content = set()
            duplicates = 0
            
            for file_path in self._markdown_files():
                if file_path.name.startswith("archive_") or file_path.parent.name == "Daily":
                    continue
                    
                content = file_path.read_text(encoding="utf-8")
                # extract core content (ignoring headers)
                core_content = "\n".join(content.split("\n\n")[1:]).strip()
                
                if core_content in seen_content:
                    file_path.unlink()
                    duplicates += 1
                else:
                    seen_content.add(core_content)
                    
            self.logger.write("info", "memory.deduplicate", removed=duplicates)
            return ToolResult(success=True, message=f"Removed {duplicates} duplicate memories.")
        except Exception as exc:
            return ToolResult(success=False, message=f"Memory deduplication failed: {exc}")
            
    def archive_stale_memories(self, max_age_days: int = 90) -> ToolResult:
        """Archives memories older than max_age_days."""
        try:
            self._recover_vault()
            import time
            current_time = time.time()
            archived = 0
            
            archive_dir = self.vault_path / "Archive"
            archive_dir.mkdir(exist_ok=True)
            
            for file_path in self._markdown_files():
                if file_path.parent.name in ["Archive", "Daily"]:
                    continue
                    
                mtime = file_path.stat().st_mtime
                if (current_time - mtime) > (max_age_days * 86400):
                    new_path = archive_dir / f"archive_{file_path.name}"
                    file_path.rename(new_path)
                    archived += 1
                    
            self.logger.write("info", "memory.archive", archived=archived)
            return ToolResult(success=True, message=f"Archived {archived} stale memories.")
        except Exception as exc:
            return ToolResult(success=False, message=f"Memory archival failed: {exc}")

    def list_memories(
        self,
        category: str,
        *,
        trace_id: Optional[str] = None,
    ) -> ToolResult:
        normalized_category = self._normalize_category(category)
        if not normalized_category:
            self._log_failed_lookup("unsupported_category", trace_id=trace_id, category=category)
            return ToolResult(
                success=False,
                message=f"Unsupported memory category: {category}.",
                data={"supported_categories": sorted(SUPPORTED_CATEGORIES)},
            )
        try:
            self._recover_vault()
            records = [
                self._record_from_file(path, normalized_category)
                for path in sorted(self._category_dir(normalized_category).glob("*.md"))
            ]
            if not records:
                self._log_failed_lookup(
                    "empty_category",
                    trace_id=trace_id,
                    category=normalized_category,
                )
            self.logger.write(
                "info",
                "memory.read",
                trace_id=trace_id,
                operation="list_memories",
                category=normalized_category,
                result_count=len(records),
            )
            return ToolResult(
                success=True,
                message=f"Found {len(records)} {normalized_category} memory record(s).",
                data={"records": records},
            )
        except Exception as exc:
            self._log_failed_lookup(
                "list_error",
                trace_id=trace_id,
                category=normalized_category,
                reason=str(exc),
            )
            return ToolResult(success=False, message=f"Memory list failed: {exc}")

    def store(self, content: str, *, namespace: str = "default") -> ToolResult:
        category = namespace if namespace in SUPPORTED_CATEGORIES else "general"
        return self.save_memory(content, category)

    def search(self, query: str, *, limit: int = 5) -> ToolResult:
        return self.search_memory(query, limit=limit)

    def health(self) -> HealthStatus:
        try:
            self._recover_vault()
        except Exception as exc:
            return HealthStatus.fail(f"Memory vault unavailable: {exc}")
        return HealthStatus.ok(f"Memory vault ready at {self.vault_path}")

    def _recover_vault(self) -> None:
        if self.vault_path.exists() and not self.vault_path.is_dir():
            raise NotADirectoryError(f"Vault path is not a directory: {self.vault_path}")
        self.vault_path.mkdir(parents=True, exist_ok=True)
        for directory in REQUIRED_DIRECTORIES:
            (self.vault_path / directory).mkdir(parents=True, exist_ok=True)

    def _normalize_category(self, category: str) -> Optional[str]:
        normalized = category.strip().lower()
        return normalized if normalized in SUPPORTED_CATEGORIES else None

    def _category_dir(self, category: str) -> Path:
        return self.vault_path / SUPPORTED_CATEGORIES[category]

    def _filename(self, *, created_at: str, text: str, record_id: str) -> str:
        timestamp = created_at.replace("-", "").replace(":", "").split(".")[0]
        slug = _slugify(text)
        return f"{timestamp}-{slug}-{record_id[:8]}.md"

    def _daily_note_path(self) -> Path:
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.vault_path / "Daily" / f"{day}.md"

    def _ensure_daily_note(self, note_path: Path) -> None:
        if not note_path.exists():
            day = note_path.stem
            note_path.write_text(f"# {day}\n", encoding="utf-8")

    def _markdown_files(self) -> Iterable[Path]:
        for directory in REQUIRED_DIRECTORIES:
            yield from sorted((self.vault_path / directory).glob("*.md"))

    def _category_from_path(self, file_path: Path) -> str:
        parent = file_path.parent.name
        for category, directory in SUPPORTED_CATEGORIES.items():
            if directory == parent:
                return category
        if parent == "Daily":
            return "daily"
        return "unknown"

    def _record_from_file(self, file_path: Path, category: str) -> dict[str, str]:
        content = file_path.read_text(encoding="utf-8")
        return {
            "path": _relative_vault_path(file_path, self.vault_path),
            "category": category,
            "content": content,
        }

    def _log_failed_lookup(
        self,
        reason: str,
        *,
        trace_id: Optional[str] = None,
        **fields: object,
    ) -> None:
        self.logger.write(
            "warning",
            "memory.lookup.failed",
            trace_id=trace_id,
            reason=reason,
            **fields,
        )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug[:48] or "memory").strip("-")


def _keywords(query: str) -> list[str]:
    return [token for token in re.split(r"\s+", query.lower().strip()) if token]


def _render_memory_markdown(record: MemoryRecord) -> str:
    return (
        "---\n"
        f"id: {record.id}\n"
        f"category: {record.category}\n"
        f"created_at: {record.created_at}\n"
        "---\n\n"
        "# Memory\n\n"
        f"{record.content}\n"
    )


def _relative_vault_path(file_path: Path, vault_path: Path) -> str:
    return file_path.relative_to(vault_path).as_posix()
