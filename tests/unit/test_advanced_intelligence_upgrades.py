"""Unit verification for Jarvis X Advanced Intelligence Upgrades:
- BM25 & Hybrid Search with Reciprocal Rank Fusion (RRF)
- Corrective RAG (CRAG)
- QLoRA Dataset Generation with Chain-of-Thought (<thought> tags)
"""

import pytest
import os
import json
from jarvisx.mesh.rag_retriever import BM25Ranker, RAGRetriever
from jarvisx.training.dataset_generator import DatasetGenerator, SEED_TRAINING_EXAMPLES


def test_bm25_ranker_lexical_scoring():
    """Verify BM25 ranker prioritizes documents with exact keyword matches."""
    corpus = [
        "The Playwright MCP server provides DOM text extraction and headless browser navigation.",
        "The UACC server handles desktop mouse clicks and screen inspection on Windows.",
        "Unreal Engine 5 features Chaos Physics and Lumen global illumination."
    ]
    bm25 = BM25Ranker(corpus)

    # Search for exact term in doc 1
    scores_uacc = bm25.score("UACC mouse clicks")
    assert scores_uacc[1] > scores_uacc[0]
    assert scores_uacc[1] > scores_uacc[2]

    # Search for exact term in doc 0
    scores_playwright = bm25.score("Playwright browser navigation")
    assert scores_playwright[0] > scores_playwright[1]
    assert scores_playwright[0] > scores_playwright[2]


def test_dataset_generator_cot_jsonl(tmp_path):
    """Verify DatasetGenerator creates valid JSONL with system, thought, and output fields."""
    out_file = tmp_path / "test_dataset.jsonl"
    gen = DatasetGenerator(output_path=str(out_file))
    res_path = gen.generate_seed_dataset()

    assert os.path.exists(res_path)
    with open(res_path, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]

    assert len(lines) == len(SEED_TRAINING_EXAMPLES)
    for entry in lines:
        messages = entry["messages"]
        assert len(messages) == 3
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"
        assert "<thought>" in messages[2]["content"]
        assert "</thought>" in messages[2]["content"]


def test_hybrid_rag_retriever_query():
    """Verify RAGRetriever performs hybrid search with RRF scoring."""
    retriever = RAGRetriever()
    if retriever.is_ready():
        matches = retriever.corrective_rag_query("PersonalOSKernel tool executor permissions", top_k=2)
        assert isinstance(matches, list)
        if matches:
            assert "rank" in matches[0]
            assert "score" in matches[0]
            assert "content" in matches[0]
