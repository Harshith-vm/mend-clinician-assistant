"""
semantic_disorder_classifier.py
================================
Uses sentence-transformers to semantically classify the ~81,500 GAD-only
sessions that have no explicit disorder keyword matches.

Approach:
  1. Build "disorder anchor embeddings" — one rich text description per
     disorder combining name + symptoms + typical patient language.
  2. Embed all 81k GAD-only sessions (patient_utterance text) in batches.
  3. Cosine-similarity each session against all disorder anchors.
  4. If best match > threshold (0.35), add INDICATES_DISORDER edge to that
     disorder AND add MENTIONS_SYMPTOM edges for matched symptoms.
  5. Sessions below threshold stay with GAD (genuinely ambiguous/generic).

Also stores s.embedding on every session for future semantic search
(Neo4j vector index already defined by add_vector_embeddings.py).

Runtime: ~20-35 min for 81k sessions on CPU (MiniLM is fast).
"""

import sys, time, random
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, SessionExpired
from sentence_transformers import SentenceTransformer

NEO4J_URI  = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "neo4jpassword"
NEO4J_DB   = "therapy"

def make_driver():
    """Create a Neo4j driver with keep-alive and short connection lifetime
    to avoid the 80-minute connection reset issue."""
    return GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASS),
        max_connection_lifetime=300,   # recycle connections every 5 min
        keep_alive=True,
        connection_acquisition_timeout=60,
    )

def run_with_retry(driver_ref, database, query, params=None, max_retries=5):
    """Run a Cypher query, reconnecting and retrying on connection errors."""
    for attempt in range(max_retries):
        try:
            with driver_ref[0].session(database=database) as sess:
                result = sess.run(query, **(params or {})).data()
                return result
        except (ServiceUnavailable, SessionExpired, ConnectionResetError, OSError) as e:
            wait = 2 ** attempt + random.uniform(0, 1)
            print(f"  [retry {attempt+1}/{max_retries}] Neo4j error: {e}. Reconnecting in {wait:.1f}s...", flush=True)
            time.sleep(wait)
            try:
                driver_ref[0].close()
            except Exception:
                pass
            driver_ref[0] = make_driver()
    raise RuntimeError(f"Neo4j query failed after {max_retries} retries.")

def write_with_retry(driver_ref, database, query, rows, max_retries=5):
    """Write a batch to Neo4j, reconnecting and retrying on connection errors."""
    for attempt in range(max_retries):
        try:
            with driver_ref[0].session(database=database) as sess:
                sess.run(query, rows=rows)
                return
        except (ServiceUnavailable, SessionExpired, ConnectionResetError, OSError) as e:
            wait = 2 ** attempt + random.uniform(0, 1)
            print(f"  [retry {attempt+1}/{max_retries}] Write error: {e}. Reconnecting in {wait:.1f}s...", flush=True)
            time.sleep(wait)
            try:
                driver_ref[0].close()
            except Exception:
                pass
            driver_ref[0] = make_driver()
    raise RuntimeError(f"Neo4j write failed after {max_retries} retries.")

# ── Similarity threshold ──────────────────────────────────────────────────────
# Tuned conservatively: only reclassify when there's strong signal
THRESHOLD = 0.32

# ── Disorder anchor texts ─────────────────────────────────────────────────────
# Each anchor is a rich narrative that captures what a patient with this
# disorder typically says in a therapy session. More natural = better match.

