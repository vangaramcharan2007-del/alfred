"""Markdown & Obsidian Knowledge Parser for Jarvis X."""

from __future__ import annotations
import hashlib
import re
from typing import Any, Dict, List, Tuple
import yaml
from jarvisx.knowledge.models import KnowledgeChunk, KnowledgeSensitivity, VaultCategory


class ObsidianMarkdownParser:
    """Parses Obsidian Markdown notes, extracting YAML frontmatter, wikilinks, tags, and section chunks."""

    WIKILINK_REGEX = re.compile(r"\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]")
    TAG_REGEX = re.compile(r"(?:^|\s)#([a-zA-Z0-9_\-\/]+)")

    def parse_document(
        self,
        raw_text: str,
        source_file: str,
        category: VaultCategory = VaultCategory.GENERAL,
        sensitivity: KnowledgeSensitivity = KnowledgeSensitivity.INTERNAL,
    ) -> Tuple[Dict[str, Any], List[KnowledgeChunk]]:
        """Parse raw markdown content into metadata and hierarchical knowledge chunks."""
        frontmatter, content = self._extract_frontmatter(raw_text)
        
        # Extract title from frontmatter or first H1
        title = frontmatter.get("title", "")
        if not title:
            h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
            else:
                title = source_file.split("/")[-1].split("\\")[-1]

        # Extract global tags
        doc_tags = set()
        if "tags" in frontmatter:
            fm_tags = frontmatter["tags"]
            if isinstance(fm_tags, list):
                doc_tags.update(str(t).strip("#") for t in fm_tags)
            elif isinstance(fm_tags, str):
                doc_tags.update(t.strip("# ") for t in fm_tags.split(","))

        for m in self.TAG_REGEX.finditer(content):
            doc_tags.add(m.group(1))

        # Extract global wikilinks
        doc_wikilinks = [m.group(1).strip() for m in self.WIKILINK_REGEX.finditer(content)]

        # Chunk the document by headings
        chunks = self._chunk_by_headings(
            content=content,
            source_file=source_file,
            doc_tags=list(doc_tags),
            category=category,
            sensitivity=sensitivity,
        )

        metadata = {
            "title": title,
            "frontmatter": frontmatter,
            "tags": list(doc_tags),
            "wikilinks": doc_wikilinks,
        }

        return metadata, chunks

    def _extract_frontmatter(self, text: str) -> Tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter between leading --- delimiters."""
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm_data = yaml.safe_load(parts[1])
                    if isinstance(fm_data, dict):
                        return fm_data, parts[2].strip()
                except Exception:
                    pass
        return {}, text.strip()

    def _chunk_by_headings(
        self,
        content: str,
        source_file: str,
        doc_tags: List[str],
        category: VaultCategory,
        sensitivity: KnowledgeSensitivity,
        max_chunk_chars: int = 1200,
    ) -> List[KnowledgeChunk]:
        """Split text hierarchically on Markdown headings while preserving heading paths."""
        lines = content.splitlines()
        chunks: List[KnowledgeChunk] = []

        current_heading_stack: List[str] = []
        current_lines: List[str] = []
        chunk_idx = 0

        for line in lines:
            h_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if h_match:
                # Flush existing buffer
                if current_lines:
                    text_block = "\n".join(current_lines).strip()
                    if text_block:
                        h_path = " > ".join(current_heading_stack) if current_heading_stack else "# Root"
                        c_hash = hashlib.sha256(text_block.encode("utf-8")).hexdigest()[:16]
                        chunks.append(KnowledgeChunk(
                            id=f"{source_file}#c{chunk_idx}",
                            source_file=source_file,
                            chunk_index=chunk_idx,
                            content=text_block,
                            heading_path=h_path,
                            content_hash=c_hash,
                            tags=doc_tags,
                            wikilinks=[m.group(1).strip() for m in self.WIKILINK_REGEX.finditer(text_block)],
                            sensitivity=sensitivity,
                            category=category,
                        ))
                        chunk_idx += 1
                        current_lines = []

                level = len(h_match.group(1))
                h_title = h_match.group(2).strip()

                # Adjust heading stack depth
                if level <= len(current_heading_stack):
                    current_heading_stack = current_heading_stack[: level - 1]
                current_heading_stack.append(f"{'#' * level} {h_title}")

            current_lines.append(line)

        # Flush final chunk
        if current_lines:
            text_block = "\n".join(current_lines).strip()
            if text_block:
                h_path = " > ".join(current_heading_stack) if current_heading_stack else "# Root"
                c_hash = hashlib.sha256(text_block.encode("utf-8")).hexdigest()[:16]
                chunks.append(KnowledgeChunk(
                    id=f"{source_file}#c{chunk_idx}",
                    source_file=source_file,
                    chunk_index=chunk_idx,
                    content=text_block,
                    heading_path=h_path,
                    content_hash=c_hash,
                    tags=doc_tags,
                    wikilinks=[m.group(1).strip() for m in self.WIKILINK_REGEX.finditer(text_block)],
                    sensitivity=sensitivity,
                    category=category,
                ))

        return chunks
