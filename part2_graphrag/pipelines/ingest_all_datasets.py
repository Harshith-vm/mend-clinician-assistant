"""
Layer 6 — Comprehensive Session Ingestion (All Datasets)
=========================================================
Handles actual on-disk file formats for all 7 datasets.
Run this to fully populate the therapy database with sessions.
"""
import json, os, sys, re
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

NEO4J_URI  = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "neo4jpassword"
NEO4J_DB   = "therapy"

BASE = r"d:\Psyco Therapy\finalmlkg\Layer6_Session_Instances\datasets"

# ── Clinical keyword maps ─────────────────────────────────────────────────────
EMOTION_KEYWORDS = {
    "sadness": "Sadness", "sad": "Sadness", "depressed": "Depression",
    "grief": "Grief", "hopeless": "Hopelessness", "anxiety": "Anxiety",
    "anxious": "Anxiety", "fear": "Fear", "afraid": "Fear",
    "anger": "Anger", "angry": "Anger", "shame": "Shame",
    "guilt": "Guilt", "worthless": "Worthlessness", "lonely": "Loneliness",
    "panic": "Panic", "worry": "Worry", "stress": "Stress",
    "numb": "Emotional Numbness", "irritable": "Irritability",
    "frustrat": "Frustration", "empty": "Emptiness",
    "hopeful": "Optimism", "joy": "Joy", "happy": "Joy",
    "disgust": "Disgust", "nervous": "Nervousness",
}

DISORDER_KEYWORDS = {
    "depress": "SingleEpisodeDepressiveDisorder",
    "anxiety disorder": "GeneralizedAnxietyDisorder",
    "generalized anxiety": "GeneralizedAnxietyDisorder",
    "ptsd": "PostTraumaticStressDisorder",
    "trauma": "PostTraumaticStressDisorder",
    "post-traumatic": "PostTraumaticStressDisorder",
    "bipolar": "BipolarTypeIDisorder",
    "ocd": "ObsessiveCompulsiveDisorder",
    "obsess": "ObsessiveCompulsiveDisorder",
    "schizo": "Schizophrenia",
    "borderline": "PersonalityDisorder",
    "bpd": "PersonalityDisorder",
    "substance": "AlcoholDependence",
    "addict": "AlcoholDependence",
    "eating disorder": "AnorexiaNervosa",
    "anorex": "AnorexiaNervosa",
    "bulimi": "BulimiaNervosa",
    "binge eat": "BingeEatingDisorder",
    "social anxiety": "SocialAnxietyDisorder",
    "adhd": "AttentionDeficitHyperactivityDisorder",
    "autism": "AutismSpectrumDisorder",
    "insomnia": "InsomniaDisorder",
    "panic disorder": "PanicDisorder",
    "phobia": "SpecificPhobia",
    "agoraphobia": "Agoraphobia",
    "postpartum": "PeripartumMentalDisorderWithoutPsychosis",
    "adjustment": "AdjustmentDisorder",
    "suicid": "SuicidalIdeation",
    "self-harm": "NonSuicidalSelfInjury",
    "alcohol": "AlcoholDependence",
    "drug": "OpioidUseDisorder",
}

PATTERN_KEYWORDS = {
    "catastroph": "Catastrophizing",
    "black and white": "All-or-Nothing Thinking",
    "all or nothing": "All-or-Nothing Thinking",
    "mind reading": "Mind Reading",
    "fortune tell": "Fortune Telling",
    "personali": "Personalization",
    "magnif": "Magnification",
    "should": "Should Statements",
    "emotional reasoning": "Emotional Reasoning",
    "mental filter": "Mental Filtering",
    "negative self": "NegativeSelfTalk",
}

def extract_links(text):
    t = text.lower()
    emotions  = list({v for k, v in EMOTION_KEYWORDS.items() if k in t})
    disorders = list({v for k, v in DISORDER_KEYWORDS.items() if k in t})
    patterns  = list({v for k, v in PATTERN_KEYWORDS.items() if k in t})
    return emotions, disorders, patterns

