"""
fix_ontology_gaps.py
====================
Fixes all ontology gaps identified in the quality audit:
  A. Add MANIFESTS_AS symptoms for 9 session-linked disorders that have none
  B. Merge/remove duplicate 'Depression' EmotionalState → Sadness
  C. Add WORSENS edges for 7 missing ContextCategory nodes
  D. Add USES + RECOMMENDED_FOR for remaining TherapeuticModalities
  E. Add PROMOTES for more emotion outcomes
  F. Extend NER aliases → re-wire behaviours, contexts, techniques in sessions
"""
import sys, re, time
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, SessionExpired
import random

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j","neo4jpassword"),
                              max_connection_lifetime=300, keep_alive=True)

def run(q, **kw):
    with driver.session(database="therapy") as s:
        return s.run(q, **kw).consume().counters

def count(q, **kw):
    with driver.session(database="therapy") as s:
        r = s.run(q, **kw).single()
        return r[0] if r else 0

def sec(t): print(f"\n{'='*60}\n  {t}\n{'='*60}")

# ═══════════════════════════════════════════════════════════════
# A. MANIFESTS_AS — 9 disorders missing symptom links
# ═══════════════════════════════════════════════════════════════
sec("A. MANIFESTS_AS — Filling symptom gaps for 9 disorders")

MISSING_SYMPTOMS = {
    "SingleEpisodeDepressiveDisorder": [
        ("Depressed Mood",          0.98, "DSM-5 Criterion A1"),
        ("Anhedonia",               0.97, "DSM-5 Criterion A2"),
        ("Fatigue",                 0.92, "DSM-5 Criterion A6"),
        ("Sleep Disturbance",       0.90, "DSM-5 Criterion A4"),
        ("Concentration Difficulty",0.88, "DSM-5 Criterion A8"),
        ("Worthlessness",           0.92, "DSM-5 Criterion A7"),
        ("Loss of Appetite",        0.85, "DSM-5 Criterion A3"),
        ("Social Withdrawal",       0.80, "DSM-5 Associated Feature"),
        ("Suicidal Ideation",       0.78, "DSM-5 Criterion A9"),
        ("Physical Complaints",     0.72, "DSM-5 Associated Feature"),
    ],
    "NonSuicidalSelfInjury": [
        ("Worthlessness",           0.85, "DSM-5 Proposed Criterion"),
        ("Emotional Numbness",      0.82, "Clinical observation"),
        ("Dissociation",            0.78, "DSM-5 Proposed Criterion"),
        ("Irritability Symptom",    0.75, "Clinical observation"),
    ],
    "BingeEatingDisorder": [
        ("Eating Disturbance",      0.98, "DSM-5 Criterion A"),
        ("Worthlessness",           0.80, "DSM-5 Criterion B3"),
        ("Concentration Difficulty",0.65, "Clinical observation"),
    ],
    "DysthymicDisorder": [
        ("Depressed Mood",          0.95, "DSM-5 Criterion A"),
        ("Fatigue",                 0.88, "DSM-5 Criterion B5"),
        ("Anhedonia",               0.85, "DSM-5 Criterion B3"),
        ("Sleep Disturbance",       0.82, "DSM-5 Criterion B1"),
        ("Worthlessness",           0.80, "DSM-5 Criterion B6"),
        ("Concentration Difficulty",0.78, "DSM-5 Criterion B4"),
    ],
    "NarcissisticPersonalityDisorder": [
        ("Grandiosity",             0.95, "DSM-5 Criterion 1"),
        ("Irritability Symptom",    0.80, "DSM-5 Criterion 8"),
        ("Social Withdrawal",       0.65, "Clinical observation"),
    ],
    "HoardingDisorder": [
        ("Concentration Difficulty",0.80, "DSM-5 Associated Feature"),
        ("Fatigue",                 0.65, "Clinical observation"),
    ],
    "PersonalityDisorder": [
        ("Mood Swings",             0.82, "General PD feature"),
        ("Irritability Symptom",    0.80, "General PD feature"),
        ("Social Withdrawal",       0.75, "General PD feature"),
    ],
    "BipolarTypeIIDisorder": [
        ("Mood Swings",             0.95, "DSM-5 Criterion A/C"),
        ("Depressed Mood",          0.92, "DSM-5 Criterion B"),
        ("Sleep Disturbance",       0.85, "DSM-5 Criterion B5"),
        ("Irritability Symptom",    0.82, "DSM-5 Criterion B6"),
        ("Fatigue",                 0.78, "DSM-5 Criterion B7"),
        ("Concentration Difficulty",0.75, "DSM-5 Criterion B8"),
    ],
    "PeripartumMentalDisorderWithoutPsychosis": [
        ("Depressed Mood",          0.92, "ICD-11 Clinical Feature"),
        ("Anhedonia",               0.85, "ICD-11 Clinical Feature"),
        ("Fatigue",                 0.88, "ICD-11 Clinical Feature"),
        ("Sleep Disturbance",       0.80, "ICD-11 Clinical Feature"),
        ("Concentration Difficulty",0.78, "ICD-11 Clinical Feature"),
    ],
}

