# Build & Run — reproducible order

`Therapy/` is the **single source of truth** for the running system. The older
`finalmlkg/` and `psychotherapy 2/` folders are **superseded** (kept only for
reference/history) — do not run their pipelines against `therapy`; they use the
pre-canonical disorder names and are what originally introduced the alias nodes.

## Prerequisites
1. Neo4j running, database **`therapy`** created (never touch `system` / `neo4j`).
2. `pip install -r requirements.txt` and `python -m spacy download en_core_web_sm`
3. Copy `.env.example` → `.env`, set `NEO4J_PASSWORD` and your `LLM_*`.
4. LLM installed (default Ollama): `ollama pull llama3.2`

## Graph build order (Part 2)  — run from `part2_graphrag/pipelines/`
| Step | Script | Purpose |
|----|--------|---------|
| 0 | `00_seed_100_disorders.py` | Create the **100 canonical Disorder nodes** + Borderline `:DiagnosticQualifier`. Run FIRST. |
| 1 | `ingest_all_datasets.py` | Layer 6 — ingest all datasets → `:Session` nodes + keyword links. |
| 2 | `enrich_layers_2_5.py` | Layers 2–5 — symptoms, emotions, behaviours, contexts, techniques + their edges to the 100. |
| 3 | `fix_ontology_gaps.py` | Fill remaining symptom/context/technique gaps. |
| 4 | `semantic_disorder_classifier.py` | Spread the generic (GAD-only / ExTES) sessions across disorders semantically. |
| 5 | `add_vector_embeddings.py` | Build `session_embeddings` vector index for semantic search. |
| 6 | `10_cleanup_canonical_100.py` | **P0 integrity pass** — re-point/merge any non-canonical nodes so exactly 100 remain, no session orphaned. Safe/idempotent; run after any re-ingest. |

> After a full rebuild, always finish with step 6. It is idempotent and guarantees
> the "exactly 100 canonical disorders, all connected" invariant.

## Run the app (Part 1)
```bash
streamlit run part1_conversational/app_integrated.py
```

## Invariants a healthy graph satisfies
- `MATCH (d:Disorder) RETURN count(d)` == **100**
- Every `:Disorder` has a non-null `classification_status`
- No `:Session` is fully unmapped (has at least one of INDICATES_DISORDER /
  INDICATES_RISK / MENTIONS_CATEGORY / HAS_QUALIFIER)
- Borderline pattern is a `:DiagnosticQualifier` (6D11.5), **not** a `:Disorder`
- Suicidal ideation / self-injury are `:RiskMarker` (via `INDICATES_RISK`), not disorders
