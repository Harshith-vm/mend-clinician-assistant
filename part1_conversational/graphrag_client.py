"""
graphrag_client.py  (Part 1)
============================
Thin client that Part 1's chatbot calls to get KG context from Part 2.
Handles the import path resolution so Part 1 code can reach finalmlkg/api/.

Usage (from psychotherapy_part1/):
    from graphrag_client import GraphRAGClient, build_request

    client = GraphRAGClient()
    request = build_request(
        patient_text  = "I feel so anxious I can't breathe",
        emotion       = "anxiety",
        behaviour     = "Help_Seeking",
        emotion_dist  = {"anxiety": 0.72, "fear": 0.20, "neutral": 0.08},
        session_id    = "patient_001",
        turn_number   = 3,
    )
    response = client.query(request)
    print(response.to_prompt_context())
    print(response.technique_guidance[0].therapist_framing)
"""

from __future__ import annotations

import os
import sys

# ── Resolve path to finalmlkg/api from inside psychotherapy_part1/ ─────────────
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR   = os.path.dirname(_THIS_DIR)               # Therapy/part1_conversational/..
_KG_API_DIR = os.path.join(_ROOT_DIR, "part2_graphrag") # Therapy/part2_graphrag

for p in [_ROOT_DIR, _KG_API_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from api.graphrag_bridge import GraphRAGBridge, GraphRAGRequest, GraphRAGResponse


class GraphRAGClient:
    """
    Singleton-style wrapper around GraphRAGBridge.
    Lazy-initializes on first call so importing this module is free.
    """

    _instance: GraphRAGBridge | None = None

    def __init__(
        self,
        neo4j_uri:      str = "bolt://localhost:7687",
        neo4j_user:     str = "neo4j",
        neo4j_password: str = os.environ.get("NEO4J_PASSWORD", ""),
    ):
        if GraphRAGClient._instance is None:
            GraphRAGClient._instance = GraphRAGBridge(
                neo4j_uri=neo4j_uri,
                neo4j_user=neo4j_user,
                neo4j_password=neo4j_password,
            )
        self._bridge = GraphRAGClient._instance

    def query(self, request: GraphRAGRequest) -> GraphRAGResponse:
        """Send one turn to the GraphRAG bridge and return the full response."""
        return self._bridge.process(request)

    def close(self):
        if GraphRAGClient._instance:
            GraphRAGClient._instance.close()
            GraphRAGClient._instance = None


def build_request(
    patient_text:  str,
    emotion:       str                     = "neutral",
    behaviour:     str                     = "Emotional_Expression",
    symptoms:      list[str] | None        = None,
    emotion_dist:  dict[str, float] | None = None,
    therapist_text: str | None             = None,
    session_id:    str                     = "default",
    turn_number:   int                     = 1,
) -> GraphRAGRequest:
    """Convenience constructor for GraphRAGRequest."""
    return GraphRAGRequest(
        patient_utterance=patient_text,
        emotion=emotion,
        behaviour=behaviour,
        symptoms=symptoms or [],
        emotion_distribution=emotion_dist,
        therapist_utterance=therapist_text,
        session_id=session_id,
        turn_number=turn_number,
    )
