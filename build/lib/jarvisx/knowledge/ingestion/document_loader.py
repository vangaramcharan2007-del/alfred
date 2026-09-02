"""Multi-Format Document Loader for Jarvis X Knowledge Subsystem."""

from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from jarvisx.knowledge.ingestion.markdown_parser import ObsidianMarkdownParser
from jarvisx.knowledge.models import (
    DocumentMetadata,
    KnowledgeChunk,
    KnowledgeSensitivity,
    VaultCategory,
)


class DocumentLoader:
    """Loads and transforms various file formats into DocumentMetadata and KnowledgeChunks."""

    def __init__(self):
        self.md_parser = ObsidianMarkdownParser()

    def load_file(
        self,
        file_path: Path | str,
        category: VaultCategory = VaultCategory.GENERAL,
        sensitivity: KnowledgeSensitivity = KnowledgeSensitivity.INTERNAL,
    ) -> Tuple[DocumentMetadata, List[KnowledgeChunk]]:
        """Load a file from disk and parse into structured chunks and metadata."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        raw_bytes = p.read_bytes()
        file_size = len(raw_bytes)
        content_hash = hashlib.sha256(raw_bytes).hexdigest()
        stat = p.stat()
        created_at = stat.st_ctime
        modified_at = stat.st_mtime
        p_str = str(p).replace("\\", "/")

        suffix = p.suffix.lower()

        if suffix in (".md", ".markdown"):
            raw_text = raw_bytes.decode("utf-8", errors="replace")
            meta_dict, chunks = self.md_parser.parse_document(
                raw_text=raw_text,
                source_file=p_str,
                category=category,
                sensitivity=sensitivity,
            )
            doc_meta = DocumentMetadata(
                source_file=p_str,
                source_type="markdown",
                category=category,
                sensitivity=sensitivity,
                content_hash=content_hash,
                title=meta_dict.get("title", p.stem),
                tags=meta_dict.get("tags", []),
                wikilinks=meta_dict.get("wikilinks", []),
                frontmatter=meta_dict.get("frontmatter", {}),
                file_size_bytes=file_size,
                created_at=created_at,
                last_modified=modified_at,
            )
            return doc_meta, chunks

        elif suffix in (".txt", ".py", ".json", ".yaml", ".yml"):
            raw_text = raw_bytes.decode("utf-8", errors="replace")
            # Simple paragraph/section chunking
            paragraphs = [p_block.strip() for p_block in raw_text.split("\n\n") if p_block.strip()]
            chunks = []
            for idx, para in enumerate(paragraphs):
                c_hash = hashlib.sha256(para.encode("utf-8")).hexdigest()[:16]
                chunks.append(KnowledgeChunk(
                    id=f"{p_str}#c{idx}",
                    source_file=p_str,
                    chunk_index=idx,
                    content=para,
                    heading_path=f"File: {p.name}",
                    content_hash=c_hash,
                    tags=[suffix.strip(".")],
                    wikilinks=[],
                    sensitivity=sensitivity,
                    category=category,
                ))

            doc_meta = DocumentMetadata(
                source_file=p_str,
                source_type="text",
                category=category,
                sensitivity=sensitivity,
                content_hash=content_hash,
                title=p.stem,
                tags=[suffix.strip(".")],
                wikilinks=[],
                frontmatter={},
                file_size_bytes=file_size,
                created_at=created_at,
                last_modified=modified_at,
            )
            return doc_meta, chunks

        elif suffix == ".pdf":
            # PDF text extraction
            pdf_text = self._extract_pdf_text(p)
            paragraphs = [p_block.strip() for p_block in pdf_text.split("\n\n") if p_block.strip()]
            chunks = []
            for idx, para in enumerate(paragraphs):
                c_hash = hashlib.sha256(para.encode("utf-8")).hexdigest()[:16]
                chunks.append(KnowledgeChunk(
                    id=f"{p_str}#c{idx}",
                    source_file=p_str,
                    chunk_index=idx,
                    content=para,
                    heading_path=f"PDF: {p.name}",
                    content_hash=c_hash,
                    tags=["pdf", "reference"],
                    wikilinks=[],
                    sensitivity=sensitivity,
                    category=category,
                ))

            doc_meta = DocumentMetadata(
                source_file=p_str,
                source_type="pdf",
                category=category,
                sensitivity=sensitivity,
                content_hash=content_hash,
                title=p.stem,
                tags=["pdf", "reference"],
                wikilinks=[],
                frontmatter={},
                file_size_bytes=file_size,
                created_at=created_at,
                last_modified=modified_at,
            )
            return doc_meta, chunks

        else:
            # Fallback plain binary/text representation
            raw_text = raw_bytes.decode("utf-8", errors="replace")[:4000]
            chunks = [KnowledgeChunk(
                id=f"{p_str}#c0",
                source_file=p_str,
                chunk_index=0,
                content=raw_text,
                heading_path=f"File: {p.name}",
                content_hash=content_hash[:16],
                tags=["generic"],
                wikilinks=[],
                sensitivity=sensitivity,
                category=category,
            )]
            doc_meta = DocumentMetadata(
                source_file=p_str,
                source_type="generic",
                category=category,
                sensitivity=sensitivity,
                content_hash=content_hash,
                title=p.stem,
                tags=["generic"],
                wikilinks=[],
                frontmatter={},
                file_size_bytes=file_size,
                created_at=created_at,
                last_modified=modified_at,
            )
            return doc_meta, chunks

    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using pypdf or fallback byte inspection."""
        try:
            import pypdf
            reader = pypdf.PdfReader(str(pdf_path))
            pages = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    pages.append(t)
            return "\n\n".join(pages)
        except Exception:
            # Fallback
            return f"PDF Document: {pdf_path.name} (Binary content indexed)"