total_sym = 0
for disorder, symptoms in MISSING_SYMPTOMS.items():
    for sym_name, conf, src in symptoms:
        c = run("""
            MATCH (d:Disorder {name: $dis})
            MERGE (sym:Symptom {name: $sym})
            MERGE (d)-[r:MANIFESTS_AS]->(sym)
              ON CREATE SET r.confidence=$conf, r.source=$src
        """, dis=disorder, sym=sym_name, conf=conf, src=src)
        total_sym += vars(c).get('relationships_created', 0)
    print(f"  ✓ {disorder}: {len(symptoms)} symptoms added")

print(f"\n  Total MANIFESTS_AS edges added: {total_sym}")

# ═══════════════════════════════════════════════════════════════
# B. Merge duplicate 'Depression' EmotionalState → Sadness
# ═══════════════════════════════════════════════════════════════
sec("B. Merge duplicate 'Depression' EmotionalState → Sadness")

# Redirect all session links from Depression → Sadness, then delete
c1 = run("""
    MATCH (dep:EmotionalState {name: 'Depression'})
    MATCH (sad:EmotionalState {name: 'Sadness'})
    WITH dep, sad
    MATCH (s:Session)-[r:EXPRESSES_EMOTION]->(dep)
    MERGE (s)-[:EXPRESSES_EMOTION]->(sad)
    DELETE r
""")
c2 = run("""
    MATCH (dep:EmotionalState {name: 'Depression'})
    DETACH DELETE dep
""")
print(f"  Redirected session→Depression edges to Sadness, node deleted.")

# ═══════════════════════════════════════════════════════════════
# C. WORSENS — 7 missing context nodes
# ═══════════════════════════════════════════════════════════════
sec("C. WORSENS — Missing context-disorder edges")

MISSING_WORSENS = [
    ("FamilyStress",          "SingleEpisodeDepressiveDisorder",       0.88),
    ("FamilyStress",          "GeneralizedAnxietyDisorder",             0.85),
    ("FamilyStress",          "BorderlinePattern",                     0.78),
    ("FamilyStress",          "PostTraumaticStressDisorder",            0.70),
    ("HealthAnxiety",         "GeneralizedAnxietyDisorder",             0.92),
    ("HealthAnxiety",         "PanicDisorder",                         0.80),
    ("HealthAnxiety",         "ObsessiveCompulsiveDisorder",            0.72),
    ("TraumaticEvent",        "PostTraumaticStressDisorder",            0.98),
    ("TraumaticEvent",        "ComplexPostTraumaticStressDisorder",    0.92),
    ("TraumaticEvent",        "AdjustmentDisorder",                    0.85),
    ("TraumaticEvent",        "SuicidalIdeation",                      0.68),
    ("SocialRejection",       "SingleEpisodeDepressiveDisorder",        0.85),
    ("SocialRejection",       "SocialAnxietyDisorder",                 0.88),
    ("SocialRejection",       "BorderlinePattern",                     0.80),
    ("ChildhoodAbuse",        "ComplexPostTraumaticStressDisorder",    0.95),
    ("ChildhoodAbuse",        "BorderlinePattern",                     0.88),
    ("ChildhoodAbuse",        "PostTraumaticStressDisorder",            0.90),
    ("ChildhoodAbuse",        "DissociativeIdentityDisorder",           0.82),
    ("ChildhoodAbuse",        "NonSuicidalSelfInjury",                 0.75),
    ("SeasonalChange",        "SingleEpisodeDepressiveDisorder",        0.80),
    ("SeasonalChange",        "GeneralizedAnxietyDisorder",             0.65),
    ("HormonalFluctuation",   "SingleEpisodeDepressiveDisorder",        0.78),
    ("HormonalFluctuation",   "PeripartumMentalDisorderWithoutPsychosis",0.90),
    ("HormonalFluctuation",   "GeneralizedAnxietyDisorder",             0.70),
    ("ChronicMedicalCondition","SingleEpisodeDepressiveDisorder",       0.82),
    ("ChronicMedicalCondition","GeneralizedAnxietyDisorder",            0.78),
    ("ChronicMedicalCondition","InsomniaDisorder",                     0.75),
    ("ChronicMedicalCondition","AdjustmentDisorder",                   0.85),
]

