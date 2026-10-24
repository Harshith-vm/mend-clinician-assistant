# -*- coding: utf-8 -*-
"""
00_seed_100_disorders.py  —  STEP 0 of the build.
Creates the 100 canonical :Disorder nodes (+ Borderline :DiagnosticQualifier) from
00_seed_100_disorders.cypher. Every later pipeline (ingest, enrich, cleanup) assumes
these exist. Idempotent (MERGE ... ON CREATE SET). Targets 'therapy' only.

Run FIRST, before ingest_all_datasets.py.
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from neo4j import GraphDatabase

URI  = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
USER = os.environ.get("NEO4J_USER", "neo4j")
PW   = os.environ.get("NEO4J_PASSWORD", "neo4jpassword")
DB   = os.environ.get("NEO4J_DATABASE", "therapy")
assert DB == "therapy", f"refusing to run against '{DB}'"

CYPHER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "00_seed_100_disorders.cypher")


def statements(text):
    # drop whole-line // comments; URLs keep their // (mid-line, inside quotes); split on ;
    body = "\n".join(ln for ln in text.splitlines() if not ln.strip().startswith("//"))
    return [s.strip() for s in body.split(";") if s.strip()]


def main():
    d = GraphDatabase.driver(URI, auth=(USER, PW))
    d.verify_connectivity()
    with d.session(database=DB) as s:
        assert s.run("CALL db.info() YIELD name RETURN name").single()["name"] == "therapy"
    stmts = statements(open(CYPHER, encoding="utf-8").read())
    ok = err = 0
    with d.session(database=DB) as s:
        for st in stmts:
            try:
                s.run(st); ok += 1
            except Exception as e:
                if "equivalent" in str(e).lower() or "already exists" in str(e):
                    ok += 1
                else:
                    err += 1; print("  ERR:", str(e)[:160])
    with d.session(database=DB) as s:
        nd = s.run("MATCH (d:Disorder) RETURN count(d)").single()[0]
        nq = s.run("MATCH (q:DiagnosticQualifier) RETURN count(q)").single()[0]
    d.close()
    print(f"seed: {ok} ok / {err} err | Disorder={nd} (target 100), DiagnosticQualifier={nq}")


if __name__ == "__main__":
    main()