DISORDER_ANCHORS = {
    "SingleEpisodeDepressiveDisorder": """
        I feel completely empty and numb. I have no motivation or energy to do anything.
        Everything feels pointless. I hate myself. I feel worthless. I cannot get out of bed.
        I have no interest in things I used to love. I cannot feel happiness or joy.
        I feel like a burden to everyone around me. I cry all the time.
        I feel hopeless about the future. Nothing matters anymore.
        I am so tired all the time. I feel like giving up.
        I cannot sleep or I sleep too much. I have lost my appetite.
        I feel like I'm failing at everything. I have low self-esteem.
        People would be better off without me. I feel invisible and alone.
    """,
    "GeneralizedAnxietyDisorder": """
        I worry constantly about everything. I cannot stop the anxious thoughts.
        I feel on edge all the time. My mind races with what-ifs.
        I am always tense and nervous. I cannot relax.
        I worry about my health, my family, money, work — everything.
        I feel restless and irritable. I cannot concentrate because of worry.
        The anxiety is always there in the background.
        I feel overwhelmed by everyday decisions. I overthink everything.
    """,
    "PostTraumaticStressDisorder": """
        I keep reliving what happened. The memories come back suddenly.
        I have nightmares about the trauma. I cannot stop thinking about it.
        I feel triggered by things that remind me of what happened.
        I feel numb and detached. I cannot trust anyone anymore.
        I am always on guard, hypervigilant. I startle easily.
        I avoid places and people that remind me of the event.
        I feel shame and guilt about what happened.
        I experienced abuse, assault, violence, or a traumatic accident.
    """,
    "SocialAnxietyDisorder": """
        I am terrified of being judged by other people. I hate being in social situations.
        I blush and shake when I have to talk to people. I avoid parties and gatherings.
        I am afraid of saying something embarrassing. I feel like everyone is watching me.
        I cannot make eye contact. I avoid phone calls and presentations.
        I feel sick before social events. I prefer to be alone rather than judged.
        I feel extremely self-conscious around people.
    """,
    "PanicDisorder": """
        I had a panic attack and thought I was dying. My heart was pounding so fast.
        I could not breathe. I felt dizzy and my hands went numb.
        I am terrified of having another panic attack. I avoid places where I had one.
        The panic comes on suddenly without warning. I feel like I am losing control.
        My chest tightens up and I start sweating. I feel like I am going crazy.
    """,
    "ObsessiveCompulsiveDisorder": """
        I cannot stop the intrusive thoughts. I have unwanted thoughts that disturb me.
        I have to check things over and over or something bad will happen.
        I count, repeat rituals to feel safe. I am obsessed with contamination and germs.
        I wash my hands constantly. The thoughts are not me but I cannot turn them off.
        I feel compelled to do certain things to reduce anxiety.
        I have violent or sexual thoughts that horrify me but I cannot stop them.
    """,
    "BipolarTypeIDisorder": """
        Sometimes I feel on top of the world, invincible, like I need no sleep.
        I spend a lot of money impulsively. I have racing thoughts and talk very fast.
        Then I crash into a deep depression. My mood swings between extreme highs and lows.
        During my high periods I take big risks and feel grandiose.
        My relationships suffer because of my mood swings.
        I have been hospitalized during a manic episode.
    """,
    "BorderlinePattern": """
        My emotions shift so rapidly and intensely. I am terrified of being abandoned.
        My relationships are unstable — I idealize and then hate people.
        I do not know who I am. I feel empty inside.
        I hurt myself when I am overwhelmed. I act impulsively.
        I go from loving someone to hating them very quickly.
        I feel intense rage that I cannot control. I feel hollow and purposeless.
    """,
    "AlcoholDependence": """
        I drink too much and I cannot stop. I need alcohol to get through the day.
        I drink to cope with stress or emotions. I have tried to quit but cannot.
        My drinking is affecting my relationships and work.
        I feel sick when I do not drink. I wake up and need a drink.
        My family is concerned about how much I drink.
        I have blacked out from drinking. I drink alone and in secret.
    """,
    "SuicidalIdeation": """
        I have been thinking about ending my life. I do not want to be here anymore.
        I have thought about how I would do it. I feel like everyone would be better off without me.
        I feel like there is no point in living. I have passive thoughts of death.
        I want to disappear. I have made a plan to hurt myself.
        I feel so hopeless that death seems like the only escape.
        I am scared of my own thoughts about suicide.
    """,
    "NonSuicidalSelfInjury": """
        I cut myself when I feel overwhelmed. Self-harm helps me cope with emotional pain.
        I hurt myself to feel something or to stop feeling too much.
        I burn or scratch myself. I hide the marks from people.
        I feel relieved after hurting myself but then ashamed.
        I have been self-harming for a long time. I do not want to die but I hurt myself.
    """,
    "EatingDisorder": """
        I restrict what I eat because I am afraid of gaining weight.
        I binge eat and then feel disgusted with myself.
        I purge after eating. I count every calorie obsessively.
        I see myself as fat even when others say I am not.
        My relationship with food is completely disordered.
        I feel out of control around food. I exercise obsessively to burn calories.
    """,
    "InsomniaDisorder": """
        I cannot sleep no matter what I do. I lie awake for hours.
        I wake up in the middle of the night and cannot go back to sleep.
        I am exhausted but my mind will not stop. I dread going to bed.
        I have not slept properly in weeks. My sleep is completely disrupted.
        I am irritable and cannot function during the day because of no sleep.
    """,
    "AttentionDeficitHyperactivityDisorder": """
        I cannot focus on anything for more than a few minutes. I am always distracted.
        I forget things constantly. I lose track of conversations.
        I act impulsively without thinking. I cannot sit still.
        I start many things and never finish them. My mind jumps from one thing to another.
        I was diagnosed with ADHD or ADD. I struggle to organize my thoughts.
    """,
    "Schizophrenia": """
        I hear voices that other people cannot hear. The voices comment on what I do.
        I believe people are following me or reading my mind.
        I have strange beliefs that others say are not real.
        I see things that are not there. My thoughts are disorganized and scattered.
        I feel like my thoughts are being broadcast to the world.
        I have been hospitalized for psychosis.
    """,
    "AdjustmentDisorder": """
        I am struggling to cope since a major life change happened.
        I went through a breakup, job loss, bereavement, or big transition.
        I was fine before this happened but now I cannot cope.
        The stress of what happened has overwhelmed my ability to function.
        I am having trouble adjusting to my new situation.
        My divorce or separation has made everything fall apart.
    """,
    "ComplexPostTraumaticStressDisorder": """
        I experienced ongoing trauma for a long time, not just one event.
        I was abused as a child. My trauma was repeated over years.
        I struggle with deep shame and feeling fundamentally broken.
        My sense of identity feels shattered. I cannot trust my own perceptions.
        I dissociate and feel like I leave my own body.
        My trauma responses affect every relationship I have.
    """,
    "ProlongedGriefDisorder": """
        I lost someone and I cannot move on. The grief is consuming everything.
        I feel like part of me died with them. I cannot accept that they are gone.
        I still feel their presence. I cannot imagine life without them.
        My grief is not getting better with time. It has been months or years.
        I feel intense longing and yearning for the person I lost.
    """,
    "DissociativeIdentityDisorder": """
        I sometimes feel like a different person. I lose time and cannot remember.
        I have different parts of myself that seem to take over.
        I find things I do not remember doing. I feel like I am watching myself.
        People tell me I acted differently and I have no memory of it.
        I feel disconnected from my own body and identity.
        I have experienced severe dissociation since childhood trauma.
    """,
}

