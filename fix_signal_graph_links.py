"""
fix_signal_graph_links.py
=========================
Adds missing ASSOCIATED_WITH edges from EmotionalState nodes to Disorders
so that query_by_signals() can traverse via emotion -> disorder -> technique.
Also adds direct ASSOCIATED_WITH edges from Disorder -> TherapeuticTechnique
for disorders that currently have none.

Safe to re-run (MERGE is idempotent).
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

URI  = os.environ.get("NEO4J_URI",      "bolt://localhost:7687")
USER = os.environ.get("NEO4J_USER",     "neo4j")
PW   = os.environ.get("NEO4J_PASSWORD", "neo4jpassword")

with open(".env") as f:
    for line in f:
        if line.startswith("NEO4J_PASSWORD="):
            PW = line.strip().split("=", 1)[1]
            break

driver = GraphDatabase.driver(URI, auth=(USER, PW))

# ── 1. EMOTION → DISORDER edges (ASSOCIATED_WITH) ──────────────────────────────
# These are the clinically correct links that the structured_query needs.
EMOTION_DISORDER_LINKS = [
    # shame_guilt / shame
    ("Shame",      "ObesityOrOverweight",               0.70),
    ("Shame",      "EatingDisordersUnspecified",         0.72),
    ("Shame",      "SocialAnxietyDisorder",              0.80),
    ("Shame",      "BodyDysmorphicDisorder",             0.88),
    ("Shame",      "ExcoriationDisorder",                0.82),
    ("Shame",      "Trichotillomania",                   0.80),
    ("Shame",      "SingleEpisodeDepressiveDisorder",    0.75),
    ("Shame",      "NonSuicidalSelfInjury",              0.78),
    ("Guilt",      "SingleEpisodeDepressiveDisorder",    0.85),
    ("Guilt",      "RecurrentDepressiveDisorder",        0.82),
    ("Guilt",      "ObsessiveCompulsiveDisorder",        0.78),
    ("Guilt",      "PostTraumaticStressDisorder",        0.80),
    # anger
    ("Anger",      "BorderlinePersonalityDisorder",      0.85),
    ("Anger",      "IntermittentExplosiveDisorder",      0.92),
    ("Anger",      "OppositionalDefiantDisorder",        0.88),
    ("Anger",      "ConductDisorder",                    0.83),
    ("Anger",      "SubstanceUseDependenceDisorder",     0.72),
    # fear / anxiety
    ("Anxiety",    "GeneralisedAnxietyDisorder",         0.95),
    ("Anxiety",    "PanicDisorder",                      0.90),
    ("Anxiety",    "SpecificPhobia",                     0.88),
    ("Anxiety",    "SocialAnxietyDisorder",              0.90),
    ("Anxiety",    "ObsessiveCompulsiveDisorder",        0.85),
    ("Anxiety",    "PostTraumaticStressDisorder",        0.80),
    ("Anxiety",    "SeparationAnxietyDisorder",          0.87),
    ("Anxiety",    "SelectiveMutism",                    0.82),
    ("Fear",       "SelectiveMutism",                    0.88),
    ("Fear",       "AgrophobiaWithOrWithoutPanicDisorder", 0.90),
    # sadness / grief / hopelessness
    ("Hopelessness","SingleEpisodeDepressiveDisorder",   0.92),
    ("Hopelessness","RecurrentDepressiveDisorder",       0.90),
    ("Hopelessness","DysthymicDisorder",                 0.85),
    ("Grief",      "ProlongedGriefDisorder",             0.95),
    ("Grief",      "AdjustmentDisorder",                 0.88),
    ("Loneliness", "SingleEpisodeDepressiveDisorder",    0.75),
    ("Loneliness", "SocialAnxietyDisorder",              0.80),
    ("Loneliness", "AvoidantPersonalityDisorder",        0.82),
    # dissociation / confusion
    ("Dissociation","DissociativeIdentityDisorder",      0.92),
    ("Dissociation","DepersonalizationDerealizationDisorder", 0.95),
    ("Dissociation","PostTraumaticStressDisorder",       0.80),
    ("Confusion",  "DissociativeIdentityDisorder",       0.75),
    ("Confusion",  "DepersonalizationDerealizationDisorder", 0.82),
    # emptiness
    ("Emptiness",  "BorderlinePersonalityDisorder",      0.88),
    ("Emptiness",  "SingleEpisodeDepressiveDisorder",    0.78),
    # worthlessness
    ("Worthlessness","SingleEpisodeDepressiveDisorder",  0.92),
    ("Worthlessness","BorderlinePersonalityDisorder",    0.80),
]

# ── 2. DISORDER → TECHNIQUE links (RECOMMENDED_FOR) ────────────────────────────
# Critical: add techniques for rare disorders that currently have none.
DISORDER_TECHNIQUE_LINKS = [
    ("BodyDysmorphicDisorder",           "CognitiveBehaviouralTherapy",        0.95),
    ("BodyDysmorphicDisorder",           "ExposureAndResponsePrevention",       0.92),
    ("BodyDysmorphicDisorder",           "MindfulnessBasedIntervention",        0.82),
    ("Trichotillomania",                 "HabitReversalTraining",               0.95),
    ("Trichotillomania",                 "CognitiveBehaviouralTherapy",         0.88),
    ("Trichotillomania",                 "AcceptanceAndCommitmentTherapy",      0.80),
    ("ExcoriationDisorder",              "HabitReversalTraining",               0.92),
    ("ExcoriationDisorder",              "CognitiveBehaviouralTherapy",         0.88),
    ("ExcoriationDisorder",              "AcceptanceAndCommitmentTherapy",      0.82),
    ("HoardingDisorder",                 "CognitiveBehaviouralTherapy",         0.90),
    ("HoardingDisorder",                 "MotivationalInterviewing",            0.85),
    ("HoardingDisorder",                 "ExposureAndResponsePrevention",       0.80),
    ("SelectiveMutism",                  "CognitiveBehaviouralTherapy",         0.88),
    ("SelectiveMutism",                  "GradedExposure",                      0.92),
    ("SelectiveMutism",                  "PlayTherapy",                         0.85),
    ("DepersonalizationDerealizationDisorder", "GroundingExercise",             0.92),
    ("DepersonalizationDerealizationDisorder", "CognitiveBehaviouralTherapy",   0.88),
    ("DepersonalizationDerealizationDisorder", "MindfulnessBasedIntervention",  0.85),
    ("OlfactoryReferenceDisorder",       "CognitiveBehaviouralTherapy",         0.90),
    ("OlfactoryReferenceDisorder",       "ExposureAndResponsePrevention",       0.85),
    ("DissociativeIdentityDisorder",     "TraumaFocusedCBT",                    0.92),
    ("DissociativeIdentityDisorder",     "EmdrTherapy",                         0.90),
    ("DissociativeIdentityDisorder",     "DialecticalBehaviourTherapy",         0.85),
]

def run(cypher, **params):
    with driver.session(database="therapy") as s:
        r = s.run(cypher, **params)
        return r.consume().counters

print("=== Adding ASSOCIATED_WITH edges: EmotionalState → Disorder ===")
added = 0
for emotion_name, disorder_name, conf in EMOTION_DISORDER_LINKS:
    c = run("""
        MATCH (e:EmotionalState {name: $emo})
        MATCH (d:Disorder {name: $dis})
        MERGE (e)-[r:ASSOCIATED_WITH]->(d)
        ON CREATE SET r.confidence = $conf, r.source = 'fix_signal_graph_links'
    """, emo=emotion_name, dis=disorder_name, conf=conf)
    if c.relationships_created > 0:
        added += 1
        print(f"  + ASSOCIATED_WITH: {emotion_name} → {disorder_name}")
    else:
        print(f"  . exists: {emotion_name} → {disorder_name}")

print(f"\nAdded {added} new ASSOCIATED_WITH edges.")

print("\n=== Adding RECOMMENDED_FOR edges: TherapeuticTechnique → Disorder ===")
added2 = 0
for disorder_name, technique_name, conf in DISORDER_TECHNIQUE_LINKS:
    c = run("""
        MERGE (t:TherapeuticTechnique {name: $tech})
        WITH t
        MATCH (d:Disorder {name: $dis})
        MERGE (t)-[r:RECOMMENDED_FOR]->(d)
        ON CREATE SET r.confidence = $conf, r.source = 'fix_signal_graph_links'
    """, tech=technique_name, dis=disorder_name, conf=conf)
    if c.relationships_created > 0:
        added2 += 1
        print(f"  + RECOMMENDED_FOR: {technique_name} → {disorder_name}")

print(f"\nAdded {added2} new RECOMMENDED_FOR edges.")

driver.close()
print("\nDone.")
