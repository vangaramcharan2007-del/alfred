"""Master Knowledge Subsystem Engine for Jarvis X v1.1."""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
from jarvisx.knowledge.context_builder import KnowledgeContextComposer
from jarvisx.knowledge.index.knowledge_index import KnowledgeMetadataIndex
from jarvisx.knowledge.index.vector_store import LocalVectorStore
from jarvisx.knowledge.models import (
    IngestionReport,
    KnowledgeSensitivity,
    SearchResult,
    VaultCategory,
)
from jarvisx.knowledge.retrieval.retriever import KnowledgeRetriever
from jarvisx.knowledge.vault.sync import VaultSyncManager
from jarvisx.knowledge.vault.vault_manager import ObsidianVaultManager


class KnowledgeEngine:
    """Master Knowledge Engine coordinating Vault Management, Sync, Indexing, and Retrieval."""

    def __init__(
        self,
        vault_path: Optional[str] = None,
        db_path: str = "var/db/knowledge.db",
        vector_index_path: str = "var/knowledge/vectors/vector_index.json",
    ):
        self.vault_manager = ObsidianVaultManager(vault_path)
        self.metadata_index = KnowledgeMetadataIndex(db_path)
        self.vector_store = LocalVectorStore(vector_index_path)
        self.sync_manager = VaultSyncManager(
            vault_manager=self.vault_manager,
            metadata_index=self.metadata_index,
            vector_store=self.vector_store,
        )
        self.retriever = KnowledgeRetriever(
            metadata_index=self.metadata_index,
            vector_store=self.vector_store,
        )
        self.context_composer = KnowledgeContextComposer()

    def init_vault(self) -> Dict[str, Any]:
        """Scaffold standard Obsidian Vault structure."""
        return self.vault_manager.initialize_vault()

    def sync(self, force_rebuild: bool = False) -> IngestionReport:
        """Run incremental sync on the Obsidian vault."""
        return self.sync_manager.sync_vault(force_rebuild=force_rebuild)

    def ingest_path(self, target_path: str | Path) -> IngestionReport:
        """Ingest a specific file or folder into the knowledge index."""
        p = Path(target_path)
        if not p.exists():
            raise FileNotFoundError(f"Path does not exist: {target_path}")

        if p.is_dir():
            # Sync that specific directory
            custom_vm = ObsidianVaultManager(str(p))
            custom_sync = VaultSyncManager(
                vault_manager=custom_vm,
                metadata_index=self.metadata_index,
                vector_store=self.vector_store,
            )
            return custom_sync.sync_vault(force_rebuild=False)
        else:
            cat, sens = self.vault_manager.infer_category_and_sensitivity(p)
            doc_meta, chunks = self.sync_manager.loader.load_file(
                file_path=p,
                category=cat,
                sensitivity=sens,
            )
            self.metadata_index.save_document(doc_meta, chunks)
            self.vector_store.remove_source(str(p).replace("\\", "/"))
            self.vector_store.index_chunks_batch(chunks)

            report = IngestionReport(
                total_files_scanned=1,
                files_indexed=1,
                files_skipped_unchanged=0,
                files_deleted_purged=0,
                total_chunks_created=len(chunks),
                details=[f"Ingested file: {p}"],
            )
            return report

    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[VaultCategory] = None,
        max_sensitivity: KnowledgeSensitivity = KnowledgeSensitivity.INTERNAL,
        actor_role: str = "AlfredMaster",
    ) -> List[SearchResult]:
        """Perform hybrid search over indexed knowledge."""
        return self.retriever.search(
            query=query,
            top_k=top_k,
            category_filter=category,
            max_sensitivity=max_sensitivity,
            actor_role=actor_role,
        )

    def get_context_for_prompt(
        self,
        query: str,
        top_k: int = 4,
        max_sensitivity: KnowledgeSensitivity = KnowledgeSensitivity.INTERNAL,
        actor_role: str = "AlfredMaster",
    ) -> str:
        """Retrieve and format grounded knowledge context ready for injection into Alfred / LLM."""
        results = self.search(
            query=query,
            top_k=top_k,
            max_sensitivity=max_sensitivity,
            actor_role=actor_role,
        )
        return self.context_composer.compose_context(query=query, results=results)

    def status(self) -> Dict[str, Any]:
        """Return knowledge engine status, document counts, and vector index size."""
        stats = self.metadata_index.get_stats()
        return {
            "vault_path": str(self.vault_manager.vault_path),
            "total_documents": stats["total_documents"],
            "total_chunks": stats["total_chunks"],
            "categories": stats["categories"],
            "vector_index_count": len(self.vector_store.vectors),
            "status": "HEALTHY",
        }