def read_json_array(path):
    """Smart reader: handles JSON arrays, single JSON objects, and JSONL files."""
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if not content:
        return []
    # Try JSON array first
    if content.startswith('['):
        try:
            return json.loads(content)
        except Exception:
            pass
    # Try single JSON object
    if content.startswith('{'):
        # Might be JSONL (multiple objects)
        records = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                continue
        if records:
            return records
        # Single object wrapped in a list
        try:
            return [json.loads(content)]
        except Exception:
            return []
    return []

def read_jsonl(path):
    """Read JSONL file (one JSON object per line)."""
    if not os.path.exists(path): return []
    out = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out

# ── Dataset loaders ──────────────────────────────────────────────────────────

def get_sessions_counselchat():
    """CounselChat: JSON array with questionText / answerText fields."""
    recs = read_json_array(os.path.join(BASE, "counsel_chat", "train.json"))
    out = []
    for r in recs:
        q = str(r.get("questionText", ""))
        a = str(r.get("answerText", ""))
        if not q.strip(): continue
        out.append({"session_id": f"counselchat_{r.get('questionID', len(out))}",
                    "patient": q[:2000], "therapist": a[:2000],
                    "source": "CounselChat", "tier": 1})
    return out

def get_sessions_esconv():
    """ESConv: JSONL where each line = {"text": "<doubly-encoded json>"}.
       Inner JSON has 'dialog' list with 'speaker' (usr/sys) and 'text' fields."""
    path = os.path.join(BASE, "esconv", "train.json")
    if not os.path.exists(path): return []
    out = []
    with open(path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line: continue
            try:
                outer = json.loads(line)
                inner_str = outer.get("text", "")
                inner = json.loads(inner_str) if isinstance(inner_str, str) else inner_str
                dlg = inner.get("dialog", [])
                # ESConv uses 'speaker' (usr/sys) and 'text'
                patient   = " ".join(u.get("text", u.get("content",""))
                                     for u in dlg if u.get("speaker", u.get("role","")) == "usr")
                therapist = " ".join(u.get("text", u.get("content",""))
                                     for u in dlg if u.get("speaker", u.get("role","")) == "sys")
                # Also capture the situation context
                situation = inner.get("situation", "")
                emotion   = inner.get("emotion_type", "")
                problem   = inner.get("problem_type", "")
                if situation:
                    patient = situation + " " + patient
                if not (patient + therapist).strip(): continue
                out.append({"session_id": f"esconv_{idx}",
                            "patient": patient[:2000], "therapist": therapist[:2000],
                            "source": "ESConv", "tier": 1})
            except Exception:
                continue
    return out

def get_sessions_mental_health():
    """Mental Health Counseling Conversations: JSON array with Context/Response."""
    recs = read_json_array(os.path.join(BASE, "mental_health_counseling_conversations", "train.json"))
    out = []
    for i, r in enumerate(recs):
        q = str(r.get("Context", r.get("context", "")))
        a = str(r.get("Response", r.get("response", "")))
        if not q.strip(): continue
        out.append({"session_id": f"mhcc_{i}",
                    "patient": q[:2000], "therapist": a[:2000],
                    "source": "MentalHealthCounselingConversations", "tier": 1})
    return out

def get_sessions_annomi():
    """AnnoMI: JSON with 'conversations' list of {from: 'gpt'/'human', value: text}."""
    recs = read_json_array(os.path.join(BASE, "annomi", "train.json"))
    out = []
    for i, r in enumerate(recs):
        convs = r.get("conversations", [])
        patient   = " ".join(c.get("value","") for c in convs
                             if c.get("from","").lower() in ["human","client","patient"])
        therapist = " ".join(c.get("value","") for c in convs
                             if c.get("from","").lower() in ["gpt","therapist","counselor","assistant"])
        if not (patient + therapist).strip():
            # Alternate turns fallback
            patient   = " ".join(c.get("value","") for j,c in enumerate(convs) if j % 2 == 1)
            therapist = " ".join(c.get("value","") for j,c in enumerate(convs) if j % 2 == 0)
        if not (patient + therapist).strip(): continue
        out.append({"session_id": f"annomi_{i}",
                    "patient": patient[:2000], "therapist": therapist[:2000],
                    "source": "AnnoMI", "tier": 1})
    return out

def get_sessions_empathetic():
    """EmpatheticDialogues: JSON array with conv_id/situation/emotion/conversations fields.
       'conversations' is a list of {from/value} or {content} dicts."""
    out = []
    for split in ["train.json", "validation.json", "test.json"]:
        recs = read_json_array(os.path.join(BASE, "empathetic_dialogues", split))
        for i, r in enumerate(recs):
            convs = r.get("conversations", [])
            situation = str(r.get("situation", ""))
            if convs:
                # Alternate turns: user starts (index 0), assistant (index 1)
                patient   = " ".join(str(c.get("value", c.get("content","")))
                                     for j,c in enumerate(convs) if j % 2 == 0)
                therapist = " ".join(str(c.get("value", c.get("content","")))
                                     for j,c in enumerate(convs) if j % 2 == 1)
                if not patient.strip():
                    patient = situation
            else:
                patient   = situation + " " + str(r.get("context",""))
                therapist = str(r.get("utterance", r.get("response", "")))
            combined = (patient + therapist).strip()
            if not combined: continue
            out.append({"session_id": f"empathetic_{split.replace('.json','')}_{i}",
                        "patient": patient[:2000], "therapist": therapist[:2000],
                        "source": "EmpatheticDialogues_ACL2019", "tier": 2})
    return out

def get_sessions_extes():
    """ExTES: JSON array where each record has 'example' field in [INST]...[/INST] format."""
    out = []
    for split in ["train.json", "test.json"]:
        recs = read_json_array(os.path.join(BASE, "extes", split))
        for i, r in enumerate(recs):
            example = str(r.get("example", ""))
            patient_part   = ""
            therapist_part = ""
            if "[/INST]" in example:
                parts = example.split("[/INST]", 1)
                # Strip [INST] tags and system prompt to get user message
                inst_block = parts[0]
                inst_match = re.search(r'\[INST\](.*)', inst_block, re.DOTALL)
                if inst_match:
                    patient_part = inst_match.group(1).strip()
                    # Remove system prompt if present (before actual user message)
                    if "<<SYS>>" in patient_part:
                        patient_part = re.sub(r'<<SYS>>.*?<</SYS>>', '', patient_part, flags=re.DOTALL).strip()
                therapist_part = parts[1].strip() if len(parts) > 1 else ""
            if not (patient_part + therapist_part).strip():
                # Fallback keys
                patient_part   = str(r.get("context", r.get("input", "")))
                therapist_part = str(r.get("response", r.get("output", "")))
            if not (patient_part + therapist_part).strip(): continue
            out.append({"session_id": f"extes_{split.replace('.json','')}_{i}",
                        "patient": patient_part[:2000], "therapist": therapist_part[:2000],
                        "source": "ExTES_ACL2023", "tier": 2})
    return out

def get_sessions_epitome():
    """EPITOME: JSON array with 'Context' seeker post and 'Response' counselor post."""
    recs = read_json_array(os.path.join(BASE, "epitome", "train.json"))
    out = []
    for i, r in enumerate(recs):
        q = str(r.get("Context", r.get("seeker_post", r.get("input", r.get("question", "")))))
        a = str(r.get("Response", r.get("response_post", r.get("output", r.get("answer", "")))))
        if not q.strip(): continue
        out.append({"session_id": f"epitome_{i}",
                    "patient": q[:2000], "therapist": a[:2000],
                    "source": "EPITOME_PHR_Counselor", "tier": 2})
    return out

# ── Cypher INSERT ─────────────────────────────────────────────────────────────
INSERT_QUERY = """
UNWIND $batch AS row
MERGE (s:Session {session_id: row.session_id})
ON CREATE SET
    s.patient_utterance   = row.patient,
    s.therapist_utterance = row.therapist,
    s.source              = row.source,
    s.tier                = row.tier,
    s.clinical_grade      = CASE row.tier WHEN 1 THEN 'Gold Standard' ELSE 'Peer Reviewed' END,
    s.date_added          = date()
WITH s, row
UNWIND row.emotions AS emo
  MATCH (e:EmotionalState) WHERE toLower(e.name) = toLower(emo)
  MERGE (s)-[:EXPRESSES_EMOTION]->(e)
WITH s, row
UNWIND row.disorders AS dis
  MATCH (d:Disorder) WHERE toLower(d.name) = toLower(dis)
  MERGE (s)-[:INDICATES_DISORDER]->(d)
WITH s, row
UNWIND row.patterns AS pat
  MATCH (cp:CognitivePattern) WHERE toLower(cp.name) = toLower(pat)
  MERGE (s)-[:SHOWS_PATTERN]->(cp)
"""

def ingest(driver, name, sessions):
    if not sessions:
        print(f"  ⚠️  {name}: 0 records parsed")
        return 0
    print(f"\n► {name}: {len(sessions)} sessions")
    batch = []
    for s in sessions:
        combined = s["patient"] + " " + s["therapist"]
        emotions, disorders, patterns = extract_links(combined)
        batch.append({**s, "emotions": emotions, "disorders": disorders, "patterns": patterns})

    with driver.session(database=NEO4J_DB) as sess:
        for i in range(0, len(batch), 300):
            sess.run(INSERT_QUERY, batch=batch[i:i+300])
            print(f"    {min(i+300, len(batch))}/{len(batch)}")
    print(f"  ✅ {name} done")
    return len(batch)

if __name__ == "__main__":
    print("=" * 60)
    print("  Layer 6 — Full Session Ingestion")
    print("=" * 60)
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    sources = [
        ("CounselChat [Tier 1]",         get_sessions_counselchat),
        ("ESConv [Tier 1]",              get_sessions_esconv),
        ("Mental Health Conv [Tier 1]",  get_sessions_mental_health),
        ("AnnoMI [Tier 1]",              get_sessions_annomi),
        ("EmpatheticDialogues [Tier 2]", get_sessions_empathetic),
        ("ExTES [Tier 2]",               get_sessions_extes),
        ("EPITOME/PHR [Tier 2]",         get_sessions_epitome),
    ]

    grand_total = 0
    for name, fn in sources:
        try:
            sessions = fn()
            grand_total += ingest(driver, name, sessions)
        except Exception as e:
            print(f"  ✗ {name} failed: {e}")

    print(f"\n{'='*60}")
    print(f"  Grand total ingested: {grand_total}")
    with driver.session(database=NEO4J_DB) as sess:
        n = sess.run("MATCH (s:Session) RETURN count(s) as c").single()['c']
        r = sess.run("MATCH (s:Session)-[rel]->() RETURN count(rel) as c").single()['c']
        total_n = sess.run("MATCH (n) RETURN count(n) as c").single()['c']
        total_r = sess.run("MATCH ()-[r]->() RETURN count(r) as c").single()['c']
        isolated = sess.run("MATCH (n) WHERE NOT (n)--() RETURN count(n) as c").single()['c']
        print(f"  Sessions in DB:    {n}")
        print(f"  Session links:     {r}")
        print(f"  Total nodes:       {total_n}")
        print(f"  Total edges:       {total_r}")
        print(f"  Isolated nodes:    {isolated}")
    print(f"{'='*60}")
    driver.close()