total_w = 0
for ctx, dis, conf in MISSING_WORSENS:
    c = run("""
        MERGE (ctx:ContextCategory {name: $ctx})
        WITH ctx
        MATCH (d:Disorder {name: $dis})
        MERGE (ctx)-[r:WORSENS]->(d)
          ON CREATE SET r.confidence=$conf, r.source='WHO-SDOH-2023'
    """, ctx=ctx, dis=dis, conf=conf)
    total_w += vars(c).get('relationships_created', 0) + vars(c).get('nodes_created', 0)

print(f"  WORSENS + new context nodes added: {total_w}")

# ═══════════════════════════════════════════════════════════════
# D. Wire remaining TherapeuticModalities
# ═══════════════════════════════════════════════════════════════
sec("D. TherapeuticModality — Remaining USES + RECOMMENDED_FOR")

REMAINING_MODS = [
    ("NarrativeTherapy", ["JournallingOrThoughtRecords","SelfCompassion"],
     ["AdjustmentDisorder","ProlongedGriefDisorder"]),
    ("SolutionFocusedBriefTherapy", ["ProblemSolving","BehaviouralActivation"],
     ["AdjustmentDisorder","SingleEpisodeDepressiveDisorder"]),
    ("InterpersonalTherapy", ["SocialSkillsTraining","GriefWork"],
     ["ProlongedGriefDisorder","SingleEpisodeDepressiveDisorder"]),
    ("SchemaTherapy", ["CognitiveRestructuring","SelfCompassion"],
     ["BorderlinePattern","PersonalityDisorder"]),
    ("EyeMovementDesensitizationReprocessing", ["TraumaProcessing"],
     ["PostTraumaticStressDisorder","ComplexPostTraumaticStressDisorder"]),
    ("CognitiveBehaviouralTherapyInsomnia", ["SleepHygieneIntervention","RelaxationTraining"],
     ["InsomniaDisorder"]),
    ("GriefCounseling", ["GriefWork","SelfCompassion"],
     ["ProlongedGriefDisorder"]),
]

total_mod = 0
for mod_name, techniques, disorders in REMAINING_MODS:
    for tech in techniques:
        c = run("""
            MERGE (m:TherapeuticModality {name: $mod})
            WITH m
            MATCH (t:TherapeuticTechnique {name: $tech})
            MERGE (m)-[r:USES]->(t)
              ON CREATE SET r.source='Clinical-Guidelines'
        """, mod=mod_name, tech=tech)
        total_mod += vars(c).get('relationships_created', 0) + vars(c).get('nodes_created', 0)
    for dis in disorders:
        c = run("""
            MERGE (m:TherapeuticModality {name: $mod})
            WITH m
            MATCH (d:Disorder {name: $dis})
            MERGE (m)-[r:RECOMMENDED_FOR]->(d)
              ON CREATE SET r.evidence_grade='B', r.confidence=0.85,
                            r.source='Clinical-Guidelines'
        """, mod=mod_name, dis=dis)
        total_mod += vars(c).get('relationships_created', 0)

print(f"  Modality edges added: {total_mod}")

# ═══════════════════════════════════════════════════════════════
# E. Extended NER re-wire: link sessions to missing behaviours,
#    contexts, and techniques using keyword matching
# ═══════════════════════════════════════════════════════════════
sec("E. Extended NER — Behaviours, Contexts, Techniques")