# Symptom anchors for secondary MENTIONS_SYMPTOM links
SYMPTOM_ANCHORS = {
    "Depressed Mood":           "feeling down sad low mood persistent sadness unhappy",
    "Anhedonia":                "no interest lost pleasure cannot enjoy things stopped caring anhedonia",
    "Fatigue":                  "exhausted tired no energy drained constant tiredness",
    "Worthlessness":            "worthless feel worthless failure burden hate myself",
    "Sleep Disturbance":        "cannot sleep insomnia wake up nightmares disrupted sleep",
    "Suicidal Ideation":        "want to die suicidal thoughts end my life better off dead",
    "Panic Symptoms":           "heart racing pounding chest pain cannot breathe sweating shaking",
    "Intrusive Thoughts":       "intrusive thoughts unwanted thoughts cannot stop thinking obsessive",
    "Social Withdrawal":        "withdrawn isolating avoiding people stopped going out",
    "Hypervigilance":           "hypervigilant always on guard jumpy startle easily unsafe",
    "Flashbacks":               "flashback reliving nightmares keeps coming back trauma memory",
    "Dissociation":             "feel detached unreal watching myself not present dissociation",
    "Mood Swings":              "mood swings unstable mood rapid changes emotions all over",
    "Irritability Symptom":     "irritable snapping easily angered short tempered agitated",
    "Concentration Difficulty": "cannot concentrate difficulty focusing brain fog forgetful",
    "Loss of Appetite":         "not hungry lost appetite not eating skipping meals",
    "Eating Disturbance":       "restricting food binge purging obsessed calories eating disorder",
    "Substance Craving":        "craving urge to use need drink relapse withdrawal",
}


