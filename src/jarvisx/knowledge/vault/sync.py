"""Incremental Vault Synchronization Engine for Jarvis X Knowledge Subsystem."""

from __future__ import annotations
import hashlib
import time
from pathlib import Path
from typing import List, Optional
from jarvisx.knowledge.ingestion.document_loader import DocumentLoader
from jarvisx.knowledge.index.knowledge_index import KnowledgeMetadataIndex
from jarvisx.knowledge.index.vector_store import LocalVectorStore
from jarvisx.knowledge.models import IngestionReport
from jarvisx.knowledge.vault.vault_manager import ObsidianVaultManager


class VaultSyncManager:
    """Performs hash-checked incremental synchronization between Obsidian Vault and Knowledge Index."""

    def __init__(
        self,
        vault_manager: Optional[ObsidianVaultManager] = None,
        metadata_index: Optional[KnowledgeMetadataIndex] = None,
        vector_store: Optional[LocalVectorStore] = None,
    ):
        self.vault_mgr = vault_manager or ObsidianVaultManager()
        self.metadata_idx = metadata_index or KnowledgeMetadataIndex()
        self.vector_store = vector_store or LocalVectorStore()
        self.loader = DocumentLoader()

    def sync_vault(self, force_rebuild: bool = False) -> IngestionReport:
        """Scan vault, compute file hashes, index only modified/new files, and purge deleted records."""
        start_t = time.time()
        report = IngestionReport()

        if force_rebuild:
            self.vector_store.clear()

        # 1. Discover all current files on disk
        current_files = self.vault_mgr.list_all_files()
        report.total_files_scanned = len(current_files)
        current_source_paths = {str(p).replace("\\", "/") for p in current_files}

        # 2. Check for deleted files that exist in DB but not on disk
        stored_docs = self.metadata_idx.list_all_documents()
        for s_doc in stored_docs:
            if s_doc.source_file not in current_source_paths:
                self.metadata_idx.delete_document(s_doc.source_file)
                self.vector_store.remove_source(s_doc.source_file)
                report.files_deleted_purged += 1
                report.details.append(f"Purged deleted file: {s_doc.source_file}")

        # 3. Process current files incrementally
        for fpath in current_files:
            p_str = str(fpath).replace("\\", "/")
            try:
                raw_bytes = fpath.read_bytes()
                curr_hash = hashlib.sha256(raw_bytes).hexdigest()
            except Exception as e:
                report.details.append(f"Error reading {p_str}: {e}")
                continue

            existing_doc = self.metadata_idx.get_document(p_str)

            # Check if unchanged
            if existing_doc and existing_doc.content_hash == curr_hash and not force_rebuild:
                report.files_skipped_unchanged += 1
                continue

            # File is new or modified: Ingest and index
            cat, sens = self.vault_mgr.infer_category_and_sensitivity(fpath)
            try:
                doc_meta, chunks = self.loader.load_file(
                    file_path=fpath,
                    category=cat,
                    sensitivity=sens,
                )
                self.metadata_idx.save_document(doc_meta, chunks)
                self.vector_store.remove_source(p_str)
                self.vector_store.index_chunks_batch(chunks)

                report.files_indexed += 1
                report.total_chunks_created += len(chunks)
                report.details.append(f"Indexed ({len(chunks)} chunks): {p_str}")
            except Exception as e:
                report.details.append(f"Failed to index {p_str}: {e}")

        report.duration_sec = time.time() - start_t
        return report
