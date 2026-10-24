"""
graphrag_bridge.py
==================
The central integration bridge between Part 1 (Conversational AI) and
Part 2 (GraphRAG Knowledge Graph).

This module defines the shared data contract and implements the full pipeline:
  1. Crisis detection (always first)
  2. Structured KG query from emotion + behaviour model signals (Part 1 → Part 2)
  3. Semantic vector search on patient text (vector index)
  4. Merge + deduplicate results from both query paths
  5. Add technique guidance (KG node names → therapist language)
  6. Return a rich GraphRAGResponse to Part 1's response engine

DATA CONTRACT
-------------
Part 1 sends:   GraphRAGRequest
Part 2 returns: GraphRAGResponse

Both are standard Python dataclasses — importable directly, no HTTP needed.
"""

from __future__ import annotations

__all__ = ["GraphRAGRequest", "GraphRAGResponse", "GraphRAGBridge"]

import sys
import os
from dataclasses import dataclass, field

# Allow running from either root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from api.crisis_detector import detect as detect_crisis
from api.graph_semantic_search import TherapyGraphSearch
from api.structured_query import query_by_signals
from api.technique_guidance import get_guidance


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CONTRACT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GraphRAGRequest:
    """
    What Part 1 sends to the GraphRAG bridge each conversation turn.

    Required:
        patient_utterance: PII-scrubbed patient text (from pii_scrubber.py)
        emotion:           Top emotion label from RoBERTa (e.g. "anxiety")
        behaviour:         Top behaviour label from DistilBERT (e.g. "Avoidance")

    Optional (improves results when available):
        therapist_utterance:    Therapist side of the transcript (from diarization)
        emotion_distribution:   Full probability dict from RoBERTa
        session_id:             Unique ID for this patient session (for memory)
        turn_number:            Which turn in the session this is
    """
    patient_utterance:    str
    emotion:              str                         = "neutral"
    behaviour:            str                         = "Emotional_Expression"
    symptoms:             list[str]                   = field(default_factory=list)
    therapist_utterance:  str | None                  = None
    emotion_distribution: dict[str, float] | None     = None
    session_id:           str                         = "default"
    turn_number:          int                         = 1


@dataclass
class RetrievedSession:
    """A single matched past therapy session."""
    session_id:      str
    patient_text:    str
    therapist_text:  str
    similarity_score: float
    source:          str = ""
    tier:            int = 0


@dataclass
class TechniqueGuidance:
    """Human-readable clinical framing for one technique."""
    name:              str
    description:       str
    therapist_framing: str
    example_phrases:   list[str]


@dataclass
class GraphRAGResponse:
    """
    What Part 2 returns to Part 1's response engine each turn.

    The response engine should use:
      - retrieved_sessions  → learn the tone/phrasing of real therapists
      - clinical_context    → know WHAT clinical issues are present
      - technique_guidance  → know HOW to address them (in natural language)
      - was_crisis          → short-circuit to crisis response if True
    """
    # Core match quality
    confidence:          float = 0.0
    was_crisis:          bool  = False

    # Past session examples (top 3 real therapy dialogues)
    retrieved_sessions:  list[RetrievedSession] = field(default_factory=list)

    # Clinical ontology context (merged from signal query + semantic search)
    disorders:           list[str] = field(default_factory=list)
    symptoms:            list[str] = field(default_factory=list)
    emotions_confirmed:  list[str] = field(default_factory=list)
    recommended_techniques: list[str] = field(default_factory=list)
    worsening_contexts:  list[str] = field(default_factory=list)
    co_occurring_disorders: list[str] = field(default_factory=list)
    modalities:          list[str] = field(default_factory=list)

    # Technique guidance (natural language framing for top 3 techniques)
    technique_guidance:  list[TechniqueGuidance] = field(default_factory=list)

    # Crisis response (only populated when was_crisis=True)
    crisis_response:     str | None = None

    def to_prompt_context(self) -> str:
        """
        Renders the response as a compact text block suitable for injecting
        into an LLM system prompt or template-based response engine.
        """
        if self.was_crisis:
            return f"[CRISIS DETECTED] {self.crisis_response}"

        lines = []
        if self.disorders:
            lines.append(f"Clinical presentations: {', '.join(self.disorders[:4])}")
        if self.symptoms:
            lines.append(f"Reported symptoms: {', '.join(self.symptoms[:5])}")
        if self.emotions_confirmed:
            lines.append(f"Confirmed emotional states: {', '.join(self.emotions_confirmed[:3])}")
        if self.worsening_contexts:
            lines.append(f"Contextual stressors: {', '.join(self.worsening_contexts[:3])}")
        if self.recommended_techniques:
            lines.append(f"Evidence-based techniques: {', '.join(self.recommended_techniques[:4])}")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# BRIDGE IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

