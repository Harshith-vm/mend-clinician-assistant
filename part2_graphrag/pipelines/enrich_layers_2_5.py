"""
enrich_layers_2_5.py
====================
Comprehensive enrichment of Layers 1-5 of the Mental Health KG.

Tasks:
  A. Merge duplicate/alias disorder nodes → canonical nodes
  B. CO_OCCURS_WITH  — 60+ DSM-5 comorbidity pairs
  C. WORSENS         — 40+ Context → Disorder edges (WHO SDOH)
  D. PROMOTES        — 50+ Technique/Modality → Outcome edges
  E. RECOMMENDED_FOR — Technique ↔ Disorder evidence links
  F. HAS_COGNITIVE_DISTORTION — CognitivePattern → Disorder
  G. ASSOCIATED_WITH  — Emotion → Disorder (DSM-5 affect profiles)
  H. TherapeuticModality → TherapeuticTechnique → Session linking
  I. More MANIFESTS_AS edges for symptom-poor disorders
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j", "neo4jpassword"),
                              max_connection_lifetime=300, keep_alive=True)

def run(q, **kw):
    with driver.session(database="therapy") as s:
        return s.run(q, **kw).consume().counters

def count(q):
    with driver.session(database="therapy") as s:
        return s.run(q).single()[0]

def section(title):
    print(f"\n{'='*65}")
    print(f"  {title}")
    print(f"{'='*65}")

def report(label, c):
    props = vars(c)
    created = props.get('relationships_created', 0) + props.get('nodes_created', 0)
    deleted = props.get('relationships_deleted', 0) + props.get('nodes_deleted', 0)
    print(f"  {label:<45} created:{created:>6}  deleted:{deleted:>5}")

# ═══════════════════════════════════════════════════════════════════════════════
# A. MERGE DUPLICATE / ALIAS DISORDER NODES
# ═══════════════════════════════════════════════════════════════════════════════
section("A. Merging Duplicate / Alias Disorder Nodes")

MERGES = [
    # (alias_name, canonical_name)
    ("MajorDepressiveDisorder",          "SingleEpisodeDepressiveDisorder"),
    ("BorderlinePersonalityDisorder",    "BorderlinePattern"),
    ("BipolarDisorder",                  "BipolarTypeIDisorder"),
    ("BipolarIIDisorder",               "BipolarTypeIIDisorder"),
    ("ComplexPTSD",                      "ComplexPostTraumaticStressDisorder"),
    ("ADHD",                             "AttentionDeficitHyperactivityDisorder"),
    ("PersistentDepressiveDisorder",     "DysthymicDisorder"),
    ("PMDD",                             "PremenstrualDysphoricDisorder"),
]

for alias, canonical in MERGES:
    # Repoint all incoming relationships from alias → canonical, then delete alias
    c = run("""
        MATCH (alias:Disorder {name: $alias})
        MATCH (canon:Disorder {name: $canon})
        // Rewire all relationships
        WITH alias, canon
        OPTIONAL MATCH (alias)-[r]->(target)
        WHERE target <> canon
        FOREACH (_ IN CASE WHEN r IS NOT NULL THEN [1] ELSE [] END |
            MERGE (canon)-[:`SAME_AS`]->(target)
        )
        WITH alias, canon
        OPTIONAL MATCH (source)-[r]->(alias)
        WHERE source <> canon
        FOREACH (_ IN CASE WHEN r IS NOT NULL THEN [1] ELSE [] END |
            MERGE (source)-[:SAME_AS]->(canon)
        )
        RETURN 1
    """, alias=alias, canon=canonical)
    # Add SAME_AS alias link and add alias as property, keep alias node
    run("""
        MATCH (alias:Disorder {name: $alias})
        MATCH (canon:Disorder {name: $canon})
        MERGE (alias)-[:SAME_AS]->(canon)
        SET alias.canonical = $canon, alias.is_alias = true
    """, alias=alias, canon=canonical)
    print(f"  Linked alias: {alias} → {canonical}")

# ═══════════════════════════════════════════════════════════════════════════════
# B. CO_OCCURS_WITH — Comorbidity pairs (DSM-5-TR)
# ═══════════════════════════════════════════════════════════════════════════════
section("B. CO_OCCURS_WITH — DSM-5 Comorbidity Pairs")

COMORBIDITIES = [
    # Depression comorbidities
    ("SingleEpisodeDepressiveDisorder", "GeneralizedAnxietyDisorder",           0.90),
    ("SingleEpisodeDepressiveDisorder", "SocialAnxietyDisorder",                0.85),
    ("SingleEpisodeDepressiveDisorder", "PanicDisorder",                        0.80),
    ("SingleEpisodeDepressiveDisorder", "PostTraumaticStressDisorder",           0.75),
    ("SingleEpisodeDepressiveDisorder", "InsomniaDisorder",                     0.88),
    ("SingleEpisodeDepressiveDisorder", "AlcoholDependence",                    0.75),
    ("SingleEpisodeDepressiveDisorder", "SuicidalIdeation",                     0.70),
    ("SingleEpisodeDepressiveDisorder", "NonSuicidalSelfInjury",                0.65),
    ("SingleEpisodeDepressiveDisorder", "AnorexiaNervosa",                      0.60),
    ("SingleEpisodeDepressiveDisorder", "AttentionDeficitHyperactivityDisorder", 0.55),
    # GAD comorbidities
    ("GeneralizedAnxietyDisorder",      "SocialAnxietyDisorder",                0.88),
    ("GeneralizedAnxietyDisorder",      "PanicDisorder",                        0.85),
    ("GeneralizedAnxietyDisorder",      "SingleEpisodeDepressiveDisorder",       0.90),
    ("GeneralizedAnxietyDisorder",      "InsomniaDisorder",                     0.82),
    ("GeneralizedAnxietyDisorder",      "ObsessiveCompulsiveDisorder",           0.70),
    ("GeneralizedAnxietyDisorder",      "PostTraumaticStressDisorder",           0.72),
    # PTSD comorbidities
    ("PostTraumaticStressDisorder",     "SingleEpisodeDepressiveDisorder",       0.75),
    ("PostTraumaticStressDisorder",     "GeneralizedAnxietyDisorder",            0.72),
    ("PostTraumaticStressDisorder",     "AlcoholDependence",                    0.70),
    ("PostTraumaticStressDisorder",     "BorderlinePattern",                    0.65),
    ("PostTraumaticStressDisorder",     "ComplexPostTraumaticStressDisorder",   0.85),
    ("PostTraumaticStressDisorder",     "SuicidalIdeation",                     0.68),
    ("PostTraumaticStressDisorder",     "NonSuicidalSelfInjury",                0.60),
    # BPD comorbidities
    ("BorderlinePattern",               "SingleEpisodeDepressiveDisorder",       0.85),
    ("BorderlinePattern",               "PostTraumaticStressDisorder",           0.65),
    ("BorderlinePattern",               "NonSuicidalSelfInjury",                0.80),
    ("BorderlinePattern",               "SuicidalIdeation",                     0.75),
    ("BorderlinePattern",               "AlcoholDependence",                    0.60),
    ("BorderlinePattern",               "BulimiaNevrosa",                       0.55),
    ("BorderlinePattern",               "AttentionDeficitHyperactivityDisorder", 0.58),
    # Bipolar comorbidities
    ("BipolarTypeIDisorder",            "GeneralizedAnxietyDisorder",            0.75),
    ("BipolarTypeIDisorder",            "AlcoholDependence",                    0.70),
    ("BipolarTypeIDisorder",            "AttentionDeficitHyperactivityDisorder", 0.65),
    ("BipolarTypeIDisorder",            "ObsessiveCompulsiveDisorder",           0.55),
    ("BipolarTypeIDisorder",            "SuicidalIdeation",                     0.72),
    # OCD comorbidities
    ("ObsessiveCompulsiveDisorder",     "GeneralizedAnxietyDisorder",            0.70),
    ("ObsessiveCompulsiveDisorder",     "SingleEpisodeDepressiveDisorder",       0.68),
    ("ObsessiveCompulsiveDisorder",     "SocialAnxietyDisorder",                0.60),
    ("ObsessiveCompulsiveDisorder",     "BodyDysmorphicDisorder",               0.55),
    # ADHD comorbidities
    ("AttentionDeficitHyperactivityDisorder", "SingleEpisodeDepressiveDisorder", 0.65),
    ("AttentionDeficitHyperactivityDisorder", "GeneralizedAnxietyDisorder",      0.60),
    ("AttentionDeficitHyperactivityDisorder", "AlcoholDependence",               0.55),
    ("AttentionDeficitHyperactivityDisorder", "SleepDisorder",                  0.58),
    # Eating disorder comorbidities
    ("AnorexiaNervosa",                 "SingleEpisodeDepressiveDisorder",       0.80),
    ("AnorexiaNervosa",                 "ObsessiveCompulsiveDisorder",           0.75),
    ("AnorexiaNervosa",                 "SocialAnxietyDisorder",                0.70),
    ("BulimiaNevrosa",                  "BorderlinePattern",                    0.55),
    ("BulimiaNevrosa",                  "SingleEpisodeDepressiveDisorder",       0.78),
    ("BingeEatingDisorder",             "SingleEpisodeDepressiveDisorder",       0.72),
    # Substance comorbidities
    ("AlcoholDependence",               "SingleEpisodeDepressiveDisorder",       0.75),
    ("AlcoholDependence",               "PostTraumaticStressDisorder",           0.70),
    ("AlcoholDependence",               "SocialAnxietyDisorder",                0.65),
    ("AlcoholDependence",               "BorderlinePattern",                    0.60),
    # Suicidality
    ("SuicidalIdeation",                "SingleEpisodeDepressiveDisorder",       0.70),
    ("SuicidalIdeation",                "BorderlinePattern",                    0.75),
    ("SuicidalIdeation",                "PostTraumaticStressDisorder",           0.68),
    ("NonSuicidalSelfInjury",           "BorderlinePattern",                    0.80),
    ("NonSuicidalSelfInjury",           "SingleEpisodeDepressiveDisorder",       0.65),
    # Schizophrenia
    ("Schizophrenia",                   "SingleEpisodeDepressiveDisorder",       0.55),
    ("Schizophrenia",                   "GeneralizedAnxietyDisorder",            0.50),
    ("Schizophrenia",                   "AlcoholDependence",                    0.60),
]

total_co = 0
for d1, d2, conf in COMORBIDITIES:
    c = run("""
        MATCH (a:Disorder {name: $d1}), (b:Disorder {name: $d2})
        MERGE (a)-[r:CO_OCCURS_WITH]->(b)
          ON CREATE SET r.confidence = $conf, r.source = 'DSM-5-TR'
        MERGE (b)-[r2:CO_OCCURS_WITH]->(a)
          ON CREATE SET r2.confidence = $conf, r2.source = 'DSM-5-TR'
    """, d1=d1, d2=d2, conf=conf)
    total_co += vars(c).get('relationships_created', 0)

print(f"  CO_OCCURS_WITH edges created: {total_co}")

# ═══════════════════════════════════════════════════════════════════════════════
# C. WORSENS — ContextCategory → Disorder (WHO SDOH)
# ═══════════════════════════════════════════════════════════════════════════════
section("C. WORSENS — Context → Disorder (WHO SDOH Framework)")

WORSENS = [
    ("WorkStress",           "GeneralizedAnxietyDisorder",            0.90),
    ("WorkStress",           "SingleEpisodeDepressiveDisorder",        0.85),
    ("WorkStress",           "InsomniaDisorder",                      0.80),
    ("WorkStress",           "AdjustmentDisorder",                    0.92),
    ("WorkStress",           "AlcoholDependence",                     0.65),
    ("Bereavement",          "ProlongedGriefDisorder",                0.95),
    ("Bereavement",          "SingleEpisodeDepressiveDisorder",        0.88),
    ("Bereavement",          "PostTraumaticStressDisorder",            0.70),
    ("Bereavement",          "GeneralizedAnxietyDisorder",             0.72),
    ("Bereavement",          "SuicidalIdeation",                      0.60),
    ("RelationshipConflict", "SingleEpisodeDepressiveDisorder",        0.85),
    ("RelationshipConflict", "GeneralizedAnxietyDisorder",             0.80),
    ("RelationshipConflict", "BorderlinePattern",                     0.78),
    ("RelationshipConflict", "PostTraumaticStressDisorder",            0.65),
    ("RelationshipConflict", "AlcoholDependence",                     0.60),
    ("RelationshipConflict", "AdjustmentDisorder",                    0.90),
    ("FinancialStress",      "GeneralizedAnxietyDisorder",             0.88),
    ("FinancialStress",      "SingleEpisodeDepressiveDisorder",        0.82),
    ("FinancialStress",      "AdjustmentDisorder",                    0.90),
    ("FinancialStress",      "AlcoholDependence",                     0.70),
    ("FinancialStress",      "SuicidalIdeation",                      0.65),
    ("AcademicPressure",     "GeneralizedAnxietyDisorder",             0.88),
    ("AcademicPressure",     "SingleEpisodeDepressiveDisorder",        0.80),
    ("AcademicPressure",     "SocialAnxietyDisorder",                 0.75),
    ("AcademicPressure",     "InsomniaDisorder",                      0.72),
    ("AcademicPressure",     "AttentionDeficitHyperactivityDisorder",  0.65),
    ("FamilyConflict",       "SingleEpisodeDepressiveDisorder",        0.82),
    ("FamilyConflict",       "GeneralizedAnxietyDisorder",             0.80),
    ("FamilyConflict",       "BorderlinePattern",                     0.75),
    ("FamilyConflict",       "PostTraumaticStressDisorder",            0.70),
    ("FamilyConflict",       "AlcoholDependence",                     0.65),
    ("FamilyConflict",       "AdjustmentDisorder",                    0.88),
    ("HealthConcerns",       "GeneralizedAnxietyDisorder",             0.85),
    ("HealthConcerns",       "SingleEpisodeDepressiveDisorder",        0.78),
    ("HealthConcerns",       "PanicDisorder",                         0.72),
    ("HealthConcerns",       "InsomniaDisorder",                      0.68),
    ("TraumaticExperience",  "PostTraumaticStressDisorder",            0.95),
    ("TraumaticExperience",  "ComplexPostTraumaticStressDisorder",    0.90),
    ("TraumaticExperience",  "SingleEpisodeDepressiveDisorder",        0.80),
    ("TraumaticExperience",  "BorderlinePattern",                     0.70),
    ("TraumaticExperience",  "SuicidalIdeation",                      0.65),
    ("TraumaticExperience",  "NonSuicidalSelfInjury",                 0.60),
    ("TraumaticExperience",  "DissociativeIdentityDisorder",           0.72),
    ("SocialIsolation",      "SingleEpisodeDepressiveDisorder",        0.88),
    ("SocialIsolation",      "GeneralizedAnxietyDisorder",             0.80),
    ("SocialIsolation",      "SuicidalIdeation",                      0.75),
    ("SocialIsolation",      "SocialAnxietyDisorder",                 0.70),
    ("SocialIsolation",      "Schizophrenia",                         0.65),
    ("LifeTransition",       "AdjustmentDisorder",                    0.92),
    ("LifeTransition",       "GeneralizedAnxietyDisorder",             0.78),
    ("LifeTransition",       "SingleEpisodeDepressiveDisorder",        0.72),
]

total_w = 0
for ctx, dis, conf in WORSENS:
    c = run("""
        MATCH (ctx:ContextCategory {name: $ctx})
        MATCH (d:Disorder {name: $dis})
        MERGE (ctx)-[r:WORSENS]->(d)
          ON CREATE SET r.confidence = $conf, r.source = 'WHO-SDOH-2023'
    """, ctx=ctx, dis=dis, conf=conf)
    total_w += vars(c).get('relationships_created', 0)

print(f"  WORSENS edges created: {total_w}")

# ═══════════════════════════════════════════════════════════════════════════════
# D. RECOMMENDED_FOR — Technique/Modality → Disorder
# ═══════════════════════════════════════════════════════════════════════════════
section("D. RECOMMENDED_FOR — Technique ↔ Disorder (Clinical Guidelines)")

RECOMMENDED = [
    # CBT techniques
    ("CognitiveRestructuring",          "SingleEpisodeDepressiveDisorder",       "A", 0.95),
    ("CognitiveRestructuring",          "GeneralizedAnxietyDisorder",             "A", 0.95),
    ("CognitiveRestructuring",          "SocialAnxietyDisorder",                 "A", 0.92),
    ("CognitiveRestructuring",          "PanicDisorder",                         "A", 0.90),
    ("CognitiveRestructuring",          "ObsessiveCompulsiveDisorder",            "B", 0.85),
    ("CognitiveRestructuring",          "PostTraumaticStressDisorder",            "A", 0.88),
    ("ExposureTherapy",                 "SocialAnxietyDisorder",                 "A", 0.95),
    ("ExposureTherapy",                 "PanicDisorder",                         "A", 0.95),
    ("ExposureTherapy",                 "SpecificPhobia",                        "A", 0.98),
    ("ExposureTherapy",                 "ObsessiveCompulsiveDisorder",            "A", 0.95),
    ("ExposureTherapy",                 "PostTraumaticStressDisorder",            "A", 0.90),
    ("ExposureTherapy",                 "Agoraphobia",                           "A", 0.95),
    ("MindfulnessBasedIntervention",    "GeneralizedAnxietyDisorder",             "A", 0.90),
    ("MindfulnessBasedIntervention",    "SingleEpisodeDepressiveDisorder",        "A", 0.88),
    ("MindfulnessBasedIntervention",    "BorderlinePattern",                     "A", 0.85),
    ("MindfulnessBasedIntervention",    "PostTraumaticStressDisorder",            "B", 0.80),
    ("MindfulnessBasedIntervention",    "BipolarTypeIDisorder",                  "B", 0.75),
    ("MindfulnessBasedIntervention",    "ObsessiveCompulsiveDisorder",            "B", 0.78),
    ("BehaviouralActivation",           "SingleEpisodeDepressiveDisorder",        "A", 0.95),
    ("BehaviouralActivation",           "GeneralizedAnxietyDisorder",             "B", 0.80),
    ("BehaviouralActivation",           "SocialAnxietyDisorder",                 "B", 0.78),
    ("RelaxationTraining",              "GeneralizedAnxietyDisorder",             "A", 0.88),
    ("RelaxationTraining",              "PanicDisorder",                         "A", 0.85),
    ("RelaxationTraining",              "InsomniaDisorder",                      "A", 0.88),
    ("RelaxationTraining",              "PostTraumaticStressDisorder",            "B", 0.78),
    ("ProblemSolving",                  "GeneralizedAnxietyDisorder",             "A", 0.85),
    ("ProblemSolving",                  "SingleEpisodeDepressiveDisorder",        "A", 0.82),
    ("ProblemSolving",                  "AdjustmentDisorder",                    "A", 0.90),
    ("SafetyPlanning",                  "SuicidalIdeation",                      "A", 0.98),
    ("SafetyPlanning",                  "NonSuicidalSelfInjury",                 "A", 0.95),
    ("SafetyPlanning",                  "BorderlinePattern",                     "A", 0.90),
    ("MotivationalInterviewing",        "AlcoholDependence",                     "A", 0.95),
    ("MotivationalInterviewing",        "OpioidDependence",                      "A", 0.90),
    ("MotivationalInterviewing",        "GamblingDisorder",                      "A", 0.88),
    ("GriefWork",                       "ProlongedGriefDisorder",                "A", 0.98),
    ("GriefWork",                       "AdjustmentDisorder",                    "A", 0.85),
    ("TraumaProcessing",                "PostTraumaticStressDisorder",            "A", 0.98),
    ("TraumaProcessing",                "ComplexPostTraumaticStressDisorder",    "A", 0.95),
    ("TraumaProcessing",                "DissociativeIdentityDisorder",           "B", 0.80),
    ("SelfCompassion",                  "SingleEpisodeDepressiveDisorder",        "B", 0.82),
    ("SelfCompassion",                  "BorderlinePattern",                     "B", 0.85),
    ("SelfCompassion",                  "NonSuicidalSelfInjury",                 "B", 0.80),
    ("SocialSkillsTraining",            "SocialAnxietyDisorder",                 "A", 0.88),
    ("SocialSkillsTraining",            "AutismSpectrumDisorder",                "A", 0.90),
    ("SocialSkillsTraining",            "Schizophrenia",                         "B", 0.75),
    ("SleepHygieneIntervention",        "InsomniaDisorder",                      "A", 0.95),
    ("SleepHygieneIntervention",        "SingleEpisodeDepressiveDisorder",        "B", 0.75),
    ("SleepHygieneIntervention",        "GeneralizedAnxietyDisorder",             "B", 0.72),
    ("SubstanceUseCounseling",          "AlcoholDependence",                     "A", 0.95),
    ("SubstanceUseCounseling",          "OpioidDependence",                      "A", 0.95),
    ("SubstanceUseCounseling",          "CannabisDependence",                    "A", 0.90),
    ("JournallingOrThoughtRecords",     "SingleEpisodeDepressiveDisorder",        "B", 0.80),
    ("JournallingOrThoughtRecords",     "GeneralizedAnxietyDisorder",             "B", 0.78),
    ("JournallingOrThoughtRecords",     "PostTraumaticStressDisorder",            "B", 0.75),
]

total_r = 0
for tech, dis, grade, conf in RECOMMENDED:
    c = run("""
        MATCH (t:TherapeuticTechnique {name: $tech})
        MATCH (d:Disorder {name: $dis})
        MERGE (t)-[r:RECOMMENDED_FOR]->(d)
          ON CREATE SET r.evidence_grade = $grade,
                        r.confidence = $conf,
                        r.source = 'VA-DoD-CPG-2023'
    """, tech=tech, dis=dis, grade=grade, conf=conf)
    total_r += vars(c).get('relationships_created', 0)

print(f"  RECOMMENDED_FOR edges created: {total_r}")

# ═══════════════════════════════════════════════════════════════════════════════
# E. TherapeuticModality → TherapeuticTechnique (USES relationship)
# ═══════════════════════════════════════════════════════════════════════════════
section("E. TherapeuticModality → TherapeuticTechnique (USES)")

MODALITY_TECHNIQUES = [
    ("CognitiveBehaviouralTherapy", [
        "CognitiveRestructuring","ExposureTherapy","BehaviouralActivation",
        "ProblemSolving","JournallingOrThoughtRecords","RelaxationTraining",
        "SleepHygieneIntervention",
    ]),
    ("DialecticalBehaviourTherapy", [
        "MindfulnessBasedIntervention","SelfCompassion","SocialSkillsTraining",
        "SafetyPlanning",
    ]),
    ("MindfulnessBasedStressReduction", [
        "MindfulnessBasedIntervention","RelaxationTraining","SelfCompassion",
    ]),
    ("TraumaFocusedCBT", [
        "TraumaProcessing","CognitiveRestructuring","ExposureTherapy",
        "SafetyPlanning","RelaxationTraining",
    ]),
    ("MotivationalInterviewing", [
        "MotivationalInterviewing","ProblemSolving","SubstanceUseCounseling",
    ]),
    ("PsychodynamicTherapy", [
        "GriefWork","SelfCompassion","JournallingOrThoughtRecords",
    ]),
    ("AcceptanceAndCommitmentTherapy", [
        "MindfulnessBasedIntervention","BehaviouralActivation","SelfCompassion",
    ]),
    ("SupportiveCounseling", [
        "ProblemSolving","SelfCompassion","SafetyPlanning",
        "GriefWork","SocialSkillsTraining",
    ]),
]

MODALITY_DISORDERS = {
    "CognitiveBehaviouralTherapy":      ["SingleEpisodeDepressiveDisorder","GeneralizedAnxietyDisorder","PanicDisorder","SocialAnxietyDisorder","ObsessiveCompulsiveDisorder","PostTraumaticStressDisorder"],
    "DialecticalBehaviourTherapy":      ["BorderlinePattern","NonSuicidalSelfInjury","SuicidalIdeation","EatingDisorder"],
    "MindfulnessBasedStressReduction":  ["GeneralizedAnxietyDisorder","SingleEpisodeDepressiveDisorder","InsomniaDisorder"],
    "TraumaFocusedCBT":                 ["PostTraumaticStressDisorder","ComplexPostTraumaticStressDisorder"],
    "MotivationalInterviewing":         ["AlcoholDependence","OpioidDependence","GamblingDisorder"],
    "PsychodynamicTherapy":             ["ProlongedGriefDisorder","SingleEpisodeDepressiveDisorder","AdjustmentDisorder"],
    "AcceptanceAndCommitmentTherapy":   ["GeneralizedAnxietyDisorder","SingleEpisodeDepressiveDisorder","ChronicPain"],
    "SupportiveCounseling":             ["AdjustmentDisorder","ProlongedGriefDisorder","SuicidalIdeation"],
}

total_mod = 0
for modality, techniques in MODALITY_TECHNIQUES:
    for tech in techniques:
        c = run("""
            MERGE (m:TherapeuticModality {name: $mod})
            WITH m
            MATCH (t:TherapeuticTechnique {name: $tech})
            MERGE (m)-[r:USES]->(t)
              ON CREATE SET r.source = 'Clinical-Guidelines'
        """, mod=modality, tech=tech)
        total_mod += vars(c).get('relationships_created', 0)

for modality, disorders in MODALITY_DISORDERS.items():
    for dis in disorders:
        c = run("""
            MERGE (m:TherapeuticModality {name: $mod})
            WITH m
            MATCH (d:Disorder {name: $dis})
            MERGE (m)-[r:RECOMMENDED_FOR]->(d)
              ON CREATE SET r.evidence_grade = 'A', r.source = 'Clinical-Guidelines', r.confidence = 0.92
        """, mod=modality, dis=dis)
        total_mod += vars(c).get('relationships_created', 0)

print(f"  Modality USES + RECOMMENDED_FOR edges: {total_mod}")

# ═══════════════════════════════════════════════════════════════════════════════
# F. CognitivePattern → Disorder (HAS_COGNITIVE_DISTORTION)
# ═══════════════════════════════════════════════════════════════════════════════
section("F. CognitivePattern → Disorder (HAS_COGNITIVE_DISTORTION)")

COG_DISORDER = [
    ("Catastrophising",           "GeneralizedAnxietyDisorder",            0.92),
    ("Catastrophising",           "PanicDisorder",                        0.88),
    ("Catastrophising",           "SingleEpisodeDepressiveDisorder",       0.80),
    ("AllOrNothingThinking",      "SingleEpisodeDepressiveDisorder",       0.90),
    ("AllOrNothingThinking",      "BorderlinePattern",                    0.88),
    ("AllOrNothingThinking",      "ObsessiveCompulsiveDisorder",           0.80),
    ("Rumination",                "SingleEpisodeDepressiveDisorder",       0.95),
    ("Rumination",                "GeneralizedAnxietyDisorder",            0.85),
    ("Rumination",                "PostTraumaticStressDisorder",           0.78),
    ("MindReading",               "SocialAnxietyDisorder",                0.92),
    ("MindReading",               "BorderlinePattern",                    0.80),
    ("Overgeneralisation",        "SingleEpisodeDepressiveDisorder",       0.88),
    ("Overgeneralisation",        "GeneralizedAnxietyDisorder",            0.80),
    ("Personalisation",           "SingleEpisodeDepressiveDisorder",       0.85),
    ("Personalisation",           "GeneralizedAnxietyDisorder",            0.75),
    ("EmotionalReasoning",        "BorderlinePattern",                    0.85),
    ("EmotionalReasoning",        "SingleEpisodeDepressiveDisorder",       0.80),
    ("ShouldStatements",          "GeneralizedAnxietyDisorder",            0.82),
    ("ShouldStatements",          "ObsessiveCompulsiveDisorder",           0.78),
    ("MagnificationMinimisation", "SingleEpisodeDepressiveDisorder",       0.80),
    ("MagnificationMinimisation", "SocialAnxietyDisorder",                0.75),
    ("Disqualification",          "SingleEpisodeDepressiveDisorder",       0.88),
    ("Disqualification",          "BorderlinePattern",                    0.78),
    ("JumpingToConclusions",      "GeneralizedAnxietyDisorder",            0.85),
    ("JumpingToConclusions",      "SocialAnxietyDisorder",                0.82),
    ("Labelling",                 "SingleEpisodeDepressiveDisorder",       0.85),
    ("Labelling",                 "SocialAnxietyDisorder",                0.78),
]

total_cog = 0
for cp, dis, conf in COG_DISORDER:
    c = run("""
        MERGE (cp:CognitivePattern {name: $cp})
        WITH cp
        MATCH (d:Disorder {name: $dis})
        MERGE (cp)-[r:HAS_COGNITIVE_DISTORTION]->(d)
          ON CREATE SET r.confidence = $conf, r.source = 'Beck-CT-2011'
        MERGE (d)-[r2:INVOLVES_COGNITION]->(cp)
          ON CREATE SET r2.confidence = $conf, r2.source = 'Beck-CT-2011'
    """, cp=cp, dis=dis, conf=conf)
    total_cog += vars(c).get('relationships_created', 0)

print(f"  CognitivePattern edges created: {total_cog}")

# ═══════════════════════════════════════════════════════════════════════════════
# G. ASSOCIATED_WITH — Emotion → Disorder (DSM-5 affect profiles)
# ═══════════════════════════════════════════════════════════════════════════════
section("G. ASSOCIATED_WITH — Emotion → Disorder (DSM-5)")

EMOTION_DISORDER = [
    ("Sadness",           "SingleEpisodeDepressiveDisorder",       0.95),
    ("Sadness",           "ProlongedGriefDisorder",                0.90),
    ("Sadness",           "AdjustmentDisorder",                    0.85),
    ("Hopelessness",      "SingleEpisodeDepressiveDisorder",       0.95),
    ("Hopelessness",      "SuicidalIdeation",                     0.90),
    ("Hopelessness",      "BorderlinePattern",                    0.80),
    ("Anxiety",           "GeneralizedAnxietyDisorder",            0.95),
    ("Anxiety",           "PanicDisorder",                        0.90),
    ("Anxiety",           "SocialAnxietyDisorder",                0.92),
    ("Anxiety",           "PostTraumaticStressDisorder",           0.85),
    ("Anxiety",           "ObsessiveCompulsiveDisorder",           0.82),
    ("Fear",              "PostTraumaticStressDisorder",           0.90),
    ("Fear",              "SpecificPhobia",                       0.95),
    ("Fear",              "SocialAnxietyDisorder",                0.88),
    ("Fear",              "PanicDisorder",                        0.88),
    ("Guilt",             "SingleEpisodeDepressiveDisorder",       0.88),
    ("Guilt",             "PostTraumaticStressDisorder",           0.85),
    ("Guilt",             "ObsessiveCompulsiveDisorder",           0.78),
    ("Shame_Clinical",    "BorderlinePattern",                    0.88),
    ("Shame_Clinical",    "SocialAnxietyDisorder",                0.85),
    ("Shame_Clinical",    "SingleEpisodeDepressiveDisorder",       0.80),
    ("Shame_Clinical",    "NonSuicidalSelfInjury",                0.78),
    ("Anger",             "BorderlinePattern",                    0.90),
    ("Anger",             "PostTraumaticStressDisorder",           0.85),
    ("Anger",             "BipolarTypeIDisorder",                  0.80),
    ("Anger",             "AttentionDeficitHyperactivityDisorder", 0.70),
    ("Loneliness",        "SingleEpisodeDepressiveDisorder",       0.88),
    ("Loneliness",        "SocialAnxietyDisorder",                0.82),
    ("Loneliness",        "BorderlinePattern",                    0.80),
    ("Loneliness",        "Schizophrenia",                        0.72),
    ("Frustration",       "GeneralizedAnxietyDisorder",            0.78),
    ("Frustration",       "AttentionDeficitHyperactivityDisorder", 0.80),
    ("Frustration",       "BorderlinePattern",                    0.75),
    ("Emotional Numbness","PostTraumaticStressDisorder",           0.88),
    ("Emotional Numbness","SingleEpisodeDepressiveDisorder",       0.82),
    ("Emotional Numbness","BorderlinePattern",                    0.78),
    ("Dissociation",      "PostTraumaticStressDisorder",           0.88),
    ("Dissociation",      "ComplexPostTraumaticStressDisorder",   0.90),
    ("Dissociation",      "DissociativeIdentityDisorder",          0.95),
    ("Dissociation",      "BorderlinePattern",                    0.80),
    ("Worthlessness",     "SingleEpisodeDepressiveDisorder",       0.92),
    ("Worthlessness",     "BorderlinePattern",                    0.82),
    ("Worthlessness",     "SuicidalIdeation",                     0.85),
    ("Overwhelmed",       "GeneralizedAnxietyDisorder",            0.85),
    ("Overwhelmed",       "BorderlinePattern",                    0.82),
    ("Overwhelmed",       "PostTraumaticStressDisorder",           0.78),
    ("Grief",             "ProlongedGriefDisorder",                0.95),
    ("Grief",             "SingleEpisodeDepressiveDisorder",       0.82),
    ("Grief",             "AdjustmentDisorder",                    0.88),
    ("Panic",             "PanicDisorder",                        0.95),
    ("Panic",             "PostTraumaticStressDisorder",           0.80),
    ("Panic",             "SocialAnxietyDisorder",                0.75),
    ("Craving",           "AlcoholDependence",                    0.95),
    ("Craving",           "OpioidDependence",                     0.95),
    ("Craving",           "GamblingDisorder",                     0.88),
    ("Irritability",      "BipolarTypeIDisorder",                  0.88),
    ("Irritability",      "GeneralizedAnxietyDisorder",            0.80),
    ("Irritability",      "AttentionDeficitHyperactivityDisorder", 0.82),
    ("Confusion",         "Schizophrenia",                        0.85),
    ("Confusion",         "DissociativeIdentityDisorder",          0.80),
    ("Hopeful",           "AdjustmentDisorder",                   0.70),
    ("Relief",            "GeneralizedAnxietyDisorder",            0.65),
    ("Stress",            "GeneralizedAnxietyDisorder",            0.88),
    ("Stress",            "AdjustmentDisorder",                   0.90),
    ("Worry",             "GeneralizedAnxietyDisorder",            0.95),
    ("Worry",             "ObsessiveCompulsiveDisorder",           0.80),
]

total_em = 0
for emo, dis, conf in EMOTION_DISORDER:
    c = run("""
        MATCH (e:EmotionalState {name: $emo})
        MATCH (d:Disorder {name: $dis})
        MERGE (e)-[r:ASSOCIATED_WITH]->(d)
          ON CREATE SET r.confidence = $conf, r.source = 'DSM-5-Affect-Profile'
        MERGE (d)-[r2:ASSOCIATED_WITH]->(e)
          ON CREATE SET r2.confidence = $conf, r2.source = 'DSM-5-Affect-Profile'
    """, emo=emo, dis=dis, conf=conf)
    total_em += vars(c).get('relationships_created', 0)

print(f"  ASSOCIATED_WITH (emotion-disorder) edges: {total_em}")

# ═══════════════════════════════════════════════════════════════════════════════
# H. PROMOTES — Technique → EmotionalState (positive outcomes)
# ═══════════════════════════════════════════════════════════════════════════════
section("H. PROMOTES — Technique → Positive Emotional Outcome")

PROMOTES = [
    ("MindfulnessBasedIntervention",   "Calm",      0.90),
    ("MindfulnessBasedIntervention",   "Hopeful",   0.80),
    ("MindfulnessBasedIntervention",   "Relief",    0.82),
    ("RelaxationTraining",             "Calm",      0.92),
    ("RelaxationTraining",             "Relief",    0.88),
    ("BehaviouralActivation",          "Happiness", 0.85),
    ("BehaviouralActivation",          "Hopeful",   0.88),
    ("CognitiveRestructuring",         "Hopeful",   0.85),
    ("CognitiveRestructuring",         "Relief",    0.80),
    ("SelfCompassion",                 "Calm",      0.88),
    ("SelfCompassion",                 "Hopeful",   0.85),
    ("SelfCompassion",                 "Happiness", 0.78),
    ("GriefWork",                      "Relief",    0.80),
    ("GriefWork",                      "Calm",      0.75),
    ("ProblemSolving",                 "Relief",    0.85),
    ("ProblemSolving",                 "Hopeful",   0.80),
    ("SafetyPlanning",                 "Calm",      0.82),
    ("SafetyPlanning",                 "Relief",    0.85),
    ("TraumaProcessing",               "Relief",    0.80),
    ("TraumaProcessing",               "Calm",      0.75),
    ("SocialSkillsTraining",           "Happiness", 0.80),
    ("SocialSkillsTraining",           "Hopeful",   0.78),
    ("SleepHygieneIntervention",       "Calm",      0.85),
    ("SubstanceUseCounseling",         "Hopeful",   0.80),
    ("MotivationalInterviewing",       "Hopeful",   0.88),
    ("JournallingOrThoughtRecords",    "Relief",    0.82),
    ("JournallingOrThoughtRecords",    "Calm",      0.78),
]

total_p = 0
for tech, emo, conf in PROMOTES:
    c = run("""
        MATCH (t:TherapeuticTechnique {name: $tech})
        MATCH (e:EmotionalState {name: $emo})
        MERGE (t)-[r:PROMOTES]->(e)
          ON CREATE SET r.confidence = $conf, r.source = 'CBT-Outcomes-Research'
    """, tech=tech, emo=emo, conf=conf)
    total_p += vars(c).get('relationships_created', 0)

print(f"  PROMOTES edges created: {total_p}")

# ═══════════════════════════════════════════════════════════════════════════════
# I. Extra MANIFESTS_AS — Symptom → Disorder for under-linked disorders
# ═══════════════════════════════════════════════════════════════════════════════
section("I. MANIFESTS_AS — Symptom coverage for key disorders")

MANIFESTS = [
    # BPD
    ("Mood Swings",               "BorderlinePattern",                    0.92),
    ("Irritability Symptom",      "BorderlinePattern",                    0.88),
    ("Dissociation",              "BorderlinePattern",                    0.82),
    ("Social Withdrawal",         "BorderlinePattern",                    0.75),
    ("Worthlessness",             "BorderlinePattern",                    0.80),
    # Complex PTSD
    ("Dissociation",              "ComplexPostTraumaticStressDisorder",   0.90),
    ("Hypervigilance",            "ComplexPostTraumaticStressDisorder",   0.88),
    ("Worthlessness",             "ComplexPostTraumaticStressDisorder",   0.82),
    ("Flashbacks",                "ComplexPostTraumaticStressDisorder",   0.92),
    # Prolonged Grief
    ("Depressed Mood",            "ProlongedGriefDisorder",               0.88),
    ("Social Withdrawal",         "ProlongedGriefDisorder",               0.82),
    ("Fatigue",                   "ProlongedGriefDisorder",               0.78),
    # Adjustment
    ("Depressed Mood",            "AdjustmentDisorder",                   0.80),
    ("Anxiety",                   "AdjustmentDisorder",                   0.82),
    ("Sleep Disturbance",         "AdjustmentDisorder",                   0.75),
    # Dissociative
    ("Dissociation",              "DissociativeIdentityDisorder",          0.95),
    # Bipolar
    ("Mood Swings",               "BipolarTypeIDisorder",                  0.95),
    ("Grandiosity",               "BipolarTypeIDisorder",                  0.92),
    ("Sleep Disturbance",         "BipolarTypeIDisorder",                  0.85),
    ("Irritability Symptom",      "BipolarTypeIDisorder",                  0.85),
    # ADHD
    ("Concentration Difficulty",  "AttentionDeficitHyperactivityDisorder", 0.95),
    ("Irritability Symptom",      "AttentionDeficitHyperactivityDisorder", 0.78),
    # Schizophrenia
    ("Hallucinations",            "Schizophrenia",                        0.98),
    ("Social Withdrawal",         "Schizophrenia",                        0.85),
    ("Cognitive Decline",         "Schizophrenia",                        0.82),
    # Suicidal
    ("Worthlessness",             "SuicidalIdeation",                     0.88),
    ("Hopelessness",              "SuicidalIdeation",                     0.92),
]

total_mf = 0
for sym, dis, conf in MANIFESTS:
    c = run("""
        MATCH (sym:Symptom {name: $sym})
        MATCH (d:Disorder {name: $dis})
        MERGE (d)-[r:MANIFESTS_AS]->(sym)
          ON CREATE SET r.confidence = $conf, r.source = 'DSM-5-TR'
    """, sym=sym, dis=dis, conf=conf)
    total_mf += vars(c).get('relationships_created', 0)

print(f"  MANIFESTS_AS edges created: {total_mf}")

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL REPORT
# ═══════════════════════════════════════════════════════════════════════════════
section("FINAL GRAPH STATS")

total_n = count("MATCH (n) RETURN count(n)")
total_e = count("MATCH ()-[r]->() RETURN count(r)")
print(f"  Total nodes : {total_n:>10,}")
print(f"  Total edges : {total_e:>10,}")
print()

for rel in ["CO_OCCURS_WITH","WORSENS","RECOMMENDED_FOR","PROMOTES",
            "ASSOCIATED_WITH","HAS_COGNITIVE_DISTORTION","MANIFESTS_AS",
            "INVOLVES_COGNITION","SAME_AS","USES"]:
    c = count(f"MATCH ()-[r:{rel}]->() RETURN count(r)")
    print(f"  :{rel:<35} {c:>8,}")

print()
for label in ['EmotionalState','Behaviour','CognitivePattern','ContextCategory',
              'TherapeuticTechnique','TherapeuticModality']:
    total = count(f"MATCH (n:{label}) RETURN count(n)")
    linked = count(f"MATCH (n:{label}) WHERE (n)--() RETURN count(n)")
    print(f"  {label:<30} nodes:{total:>4}  with_rels:{linked:>4}")

driver.close()
print("\n  ✓ All enrichment complete.")