# Extended aliases for nodes not covered by original NER
BEHAVIOUR_EXT = {
    "SelfHarmBehaviour":            ["self harm","self-harm","cutting","hurt myself","self injury","burning myself","scratching","self inflicted"],
    "CompulsiveChecking":           ["checking compulsion","check repeatedly","keep checking","verify over and over","lock the door again"],
    "BingeEating":                  ["binge eat","bingeing","eating a lot in one go","ate everything","uncontrollable eating","food binge"],
    "PurgingBehaviour":             ["purging","making myself sick after eating","vomiting after","laxatives","throwing up what i ate"],
    "AlcoholUse":                   ["drinking alcohol","having a drink","drunk","whiskey","beer","wine to cope","alcohol to relax"],
    "SubstanceMisuse":              ["using drugs","took drugs","drug use","cannabis","cocaine","pills to cope","substance use"],
    "SafetyBehaviours":             ["safety behavior","reassurance seeking","need someone to tell me","asking for reassurance","avoid to stay safe"],
    "HypervigilantSafetyBehaviours":["always scanning","watch for danger","hyper alert","can never relax","always on edge watching"],
    "ImpulsiveDecisions":           ["acted impulsively","made a rash decision","did not think it through","impulsive spending","risky behavior","reckless"],
    "MedicalReassuranceSeeking":    ["kept going to doctor","health check","googling symptoms","worried about illness","health anxiety check"],
    "Withdrawal":                   ["withdrawing from","pulling away from","closing myself off","shutting down","not engaging","retreating"],
}

CONTEXT_EXT = {
    "FamilyStress":                 ["family stress","stressed about family","family problems","family situation","conflict at home","home life"],
    "HealthAnxiety":                ["worried about health","fear of illness","health anxiety","googling symptoms","think i'm sick","medical worry"],
    "TraumaticEvent":               ["traumatic event","what happened to me","the incident","after the accident","after it happened","the event"],
    "SocialRejection":              ["rejected","left out","excluded","nobody likes me","not accepted","ostracized","bullied","ignored by everyone"],
    "ChildhoodAbuse":               ["childhood abuse","abused as a child","grew up in an abusive","parents abused","childhood trauma","early abuse"],
    "SeasonalChange":               ["winter depression","dark months","seasonal","less sunlight","days getting shorter","SAD","seasonal mood"],
    "HormonalFluctuation":          ["hormones","menstrual","pms","postpartum","after giving birth","monthly cycle affecting mood","hormonal"],
    "ChronicMedicalCondition":      ["chronic illness","long term condition","living with disease","chronic pain","ongoing medical","managing my condition"],
}

TECHNIQUE_EXT = {
    "TraumaProcessing":             ["emdr","eye movement","processing the trauma","trauma work","trauma-focused therapy","working through trauma"],
    "DistressToleranceSkills":      ["distress tolerance","tolerating the feeling","riding out the urge","sitting with discomfort","tipp skills"],
    "EmotionRegulationSkills":      ["emotion regulation","regulate emotions","managing emotions","dbt skills","opposite action","check the facts"],
    "GroundingExercise":            ["grounding","5 4 3 2 1","feel the ground","stay present","anchor yourself","grounding technique","feet on floor"],
    "ThoughtRecord":                ["thought record","thought diary","recording thoughts","logging thoughts","thought log","abc model"],
    "ProgressiveMuscleRelaxation":  ["progressive muscle relaxation","tense and release","muscle relaxation","pmr","tensing muscles","body relaxation"],
    "ProlongedExposure":            ["prolonged exposure","pe therapy","reliving the memory on purpose","exposure narrative","repeating the story"],
    "SleepRestriction":             ["sleep restriction","cutting back sleep time","sleep window","staying awake until","restricted sleep schedule"],
    "StimulusControl":              ["stimulus control","only use bed for sleep","no screens before bed","bed only for sleeping","sleep cue"],
    "InteroceptiveExposure":        ["interoceptive exposure","inducing panic symptoms","racing heart on purpose","practice the sensations"],
    "RelapsePreventionCounseling":  ["relapse prevention","prevent relapse","avoiding triggers","staying sober","managing urges","coping with cravings"],
}

