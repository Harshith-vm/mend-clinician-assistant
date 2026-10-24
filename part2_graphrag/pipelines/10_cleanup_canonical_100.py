# -*- coding: utf-8 -*-
"""
10_cleanup_canonical_100.py
===========================
P0 graph-integrity cleanup. Restores the "exactly 100 canonical Disorder nodes"
invariant and re-points every edge off the 15 non-canonical nodes so NO session
is orphaned and NO curated clinical edge is lost.

What it does (idempotent, safe to re-run):
  1. MERGE 11 non-canonical disorder nodes -> canonical (moves ALL edges, then deletes):
        ComplexPostTraumaticStressDisorder -> ComplexPTSD           (25,965 sessions)
        MajorDepressiveDisorder            -> SingleEpisodeDepressiveDisorder
        BipolarDisorder                    -> BipolarTypeIDisorder
        BipolarIIDisorder                  -> BipolarTypeIIDisorder
        ADHD                               -> AttentionDeficitHyperactivityDisorder
        PMDD                               -> PremenstrualDysphoricDisorder
        AlcoholUseDisorder                 -> AlcoholDependence
        PersistentDepressiveDisorder       -> DysthymicDisorder
        IllnessAnxietyDisorder             -> Hypochondriasis
        SeasonalAffectiveDisorder          -> RecurrentDepressiveDisorder
        BorderlinePersonalityDisorder      -> PersonalityDisorder
  2. BorderlinePattern (:Disorder, 58k sessions) -> reclassify to :DiagnosticQualifier:
        - every session's INDICATES_DISORDER becomes HAS_QUALIFIER -> the qualifier
        - sessions left with no primary disorder get INDICATES_DISORDER -> PersonalityDisorder
        - remaining non-session edges moved to PersonalityDisorder, then the Disorder node deleted
  3. SuicidalIdeation / NonSuicidalSelfInjury (:Disorder) -> relabel :RiskMarker,
        INDICATES_DISORDER -> INDICATES_RISK (kept for the crisis layer; not a disorder).
  4. EatingDisorder (:Disorder parent, 176 sessions) -> relabel :DisorderCategory,
        the 6 specific eating disorders get IN_CATEGORY -> it,
        INDICATES_DISORDER -> MENTIONS_CATEGORY (connected, but not a false specific dx).

Result: exactly 100 :Disorder nodes, all carrying classification_status, every session
still connected. Credentials come from env (NEO4J_PASSWORD), falling back to the
project default so it runs out-of-the-box.

NOTE (precision): BorderlinePattern held ~47% of all disorder-linked sessions due to
low-precision semantic classification. This script makes the TAXONOMY valid and keeps
sessions connected; re-running semantic_disorder_classifier.py with tighter anchors/
thresholds is the recommended follow-up to spread those sessions more accurately.
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from neo4j import GraphDatabase

URI  = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
USER = os.environ.get("NEO4J_USER", "neo4j")
PW   = os.environ.get("NEO4J_PASSWORD", "neo4jpassword")
DB   = os.environ.get("NEO4J_DATABASE", "therapy")
assert DB == "therapy", f"refusing to run against '{DB}'"

DRIVER = GraphDatabase.driver(URI, auth=(USER, PW), max_connection_lifetime=300, keep_alive=True)

# All relationship types that can touch a Disorder node (from the pipeline schema).
REL_TYPES = [
    "INDICATES_DISORDER", "RECOMMENDED_FOR", "WORSENS", "ASSOCIATED_WITH",
    "HAS_COGNITIVE_DISTORTION", "INVOLVES_COGNITION", "MANIFESTS_AS",
    "CO_OCCURS_WITH", "SAME_AS", "MENTIONS_SYMPTOM", "SUGGESTS_TECHNIQUE",
    "EXHIBITS_BEHAVIOUR", "EXPRESSES_EMOTION", "SHOWS_PATTERN", "PROMOTES",
    "USES", "INVOLVES_CONTEXT", "TREATS", "HAS_QUALIFIER",
]

MERGE_MAP = {
    "ComplexPostTraumaticStressDisorder": "ComplexPTSD",
    "MajorDepressiveDisorder":            "SingleEpisodeDepressiveDisorder",
    "BipolarDisorder":                    "BipolarTypeIDisorder",
    "BipolarIIDisorder":                  "BipolarTypeIIDisorder",
    "ADHD":                               "AttentionDeficitHyperactivityDisorder",
    "PMDD":                               "PremenstrualDysphoricDisorder",
    "AlcoholUseDisorder":                 "AlcoholDependence",
    "PersistentDepressiveDisorder":       "DysthymicDisorder",
    "IllnessAnxietyDisorder":             "Hypochondriasis",
    "SeasonalAffectiveDisorder":          "RecurrentDepressiveDisorder",
    "BorderlinePersonalityDisorder":      "PersonalityDisorder",
}
EATING_SPECIFIC = ["AnorexiaNervosa","BulimiaNervosa","BingeEatingDisorder",
                   "AvoidantRestrictiveFoodIntakeDisorder","Pica","RuminationRegurgitationDisorder"]


def run(cy, **kw):
    with DRIVER.session(database=DB) as s:
        return s.run(cy, **kw).consume().counters


def val(cy, **kw):
    with DRIVER.session(database=DB) as s:
        r = s.run(cy, **kw).single()
        return r[0] if r else None


def sec(t):
    print(f"\n{'='*66}\n  {t}\n{'='*66}")


def repoint_all_edges(alias, canon, alias_label="Disorder", canon_label="Disorder"):
    """Move every REL_TYPE edge (both directions) from alias -> canon, skipping
    self-loops, using MERGE so no duplicate edges are created."""
    moved = 0
    for t in REL_TYPES:
        # incoming edges: (x)-[t]->(alias)  =>  (x)-[t]->(canon)
        moved += run(
            f"MATCH (x)-[r:{t}]->(a:{alias_label} {{name:$alias}}) "
            f"MATCH (c:{canon_label} {{name:$canon}}) WHERE x <> c "
            f"MERGE (x)-[:{t}]->(c) DELETE r",
            alias=alias, canon=canon).relationships_created
        # outgoing edges: (alias)-[t]->(y)  =>  (canon)-[t]->(y)
        moved += run(
            f"MATCH (a:{alias_label} {{name:$alias}})-[r:{t}]->(y) "
            f"MATCH (c:{canon_label} {{name:$canon}}) WHERE y <> c "
            f"MERGE (c)-[:{t}]->(y) DELETE r",
            alias=alias, canon=canon).relationships_created
    return moved


def main():
    DRIVER.verify_connectivity()
    cur = val("CALL db.info() YIELD name RETURN name")
    assert cur == "therapy", f"bound to {cur}"
    before = val("MATCH (d:Disorder) RETURN count(d)")
    print(f"Disorder nodes before: {before}")

    # ---- 1. Merge 11 alias/duplicate disorders into canonical ----
    sec("1. Merge alias / duplicate disorders -> canonical")
    for alias, canon in MERGE_MAP.items():
        if val("MATCH (d:Disorder {name:$n}) RETURN count(d)", n=alias) == 0:
            print(f"  - {alias}: already gone (skip)"); continue
        if val("MATCH (d:Disorder {name:$n}) RETURN count(d)", n=canon) == 0:
            print(f"  ! canonical target missing for {alias} -> {canon}; SKIPPING"); continue
        s_before = val("MATCH (:Session)-[:INDICATES_DISORDER]->(d:Disorder {name:$n}) RETURN count(*)", n=canon)
        moved = repoint_all_edges(alias, canon)
        run("MATCH (d:Disorder {name:$n}) DETACH DELETE d", n=alias)
        s_after = val("MATCH (:Session)-[:INDICATES_DISORDER]->(d:Disorder {name:$n}) RETURN count(*)", n=canon)
        print(f"  {alias:<36} -> {canon:<34} (+{moved} edges moved; sessions {s_before}->{s_after})")

    # ---- 2. BorderlinePattern (Disorder) -> DiagnosticQualifier ----
    sec("2. BorderlinePattern: :Disorder -> :DiagnosticQualifier (+ redistribute)")
    if val("MATCH (b:Disorder {name:'BorderlinePattern'}) RETURN count(b)"):
        run("MERGE (q:DiagnosticQualifier {name:'BorderlinePattern'}) "
            "ON CREATE SET q.official_name='Borderline pattern', q.icd11_code='6D11.5', "
            "q.count_as_primary_disorder=false")
        # every session tagged with borderline gets the qualifier
        c = run("MATCH (s:Session)-[r:INDICATES_DISORDER]->(b:Disorder {name:'BorderlinePattern'}) "
                "MATCH (q:DiagnosticQualifier {name:'BorderlinePattern'}) "
                "MERGE (s)-[:HAS_QUALIFIER]->(q) DELETE r")
        print(f"  sessions moved to HAS_QUALIFIER: {c.relationships_created} created, {c.relationships_deleted} INDICATES removed")
        # sessions now with NO primary disorder -> PersonalityDisorder (the disorder borderline qualifies)
        c2 = run("MATCH (s:Session)-[:HAS_QUALIFIER]->(:DiagnosticQualifier {name:'BorderlinePattern'}) "
                 "WHERE NOT (s)-[:INDICATES_DISORDER]->(:Disorder) "
                 "MATCH (pd:Disorder {name:'PersonalityDisorder'}) MERGE (s)-[:INDICATES_DISORDER]->(pd)")
        print(f"  orphaned sessions re-pointed to PersonalityDisorder: {c2.relationships_created}")
        # move any remaining non-session edges to PersonalityDisorder, then delete the bogus node
        repoint_all_edges("BorderlinePattern", "PersonalityDisorder")
        run("MATCH (b:Disorder {name:'BorderlinePattern'}) DETACH DELETE b")
        print("  deleted :Disorder BorderlinePattern (now only :DiagnosticQualifier remains)")
    else:
        print("  already reclassified (skip)")

    # ---- 3. Suicide / self-injury -> RiskMarker ----
    sec("3. SuicidalIdeation / NonSuicidalSelfInjury -> :RiskMarker")
    for rm in ["SuicidalIdeation", "NonSuicidalSelfInjury"]:
        if val("MATCH (d:Disorder {name:$n}) RETURN count(d)", n=rm) == 0:
            print(f"  - {rm}: not a Disorder (skip)"); continue
        run("MATCH (d:Disorder {name:$n}) REMOVE d:Disorder SET d:RiskMarker, d.category='risk_marker'", n=rm)
        c = run("MATCH (s:Session)-[r:INDICATES_DISORDER]->(m:RiskMarker {name:$n}) "
                "MERGE (s)-[:INDICATES_RISK]->(m) DELETE r", n=rm)
        print(f"  {rm:<24} relabelled; {c.relationships_created} INDICATES_RISK edges")

    # ---- 4. EatingDisorder parent -> DisorderCategory ----
    sec("4. EatingDisorder parent -> :DisorderCategory")
    if val("MATCH (d:Disorder {name:'EatingDisorder'}) RETURN count(d)"):
        run("MATCH (d:Disorder {name:'EatingDisorder'}) REMOVE d:Disorder SET d:DisorderCategory")
        run("MATCH (spec:Disorder) WHERE spec.name IN $specs "
            "MATCH (cat:DisorderCategory {name:'EatingDisorder'}) MERGE (spec)-[:IN_CATEGORY]->(cat)",
            specs=EATING_SPECIFIC)
        c = run("MATCH (s:Session)-[r:INDICATES_DISORDER]->(cat:DisorderCategory {name:'EatingDisorder'}) "
                "MERGE (s)-[:MENTIONS_CATEGORY]->(cat) DELETE r")
        print(f"  relabelled; {c.relationships_created} MENTIONS_CATEGORY edges; 6 IN_CATEGORY links")
    else:
        print("  already a category (skip)")

    # ---- 5. Remove EPITOME duplicate sessions (exact copy of MHCC content) ----
    sec("5. Remove EPITOME_PHR duplicate sessions (100% overlap with MHCC)")
    dup = val("MATCH (s:Session {source:'EPITOME_PHR_Counselor'}) RETURN count(s)")
    if dup:
        run("MATCH (s:Session {source:'EPITOME_PHR_Counselor'}) DETACH DELETE s")
        print(f"  removed {dup} EPITOME duplicate sessions")
    else:
        print("  none present (skip)")

    # ---- 6. Connect any fully-orphaned canonical disorder to its family ----
    sec("6. Connect fully-orphaned canonical disorders (clinical family mirror)")
    # {orphan: exemplar} — orphan inherits exemplar's clinical L2-L5 profile + co-occurs with family
    FAMILY_MIRROR = {"CyclothymicDisorder": ("BipolarTypeIIDisorder", ["BipolarTypeIDisorder", "BipolarTypeIIDisorder"])}
    # (rel type, direction): "out" = (Disorder)-[r]->(x); "in" = (x)-[r]->(Disorder)
    MIRROR_DIRS = {"MANIFESTS_AS": "out", "RECOMMENDED_FOR": "in",
                   "ASSOCIATED_WITH": "in", "WORSENS": "in", "HAS_COGNITIVE_DISTORTION": "in"}
    for orphan, (exemplar, cooccur) in FAMILY_MIRROR.items():
        if val("MATCH (d:Disorder {name:$n}) WHERE NOT (d)--() RETURN count(d)", n=orphan) == 0:
            print(f"  - {orphan}: already connected (skip)"); continue
        for t, direction in MIRROR_DIRS.items():
            if direction == "out":
                run(f"MATCH (ex:Disorder {{name:$ex}})-[:{t}]->(x) MATCH (o:Disorder {{name:$o}}) "
                    f"MERGE (o)-[:{t}]->(x)", ex=exemplar, o=orphan)
            else:
                run(f"MATCH (x)-[:{t}]->(ex:Disorder {{name:$ex}}) MATCH (o:Disorder {{name:$o}}) "
                    f"MERGE (x)-[:{t}]->(o)", ex=exemplar, o=orphan)
        for fam in cooccur:
            run("MATCH (o:Disorder {name:$o}), (f:Disorder {name:$f}) WHERE o<>f MERGE (o)-[:CO_OCCURS_WITH]->(f)", o=orphan, f=fam)
        deg = val("MATCH (d:Disorder {name:$n})--() RETURN count(*)", n=orphan)
        print(f"  {orphan}: mirrored {exemplar} + co-occurs {cooccur}  -> now {deg} edges")

    # ---- Verification ----
    sec("VERIFICATION")
    total = val("MATCH (d:Disorder) RETURN count(d)")
    with_status = val("MATCH (d:Disorder) WHERE d.classification_status IS NOT NULL RETURN count(d)")
    noncanon = val("MATCH (d:Disorder) WHERE d.classification_status IS NULL RETURN count(d)")
    orphan_sess = val("MATCH (s:Session) WHERE NOT (s)-[:INDICATES_DISORDER]->() "
                      "AND NOT (s)-[:INDICATES_RISK]->() AND NOT (s)-[:MENTIONS_CATEGORY]->() "
                      "AND NOT (s)-[:HAS_QUALIFIER]->() RETURN count(s)")
    print(f"  Disorder nodes now         : {total}   (target 100)")
    print(f"  ...with classification_status: {with_status}")
    print(f"  ...WITHOUT status (should be 0): {noncanon}")
    print(f"  fully unmapped sessions    : {orphan_sess}")
    print("\n  top disorders by sessions:")
    with DRIVER.session(database=DB) as s:
        for r in s.run("MATCH (d:Disorder)<-[:INDICATES_DISORDER]-() RETURN d.name AS n, count(*) AS c ORDER BY c DESC LIMIT 10"):
            print(f"    {r['n']:<44} {r['c']}")
    DRIVER.close()
    print("\nDONE." + ("  ✅ exactly 100 canonical disorders." if total == 100 and noncanon == 0 else "  ⚠️ review counts above."))


if __name__ == "__main__":
    main()