def cosine_sim(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def run():
    print("=" * 70)
    print("  SEMANTIC DISORDER CLASSIFIER")
    print("  Classifying ~81k GAD-only sessions using sentence embeddings")
    print("=" * 70)

    # Load model
    print("\n[1] Loading sentence-transformers model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("    Model loaded. Embedding size: 384")

    # Build disorder anchor embeddings
    print("\n[2] Building disorder anchor embeddings...")
    disorder_names = list(DISORDER_ANCHORS.keys())
    anchor_texts   = [DISORDER_ANCHORS[d] for d in disorder_names]
    anchor_embs    = model.encode(anchor_texts, batch_size=32, show_progress_bar=False)
    print(f"    {len(disorder_names)} disorder anchors embedded.")

    # Build symptom anchor embeddings
    print("\n[3] Building symptom anchor embeddings...")
    symptom_names = list(SYMPTOM_ANCHORS.keys())
    symptom_texts = [SYMPTOM_ANCHORS[s] for s in symptom_names]
    symptom_embs  = model.encode(symptom_texts, batch_size=32, show_progress_bar=False)
    print(f"    {len(symptom_names)} symptom anchors embedded.")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    # Ensure vector index exists
    with driver.session(database=NEO4J_DB) as s:
        s.run("""
            CREATE VECTOR INDEX session_embeddings IF NOT EXISTS
            FOR (s:Session) ON (s.embedding)
            OPTIONS {indexConfig: {
              `vector.dimensions`: 384,
              `vector.similarity_function`: 'cosine'
            }}
        """)
    print("\n[4] Vector index ensured.")

    # Fetch unprocessed sessions: those still missing an embedding.
    # Using s.embedding IS NULL as a natural cursor means we always SKIP 0
    # and the pool shrinks naturally as embeddings are committed.
    # This is also crash-safe: if we crash, unprocessed sessions still have
    # NULL embeddings and will be picked up on the next run.
    FETCH_QUERY = """
        MATCH (s:Session)-[:INDICATES_DISORDER]->(d:Disorder {name:'GeneralizedAnxietyDisorder'})
        WHERE s.embedding IS NULL
          AND NOT (s)-[:MENTIONS_SYMPTOM]->()
          AND NOT (s)-[:SUGGESTS_TECHNIQUE]->()
          AND NOT (s)-[:INVOLVES_CONTEXT]->()
        RETURN elementId(s) AS eid,
               coalesce(s.patient_utterance,'') + ' ' + coalesce(s.therapist_utterance,'') AS text
        LIMIT $batch_size
    """

    WIRE_QUERY = """
        UNWIND $rows AS row
        MATCH (s) WHERE elementId(s) = row.eid
        SET s.embedding = row.embedding
        FOREACH (name IN row.disorders |
            MERGE (d:Disorder {name: name})
            MERGE (s)-[:INDICATES_DISORDER]->(d)
        )
        FOREACH (name IN row.symptoms |
            MERGE (sym:Symptom {name: name})
            MERGE (s)-[:MENTIONS_SYMPTOM]->(sym)
        )
    """

    BATCH_SIZE = 400   # smaller batch = less data per write = more resilient
    total_processed = 0
    total_reclassified = 0
    total_stayed_gad = 0
    start = time.time()

    disorder_hit_counts = {d: 0 for d in disorder_names}

    # Use a mutable list so retry helpers can swap the driver on reconnect
    driver_ref = [make_driver()]

    print(f"\n[5] Processing GAD-only sessions (threshold={THRESHOLD})...")
    print(f"    Strategy: embedding IS NULL cursor — crash-safe, no skip needed\n")

    while True:
        rows = run_with_retry(
            driver_ref, NEO4J_DB,
            FETCH_QUERY, {"batch_size": BATCH_SIZE}
        )

        if not rows:
            print("\n  No more unprocessed sessions — done!")
            break

        texts = [r["text"] for r in rows]
        eids  = [r["eid"] for r in rows]

        # Encode all session texts at once (fast with MiniLM)
        session_embs = model.encode(texts, batch_size=256, show_progress_bar=False)

        batch = []
        for i, (eid, emb) in enumerate(zip(eids, session_embs)):
            emb_list = emb.tolist()

            # ── Disorder classification ───────────────────────────────────────
            sims = [cosine_sim(emb, anchor_embs[j]) for j in range(len(disorder_names))]
            best_idx  = int(np.argmax(sims))
            best_sim  = sims[best_idx]
            best_disorder = disorder_names[best_idx]

            matched_disorders = []
            if best_sim >= THRESHOLD:
                matched_disorders.append(best_disorder)
                disorder_hit_counts[best_disorder] += 1
                # Also add secondary matches above a slightly lower bar
                for j, sim in enumerate(sims):
                    if j != best_idx and sim >= THRESHOLD + 0.05:
                        matched_disorders.append(disorder_names[j])
                        disorder_hit_counts[disorder_names[j]] += 1
                total_reclassified += 1
            else:
                total_stayed_gad += 1

            # ── Symptom detection ─────────────────────────────────────────────
            matched_symptoms = []
            for k, s_emb in enumerate(symptom_embs):
                if cosine_sim(emb, s_emb) >= 0.30:
                    matched_symptoms.append(symptom_names[k])

            batch.append({
                "eid":       eid,
                "embedding": emb_list,
                "disorders": matched_disorders,
                "symptoms":  matched_symptoms,
            })

        # Write to Neo4j with retry on connection failure
        write_with_retry(driver_ref, NEO4J_DB, WIRE_QUERY, batch)

        total_processed += len(rows)
        elapsed = time.time() - start
        rate = total_processed / elapsed if elapsed > 0 else 0
        eta  = max(0, 81513 - total_processed) / rate if rate > 0 else 0
        pct  = total_reclassified / max(total_processed, 1) * 100

        print(
            f"  [{total_processed:>7}/~81513]"
            f"  reclassified: {total_reclassified:>6} ({pct:.1f}%)"
            f"  stayed GAD: {total_stayed_gad:>6}"
            f"  {rate:.0f}/s  ETA:{eta/60:.1f}m",
            flush=True
        )

        if len(rows) < BATCH_SIZE:
            break

    driver_ref[0].close()

    elapsed = time.time() - start
    print(f"\n{'=' * 70}")
    print(f"  SEMANTIC CLASSIFICATION COMPLETE in {elapsed/60:.1f} minutes")
    print(f"{'=' * 70}")
    print(f"  Sessions processed   : {total_processed:>8}")
    print(f"  Reclassified         : {total_reclassified:>8}  ({total_reclassified/max(total_processed,1)*100:.1f}%)")
    print(f"  Stayed as GAD        : {total_stayed_gad:>8}")
    print(f"\n  Reclassification breakdown:")
    for d, cnt in sorted(disorder_hit_counts.items(), key=lambda x: -x[1]):
        if cnt > 0:
            print(f"    {d:<45} : {cnt:>7}")


def verify():
    driver = make_driver()
    print(f"\n{'=' * 70}")
    print(f"  POST-SEMANTIC-CLASSIFICATION VERIFICATION")
    print(f"{'=' * 70}")
    with driver.session(database=NEO4J_DB) as s:
        total_e   = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        has_emb   = s.run("MATCH (s:Session) WHERE s.embedding IS NOT NULL RETURN count(s) AS c").single()["c"]
        dis_with  = s.run("MATCH (d:Disorder)<-[:INDICATES_DISORDER]-(:Session) RETURN count(DISTINCT d) AS c").single()["c"]
        dis_cnt   = s.run("MATCH (d:Disorder) RETURN count(d) AS c").single()["c"]
        gad_remaining = s.run("""
            MATCH (s:Session)-[:INDICATES_DISORDER]->(d:Disorder {name:'GeneralizedAnxietyDisorder'})
            WHERE NOT (s)-[:MENTIONS_SYMPTOM]->()
            RETURN count(s) AS c
        """).single()["c"]

        print(f"  Total edges          : {total_e:>10}")
        print(f"  Sessions with embedding: {has_emb:>8}")
        print(f"  Disorders with sessions: {dis_with:>8} / {dis_cnt}")
        print(f"  Truly ambiguous GAD sessions remaining: {gad_remaining:>8}")

        print("\n  Top 20 disorders by session count:")
        top = s.run("""
            MATCH (d:Disorder)<-[:INDICATES_DISORDER]-(s:Session)
            RETURN d.name AS disorder, count(s) AS cnt
            ORDER BY cnt DESC LIMIT 20
        """).data()
        for r in top:
            print(f"    {r['disorder']:<45} : {r['cnt']:>8}")

    driver.close()


if __name__ == "__main__":
    run()
    verify()
