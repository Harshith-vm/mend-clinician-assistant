"""
finalmlkg/api/__init__.py
=========================
Public API surface for the Mental Health Knowledge Graph GraphRAG module.

Quick start (LLM as therapist via GraphRAG bridge):
----------------------------------------------------
    # From Part 1 (psychotherapy_part1/):
    from graphrag_client import GraphRAGClient, build_request
    client = GraphRAGClient()
    resp = client.query(build_request("I feel so alone", emotion="sadness", behaviour="Social_Withdrawal"))
    print(resp.to_prompt_context())

Direct KG search:
-----------------
    from finalmlkg.api.graph_semantic_search import TherapyGraphSearch
    kg = TherapyGraphSearch()
    results = kg.search("fear of abandonment", top_k=5)

Structured signal query (no vector search):
-------------------------------------------
    from finalmlkg.api.structured_query import query_by_signals
    results = query_by_signals(driver, emotions=["anxiety"], behaviours=["Avoidance"])

Switching models:
-----------------
    from finalmlkg.api.therapy_assistant import (
        TherapyAssistant, OpenAIAdapter, GeminiAdapter, AnthropicAdapter
    )
    assistant = TherapyAssistant(llm=OpenAIAdapter(api_key="sk-...", model="gpt-4o"))

Direct KG search (no LLM):
---------------------------
    from finalmlkg.api.graph_semantic_search import TherapyGraphSearch
    kg = TherapyGraphSearch()
    results = kg.search("fear of abandonment", top_k=5)

Crisis detection only:
----------------------
    from finalmlkg.api.crisis_detector import detect
    result = detect("I don't want to live anymore")
    if result.is_crisis:
        print(result.response)
"""

from .graph_semantic_search import TherapyGraphSearch
from .crisis_detector import detect as detect_crisis, CrisisResult
from .session_memory import SessionMemory
from .structured_query import query_by_signals, EMOTION_LABEL_MAP, BEHAVIOUR_LABEL_MAP
from .technique_guidance import get_guidance, TECHNIQUE_GUIDANCE
from .graphrag_bridge import GraphRAGBridge, GraphRAGRequest, GraphRAGResponse
from .therapy_assistant import (
    TherapyAssistant,
    ChatResult,
    BaseLLMAdapter,
    OllamaAdapter,
    OpenAIAdapter,
    GeminiAdapter,
    AnthropicAdapter,
)

__all__ = [
    # Core search
    "TherapyGraphSearch",
    # Bridge (Part 1 ↔ Part 2 contract)
    "GraphRAGBridge",
    "GraphRAGRequest",
    "GraphRAGResponse",
    # Signal query
    "query_by_signals",
    "EMOTION_LABEL_MAP",
    "BEHAVIOUR_LABEL_MAP",
    # Technique guidance
    "get_guidance",
    "TECHNIQUE_GUIDANCE",
    # Session memory
    "SessionMemory",
    # Safety
    "detect_crisis",
    "CrisisResult",
    # LLM assistant
    "TherapyAssistant",
    "ChatResult",
    "BaseLLMAdapter",
    "OllamaAdapter",
    "OpenAIAdapter",
    "GeminiAdapter",
    "AnthropicAdapter",
]
