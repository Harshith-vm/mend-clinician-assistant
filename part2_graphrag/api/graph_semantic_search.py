"""
graph_semantic_search.py
========================
Provides GraphRAG (Retrieval-Augmented Generation) capabilities by combining
Semantic Vector Search with Knowledge Graph traversal.

How it works:
1. Embeds the user's natural language query using sentence-transformers.
2. Queries the Neo4j vector index (`session_embeddings`) to find the most
   semantically similar counseling sessions.
3. Traverses the graph from those sessions to retrieve their clinical metadata
   (Disorders, Symptoms, Emotions, Techniques, Behaviours, Contexts).
4. Returns a rich, structured clinical profile for the matched sessions.

This module is LLM-agnostic — it only handles retrieval, not generation.
"""

__all__ = ["TherapyGraphSearch"]

import sys
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase

# Configure stdout for safe printing of unicode characters (emojis/special chars)
sys.stdout.reconfigure(encoding='utf-8')

class TherapyGraphSearch:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="neo4jpassword"):
        print("[System] Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        import os
        pwd = os.environ.get("NEO4J_PASSWORD", password)
        self.driver = GraphDatabase.driver(uri, auth=(user, pwd))
        print("[System] Connected to Neo4j and ready for queries.\n")

    def close(self):
        self.driver.close()

    def search(self, query: str, top_k: int = 3, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Executes a vector search followed by a graph traversal.
        """
        # 1. Embed the natural language query
        query_vector = self.model.encode(query).tolist()
        
        # 2. Cypher: Vector search (current Neo4j 5.x syntax) + Graph traversal
        cypher = """
        CALL db.index.vector.queryNodes('session_embeddings', $top_k, $query_vector)
        YIELD node AS s, score
        WHERE score >= $threshold

        // Traverse to find connected clinical data
        OPTIONAL MATCH (s)-[:INDICATES_DISORDER]->(d:Disorder)
        OPTIONAL MATCH (s)-[:MENTIONS_SYMPTOM]->(sym:Symptom)
        OPTIONAL MATCH (s)-[:EXPRESSES_EMOTION]->(e:EmotionalState)
        OPTIONAL MATCH (s)-[:SUGGESTS_TECHNIQUE]->(t:TherapeuticTechnique)
        OPTIONAL MATCH (s)-[:INVOLVES_CONTEXT]->(c:ContextCategory)
        OPTIONAL MATCH (s)-[:EXHIBITS_BEHAVIOUR]->(b:Behaviour)

        RETURN
            s.session_id AS session_id,
            s.patient_utterance AS patient_text,
            s.therapist_utterance AS therapist_text,
            s.source AS source,
            s.tier AS tier,
            score,
            collect(DISTINCT d.name) AS disorders,
            collect(DISTINCT sym.name) AS symptoms,
            collect(DISTINCT e.name) AS emotions,
            collect(DISTINCT t.name) AS techniques,
            collect(DISTINCT c.name) AS contexts,
            collect(DISTINCT b.name) AS behaviours
        ORDER BY score DESC
        """
        
        results = []
        with self.driver.session(database="therapy") as session:
            records = session.run(cypher, query_vector=query_vector, top_k=top_k, threshold=similarity_threshold)
            
            for r in records:
                results.append({
                    "session_id": r["session_id"],
                    "score": r["score"],
                    "patient_text": r["patient_text"],
                    "therapist_text": r["therapist_text"],
                    "graph_context": {
                        "Disorders": r["disorders"],
                        "Symptoms": r["symptoms"],
                        "Emotions": r["emotions"],
                        "Techniques": r["techniques"],
                        "Contexts": r["contexts"],
                        "Behaviours": r["behaviours"]
                    }
                })
        return results

    def display_results(self, query: str, results: List[Dict[str, Any]]):
        print("=" * 80)
        print(f"🔍 SEARCH QUERY: \"{query}\"")
        print("=" * 80)
        
        if not results:
            print("\n❌ No sessions found matching the threshold.")
            return

        for i, res in enumerate(results, 1):
            print(f"\n[{i}] MATCH SCORE: {res['score']:.4f} | Session: {res['session_id']}")
            print("-" * 80)
            print("👤 PATIENT:")
            pt_text = res['patient_text'] or ""
            print(f"  {pt_text[:200]}..." if len(pt_text) > 200 else f"  {pt_text}")
            
            print("\n🧑‍⚕️ THERAPIST:")
            th_text = res['therapist_text'] or ""
            print(f"  {th_text[:200]}..." if len(th_text) > 200 else f"  {th_text}")
            
            print("\n🧠 GRAPH CONTEXT (Layer 1-5 Ontology Mapping):")
            ctx = res['graph_context']
            if ctx['Disorders']:  print(f"  • Disorders : {', '.join(ctx['Disorders'])}")
            if ctx['Symptoms']:   print(f"  • Symptoms  : {', '.join(ctx['Symptoms'])}")
            if ctx['Emotions']:   print(f"  • Emotions  : {', '.join(ctx['Emotions'])}")
            if ctx['Techniques']: print(f"  • Techniques: {', '.join(ctx['Techniques'])}")
            if ctx['Contexts']:   print(f"  • Contexts  : {', '.join(ctx['Contexts'])}")
            if ctx['Behaviours']: print(f"  • Behaviours: {', '.join(ctx['Behaviours'])}")
            print("-" * 80)


if __name__ == "__main__":
    # Interactive CLI mode
    searcher = TherapyGraphSearch()
    
    if len(sys.argv) > 1:
        # Command line argument mode
        query = " ".join(sys.argv[1:])
        results = searcher.search(query, top_k=3)
        searcher.display_results(query, results)
    else:
        # Example queries to show off the GraphRAG capabilities
        queries = [
            "I feel completely empty inside and I cannot get out of bed. I have no motivation.",
            "I'm terrified of social situations, I always think people are judging me and I start sweating.",
            "My partner left me and I can't stop drinking to cope with the pain."
        ]
        
        for q in queries:
            results = searcher.search(q, top_k=2)
            searcher.display_results(q, results)
            
    searcher.close()