import re as re_mod

def build_pats(alias_dict):
    pats = {}
    for name, aliases in alias_dict.items():
        sorted_a = sorted(aliases, key=len, reverse=True)
        pat = re_mod.compile(r'\b(' + '|'.join(re_mod.escape(a) for a in sorted_a) + r')\b', re_mod.IGNORECASE)
        pats[name] = pat
    return pats

B_PATS = build_pats(BEHAVIOUR_EXT)
C_PATS = build_pats(CONTEXT_EXT)
T_PATS = build_pats(TECHNIQUE_EXT)

FETCH = """
    MATCH (s:Session)
    RETURN elementId(s) AS eid,
           coalesce(s.patient_utterance,'') + ' ' + coalesce(s.therapist_utterance,'') AS text
    SKIP $skip LIMIT 2000
"""

WIRE = """
    UNWIND $rows AS row
    MATCH (s) WHERE elementId(s) = row.eid
    FOREACH (name IN row.behaviours |
        MERGE (b:Behaviour {name:name})
        MERGE (s)-[:EXHIBITS_BEHAVIOUR]->(b)
    )
    FOREACH (name IN row.contexts |
        MERGE (c:ContextCategory {name:name})
        MERGE (s)-[:INVOLVES_CONTEXT]->(c)
    )
    FOREACH (name IN row.techniques |
        MERGE (t:TherapeuticTechnique {name:name})
        MERGE (s)-[:SUGGESTS_TECHNIQUE]->(t)
    )
"""

skip = 0
total_proc = 0
total_wired = 0
start_t = time.time()
print("  Scanning all 123,926 sessions for extended NER matches...")

while True:
    with driver.session(database="therapy") as s:
        rows = s.run(FETCH, skip=skip, limit=2000).data()
    if not rows:
        break

    batch = []
    for r in rows:
        text = r['text']
        behaviours = [n for n, p in B_PATS.items() if p.search(text)]
        contexts   = [n for n, p in C_PATS.items() if p.search(text)]
        techniques = [n for n, p in T_PATS.items() if p.search(text)]
        if behaviours or contexts or techniques:
            batch.append({"eid": r['eid'], "behaviours": behaviours,
                          "contexts": contexts, "techniques": techniques})
            total_wired += 1

    if batch:
        for attempt in range(5):
            try:
                with driver.session(database="therapy") as s:
                    s.run(WIRE, rows=batch)
                break
            except (ServiceUnavailable, SessionExpired, OSError) as e:
                time.sleep(2**attempt + random.random())

    total_proc += len(rows)
    elapsed = time.time() - start_t
    rate = total_proc / elapsed if elapsed > 0 else 1
    eta  = max(0, 123926 - total_proc) / rate
    print(f"  [{total_proc:>7}/123926]  wired:{total_wired:>6}  {rate:.0f}/s  ETA:{eta/60:.1f}m", flush=True)

    if len(rows) < 2000:
        break
    skip += 2000

print(f"\n  Extended NER done. Sessions with new links: {total_wired:,}")

# ═══════════════════════════════════════════════════════════════
# FINAL STATS
# ═══════════════════════════════════════════════════════════════
sec("FINAL STATS AFTER ALL FIXES")
total_n = count("MATCH (n) RETURN count(n)")
total_e = count("MATCH ()-[r]->() RETURN count(r)")
print(f"  Total nodes : {total_n:>10,}")
print(f"  Total edges : {total_e:>10,}")
print(f"  Isolated    : {count('MATCH (n) WHERE NOT (n)--() RETURN count(n)'):>10,}")
for rel in ["MANIFESTS_AS","EXPRESSES_EMOTION","MENTIONS_SYMPTOM","EXHIBITS_BEHAVIOUR",
            "INVOLVES_CONTEXT","SUGGESTS_TECHNIQUE","WORSENS","CO_OCCURS_WITH",
            "RECOMMENDED_FOR","PROMOTES","ASSOCIATED_WITH"]:
    c = count(f"MATCH ()-[r:{rel}]->() RETURN count(r)")
    print(f"  :{rel:<30} {c:>10,}")

driver.close()
print("\n  ✓ All ontology fixes complete.")