class GraphRAGBridge:
    """
    Main bridge class. Instantiate once and call process() per conversation turn.

    Parameters
    ----------
    neo4j_uri      : bolt://localhost:7687
    neo4j_user     : neo4j
    neo4j_password : neo4jpassword
    top_k          : number of sessions to retrieve via vector search
    signal_weight  : 0.0–1.0, how much to weight structured signal query
                     vs semantic search (0.5 = equal weight)
    """

    def __init__(
        self,
        neo4j_uri:      str = "bolt://localhost:7687",
        neo4j_user:     str = "neo4j",
        neo4j_password: str = "neo4jpassword",
        top_k:          int = 3,
        signal_weight:  float = 0.5,
    ):
        print("[GraphRAGBridge] Initializing...")
        self._kg = TherapyGraphSearch(uri=neo4j_uri, user=neo4j_user, password=neo4j_password)
        self._driver = self._kg.driver
        self._top_k = top_k
        self._signal_weight = signal_weight
        print("[GraphRAGBridge] Ready.\n")

    def process(self, request: GraphRAGRequest) -> GraphRAGResponse:
        """
        Full pipeline for one conversation turn.
        Returns a GraphRAGResponse ready to be consumed by Part 1.
        """
        # ── 1. Crisis check ─────────────────────────────────────────────────────
        crisis = detect_crisis(request.patient_utterance)
        if crisis.is_crisis:
            return GraphRAGResponse(
                was_crisis=True,
                crisis_response=crisis.response,
                confidence=1.0,
            )

        # ── 2. Structured signal query (emotion + behaviour → KG traversal) ─────
        signal_results = query_by_signals(
            driver=self._driver,
            emotions=[request.emotion],
            behaviours=[request.behaviour],
            symptoms=request.symptoms,
            emotion_distribution=request.emotion_distribution,
        )

        # ── 3. Semantic vector search (patient text → embedding → sessions) ─────
        search_text = request.patient_utterance
        if request.therapist_utterance:
            search_text += " " + request.therapist_utterance

        semantic_results = self._kg.search(
            search_text, top_k=self._top_k, similarity_threshold=0.30
        )

        # ── 4. Merge results from both paths ─────────────────────────────────────
        disorders   = _merge_lists(
            signal_results.get("disorders", []),
            [d for r in semantic_results for d in r["graph_context"]["Disorders"]],
            max_items=4,
        )
        symptoms    = _merge_lists(
            signal_results.get("symptoms", []),
            [s for r in semantic_results for s in r["graph_context"]["Symptoms"]],
            max_items=6,
        )
        techniques  = _merge_lists(
            signal_results.get("techniques", []),
            [t for r in semantic_results for t in r["graph_context"]["Techniques"]],
            max_items=5,
        )
        contexts    = _merge_lists(
            signal_results.get("contexts", []),
            [c for r in semantic_results for c in r["graph_context"]["Contexts"]],
            max_items=4,
        )
        emotions_confirmed = _merge_lists(
            signal_results.get("emotion_nodes_matched", []),
            [e for r in semantic_results for e in r["graph_context"]["Emotions"]],
            max_items=4,
        )
        comorbidities = signal_results.get("comorbidities", [])[:3]
        modalities    = signal_results.get("modalities", [])[:3]

        # ── 5. Build retrieved session list ──────────────────────────────────────
        retrieved = [
            RetrievedSession(
                session_id=r["session_id"],
                patient_text=r["patient_text"] or "",
                therapist_text=r["therapist_text"] or "",
                similarity_score=r["score"],
                source=r.get("source") or "",
                tier=int(r.get("tier") or 0),
            )
            for r in semantic_results
        ]

        # ── 6. Build technique guidance for top techniques ────────────────────────
        guidance_list = []
        for tech_name in techniques[:3]:
            g = get_guidance(tech_name)
            guidance_list.append(TechniqueGuidance(
                name=tech_name,
                description=g["description"],
                therapist_framing=g["therapist_framing"],
                example_phrases=g["example_phrases"],
            ))

        # ── 7. Compute blended confidence ────────────────────────────────────────
        signal_conf   = signal_results.get("confidence", 0.0)
        semantic_conf = semantic_results[0]["score"] if semantic_results else 0.0
        blended_conf  = (
            self._signal_weight * signal_conf +
            (1 - self._signal_weight) * semantic_conf
        )

        return GraphRAGResponse(
            confidence=round(blended_conf, 3),
            was_crisis=False,
            retrieved_sessions=retrieved,
            disorders=disorders,
            symptoms=symptoms,
            emotions_confirmed=emotions_confirmed,
            recommended_techniques=techniques,
            worsening_contexts=contexts,
            co_occurring_disorders=comorbidities,
            modalities=modalities,
            technique_guidance=guidance_list,
        )

    def close(self):
        self._kg.close()


# ─── Helpers ────────────────────────────────────────────────────────────────────

def _merge_lists(*lists, max_items: int = 5) -> list[str]:
    """Merge multiple lists preserving order, deduplicating, capping at max_items."""
    seen = set()
    merged = []
    for lst in lists:
        for item in (lst or []):
            if item and item not in seen:
                seen.add(item)
                merged.append(item)
            if len(merged) >= max_items:
                return merged
    return merged
