"""
smart_session_rewiring.py
Phase 1-4 Smart Clinical NER + Multi-hop Session Wiring

Fixes the graph where 76% of sessions map only to GAD (fallback).
New relationship types added:
  MENTIONS_SYMPTOM, SUGGESTS_TECHNIQUE, INVOLVES_CONTEXT, EXHIBITS_BEHAVIOUR
Phase 4: ESConv emotion_hint/problem_hint + CounselChat topic overrides.
"""

import re, sys, time
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

NEO4J_URI  = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "neo4jpassword"
NEO4J_DB   = "therapy"

# ── DISORDER ALIASES ──────────────────────────────────────────────────────────
DISORDER_ALIASES = {
    "SingleEpisodeDepressiveDisorder": [
        "major depressive disorder","mdd","clinical depression","major depression",
        "depression","depressed","depressive episode","feeling depressed",
        "worthless","hopeless","no reason to live","everything feels pointless",
        "lost all interest","anhedonia","nothing brings me joy",
    ],
    "RecurrentDepressiveDisorder": [
        "recurrent depression","chronic depression episodes",
        "depression keeps coming back","multiple depressive episodes",
    ],
    "DysthymicDisorder": [
        "dysthymia","persistent depressive disorder","low mood for years",
        "always been depressed","chronically sad","constant low mood",
    ],
    "GeneralizedAnxietyDisorder": [
        "generalized anxiety disorder","gad","constant worry",
        "excessive worry","always worried","anxiety disorder",
        "uncontrollable worry","worried about everything",
    ],
    "SocialAnxietyDisorder": [
        "social anxiety disorder","social anxiety","social phobia",
        "fear of judgment","afraid of people","embarrassed in public",
        "avoid social situations","performance anxiety",
    ],
    "PostTraumaticStressDisorder": [
        "post traumatic stress disorder","ptsd","post-traumatic stress",
        "trauma","traumatic event","flashback","flashbacks",
        "nightmares about the event","replaying what happened",
        "triggered by reminders","hypervigilant",
    ],
    "ComplexPostTraumaticStressDisorder": [
        "complex ptsd","complex trauma","c-ptsd","complex post-traumatic",
        "childhood trauma","developmental trauma","repeated trauma",
    ],
    "PanicDisorder": [
        "panic disorder","panic attack","panic attacks",
        "heart racing","shortness of breath","chest tightening",
        "thought i was dying","sudden overwhelming fear","pounding heart",
    ],
    "ObsessiveCompulsiveDisorder": [
        "obsessive compulsive disorder","ocd","intrusive thoughts",
        "compulsions","obsessions","counting","contamination fear",
        "hand washing","rituals to calm",
    ],
    "BipolarTypeIDisorder": [
        "bipolar disorder","bipolar type 1","bipolar i",
        "manic episode","mania","manic phase",
        "mood swings between highs and lows","grandiose thoughts",
    ],
    "BipolarTypeIIDisorder": [
        "bipolar type 2","bipolar ii","hypomania",
        "hypomanic episode","mild mania","elevated mood then depression",
    ],
    "Schizophrenia": [
        "schizophrenia","schizophrenic","hearing voices","voices in my head",
        "seeing things","delusions","paranoid","paranoia","thought broadcasting",
    ],
    "AnorexiaNervosa": [
        "anorexia","anorexic","restricting food","extreme dieting",
        "fear of gaining weight","starving myself",
    ],
    "BulimiaNervosa": [
        "bulimia","bulimic","binge and purge","purging","vomiting after eating",
        "laxatives to lose weight",
    ],
    "BingeEatingDisorder": [
        "binge eating disorder","binge eating","uncontrollable eating",
        "eating large amounts","eating in secret",
    ],
    "InsomniaDisorder": [
        "insomnia","sleeplessness","sleep deprivation","lying awake",
        "waking up at night","no sleep","poor sleep quality",
    ],
    "AlcoholDependence": [
        "alcohol abuse","alcoholism","drinking problem","alcohol dependence",
        "drinking too much","drunk every day","alcohol addiction","sober",
        "sobriety","relapsed with alcohol",
    ],
    "CannabisDependence": [
        "weed addiction","cannabis dependence","marijuana addiction",
        "cannabis use disorder","daily weed",
    ],
    "OpioidDependence": [
        "opioid addiction","heroin addiction","opioid dependence",
        "opioid use disorder","prescription drug addiction","fentanyl",
    ],
    "AttentionDeficitHyperactivityDisorder": [
        "adhd","attention deficit","hyperactivity disorder",
        "always distracted","hyperactive","difficulty paying attention",
    ],
    "AutismSpectrumDisorder": [
        "autism","autistic","autism spectrum disorder","asd",
        "asperger","difficulty with social cues","sensory sensitivity",
    ],
    "SpecificPhobia": [
        "specific phobia","phobia","phobic","irrational fear of",
        "fear of spiders","fear of heights","fear of flying",
        "arachnophobia","claustrophobia",
    ],
    "Agoraphobia": [
        "agoraphobia","fear of open spaces","afraid to leave home","fear of crowds",
    ],
    "SeparationAnxietyDisorder": [
        "separation anxiety","fear of abandonment","terrified of being alone",
    ],
    "AdjustmentDisorder": [
        "adjustment disorder","difficulty coping with change",
        "struggling to adjust","stressed by life events",
    ],
    "SuicidalIdeation": [
        "suicidal","want to die","thinking about suicide","end my life",
        "kill myself","better off dead","suicidal thoughts","passive suicidal",
    ],
    "NonSuicidalSelfInjury": [
        "self harm","self-harm","cutting","hurting myself",
        "self-injury","burning myself","scratching until bleeding",
    ],
    "BorderlinePattern": [
        "borderline personality disorder","bpd","borderline",
        "unstable relationships","identity confusion",
        "intense emotions that shift rapidly","emptiness inside",
    ],
    "NarcissisticPersonalityDisorder": [
        "narcissistic personality disorder","narcissism","narcissist",
        "entitled","grandiose sense of self","lack of empathy",
    ],
    "GamblingDisorder": [
        "gambling disorder","gambling addiction","compulsive gambling",
        "betting","casino","gambling debt","poker addiction",
    ],
    "GamingDisorder": [
        "gaming disorder","gaming addiction","video game addiction",
        "addicted to games","playing games all day","internet gaming disorder",
    ],
    "ProlongedGriefDisorder": [
        "prolonged grief","complicated grief","grief disorder","grief that won't end",
    ],
    "PeripartumMentalDisorderWithoutPsychosis": [
        "postpartum depression","postnatal depression","baby blues",
        "depression after giving birth","struggling after having baby",
    ],
    "DissociativeIdentityDisorder": [
        "dissociative identity disorder","multiple personality","alters",
        "switching personalities","feel like i'm watching myself","depersonalization",
    ],
    "BodyDysmorphicDisorder": [
        "body dysmorphic disorder","body dysmorphia","obsessed with appearance flaw",
    ],
    "HoardingDisorder": [
        "hoarding disorder","hoarding","compulsive collecting",
    ],
}

# ── SYMPTOM ALIASES ───────────────────────────────────────────────────────────
SYMPTOM_ALIASES = {
    "Depressed Mood":           ["depressed mood","feeling down","low mood","sad all the time","persistent sadness"],
    "Anhedonia":                ["anhedonia","lost interest","nothing brings me joy","no pleasure","stopped doing things i loved"],
    "Sleep Disturbance":        ["sleeping too much","wake up at night","nightmares","early morning awakening","difficulty sleeping","disrupted sleep"],
    "Fatigue":                  ["fatigue","exhausted","tired all the time","no energy","drained","constant tiredness"],
    "Worthlessness":            ["feel worthless","no value","burden to everyone","i don't matter"],
    "Concentration Difficulty": ["difficulty focusing","mind goes blank","forgetful","brain fog"],
    "Suicidal Ideation":        ["suicidal thoughts","thinking of ending my life","better off dead"],
    "Panic Symptoms":           ["pounding heart","chest pain","shortness of breath","sweating","trembling","shaking","dizzy"],
    "Intrusive Thoughts":       ["intrusive thoughts","unwanted thoughts","thought stuck in my head","obsessive thoughts","violent thoughts"],
    "Avoidance Symptom":        ["stay away","not going","avoid people","isolating myself"],
    "Hypervigilance":           ["hypervigilant","always on guard","jumpy","startle easily","feel unsafe everywhere"],
    "Flashbacks":               ["flashback","flashbacks","reliving it","nightmares about","can't stop seeing"],
    "Dissociation":             ["feel detached","feel unreal","watching myself from outside","not present","derealization","feel like in a dream"],
    "Social Withdrawal":        ["withdrawn","pulling away","not seeing anyone","stopped going out"],
    "Mood Swings":              ["mood swings","emotions all over the place","unstable mood","rapid mood changes"],
    "Irritability Symptom":     ["snapping at everyone","easily angered","short-tempered","agitated"],
    "Loss of Appetite":         ["lost my appetite","not hungry","skipping meals","no appetite"],
    "Compulsions":              ["compulsions","rituals","repeating actions","doing it over and over"],
    "Grandiosity":              ["grandiose","feel invincible","special mission","more capable than everyone"],
    "Hallucinations":           ["hearing voices","seeing things","voices telling me","visual hallucinations"],
    "Cognitive Decline":        ["memory loss","forgetting things","disoriented","can't remember names"],
    "Physical Complaints":      ["physical pain","body aches","unexplained pain","somatic symptoms","pain with no medical cause"],
    "Eating Disturbance":       ["restricting food","purging","fear of food","obsessed with calories","hiding food","eating in secret"],
    "Substance Craving":        ["urge to use","need a drink","relapse","withdrawal symptoms"],
}

# ── EMOTION ALIASES ───────────────────────────────────────────────────────────
EMOTION_ALIASES = {
    "Anxiety":            ["anxious","anxiety","nervous","worried","worrying","on edge","fearful","dread","uneasy"],
    "Sadness":            ["sad","sadness","crying","upset","heartbroken","sorrowful","tearful","melancholy"],
    "Anger":              ["angry","anger","furious","rage","irritated","annoyed","mad","resentful"],
    "Fear":               ["afraid","frightened","terrified","terror","scared","horror"],
    "Hopelessness":       ["hopeless","hopelessness","no hope","pointless","no future","nothing to live for"],
    "Guilt":              ["guilty","guilt","ashamed","regret","blame myself","self-blame"],
    "Loneliness":         ["lonely","loneliness","no one cares","nobody understands","alone"],
    "Frustration":        ["frustrated","frustration","fed up","exasperated"],
    "Shame_Clinical":     ["shame","shameful","feel ashamed","embarrassed about myself"],
    "Worthlessness":      ["feel worthless","i'm a burden","i don't matter"],
    "Overwhelmed":        ["overwhelmed","too much","everything is too much"],
    "Stress":             ["stressed","stress","under pressure","strain"],
    "Grief":              ["grieving","bereavement","mourning","died","passed away"],
    "Confusion":          ["confused","confusion","bewildered","uncertain"],
    "Dissociation":       ["dissociated","not real","detached","unreal","foggy"],
    "Hopeful":            ["hopeful","optimistic","positive outlook","things will get better"],
    "Calm":               ["calm","at peace","serene","relaxed","grounded"],
    "Happiness":          ["happy","happiness","joyful","glad","pleased","content"],
    "Relief":             ["relief","relieved","weight lifted"],
    "Irritability":       ["irritable","irritability","snapping","short-tempered"],
    "Panic":              ["panicking","panic","racing heart"],
    "Worry":              ["worrying","constant worry"],
    "Emotional Numbness": ["numb","emotionally numb","feel nothing","empty inside","shut down emotionally"],
    "Craving":            ["craving","urge to use","need it"],
}

# ── TECHNIQUE ALIASES ─────────────────────────────────────────────────────────
TECHNIQUE_ALIASES = {
    "CognitiveRestructuring":    ["cognitive restructuring","challenging my thoughts","questioning negative thoughts","reframing thoughts","thought records","cognitive distortions","automatic thoughts","catastrophizing"],
    "ExposureTherapy":           ["exposure therapy","facing my fears","gradual exposure","confronting my fear","hierarchy of fears","systematic desensitization","flooding"],
    "MindfulnessBasedIntervention": ["mindfulness","mindful breathing","staying present","grounding techniques","body scan","mindfulness meditation","non-judgmental awareness","mbsr"],
    "BehaviouralActivation":     ["behavioral activation","behavioural activation","scheduling activities","activity scheduling","doing things i used to enjoy","pleasant events scheduling"],
    "RelaxationTraining":        ["relaxation","deep breathing","progressive muscle relaxation","breathing exercises","diaphragmatic breathing","slow breathing","box breathing"],
    "ProblemSolving":            ["problem solving","breaking it down","identify the problem","generate solutions","evaluate options","problem-solving therapy"],
    "JournallingOrThoughtRecords": ["journaling","writing down thoughts","thought diary","thought record","journalling","keeping a diary"],
    "SafetyPlanning":            ["safety plan","safety planning","crisis plan","who to call when in crisis","coping strategies for crisis"],
    "MotivationalInterviewing":  ["motivational interviewing","ambivalence about change","exploring reasons to change","change talk","readiness to change","stages of change"],
    "GriefWork":                 ["grief work","processing grief","working through loss","bereavement counseling","stages of grief","accepting loss"],
    "TraumaProcessing":          ["emdr","trauma processing","processing the trauma","trauma-focused","prolonged exposure for trauma","narrative exposure therapy"],
    "SelfCompassion":            ["self-compassion","self compassion","being kind to yourself","self-forgiveness","treating yourself with kindness","inner critic","self-criticism"],
    "SocialSkillsTraining":      ["social skills training","assertiveness training","communication skills","practice conversations","role play social situations"],
    "SleepHygieneIntervention":  ["sleep hygiene","sleep routine","bedtime routine","sleep schedule","stimulus control for sleep","cognitive behavioral therapy for insomnia","cbti"],
    "SubstanceUseCounseling":    ["relapse prevention","12 step","sobriety strategies","harm reduction","motivational enhancement","addiction counseling","substance use counseling"],
}

# ── CONTEXT ALIASES ───────────────────────────────────────────────────────────
CONTEXT_ALIASES = {
    "WorkStress":          ["work stress","job stress","workplace pressure","overworked","work-life balance","fired","layoff","job loss","toxic workplace","burnout at work"],
    "Bereavement":         ["grieving","death","died","passed away","bereavement","mourning","losing a loved one","funeral","loss of a parent","loss of child"],
    "RelationshipConflict":["relationship problems","breakup","break up","divorce","marriage problems","argument with partner","fight with partner","cheating","infidelity","trust issues in relationship","separation"],
    "FinancialStress":     ["financial stress","money problems","debt","broke","financial difficulty","losing house","poverty","eviction"],
    "AcademicPressure":    ["academic pressure","exam stress","school stress","failing class","failing exams","university pressure","college anxiety"],
    "FamilyConflict":      ["family conflict","family problems","argument with family","issues with parents","abusive family","toxic family","parent problems","sibling conflict"],
    "HealthConcerns":      ["health problems","chronic illness","medical condition","health anxiety","sick","disease","diagnosis","chronic pain","terminal illness"],
    "TraumaticExperience": ["abuse","assault","violence","accident","traumatic experience","sexual abuse","childhood abuse","domestic violence","rape","attack"],
    "SocialIsolation":     ["social isolation","no friends","no social life","cut off from people","alone all the time","no one to talk to"],
    "LifeTransition":      ["major life change","moving cities","new job","retirement","big transition","starting college","becoming a parent","empty nest"],
}

# ── BEHAVIOUR ALIASES ─────────────────────────────────────────────────────────
BEHAVIOUR_ALIASES = {
    "Avoidance":         ["avoidance","stay away","isolating myself","withdrawal","not facing it"],
    "Rumination":        ["ruminating","rumination","overthinking","dwelling on","obsessing over"],
    "SelfHarm":          ["self harm","self-harm","cutting","hurting myself","self-injury","burning myself"],
    "SubstanceUse":      ["drinking heavily","drug use","using drugs","substance use","taking pills to cope"],
    "Aggression":        ["aggressive","aggression","violent","hitting","fighting","outburst","anger outburst"],
    "SocialWithdrawal":  ["withdrawing","social withdrawal","isolating","stopped seeing people"],
    "HelpSeeking":       ["seeking help","asking for help","looking for support","reaching out"],
    "ActiveCoping":      ["coping with","managing my","dealing with","working through","trying to cope"],
    "Procrastination":   ["procrastinating","procrastination","keep putting off","delaying"],
    "ImpulsiveBehaviour":["impulsive","impulsivity","acting without thinking","reckless","risky behavior","impulsive decisions"],
    "Checking":          ["checking repeatedly","rechecking","verify multiple times"],
    "SafetyBehaviours":  ["safety behaviors","safety behaviours","reassurance seeking","always asking for reassurance","seeking confirmation"],
}

# ── METADATA MAPS ─────────────────────────────────────────────────────────────
ESCONV_EMOTION_MAP = {
    "anxiety":"Anxiety","depression":"Sadness","fear":"Fear","anger":"Anger",
    "disgust":"Disgust","sadness":"Sadness","stress":"Stress","grief":"Grief",
    "jealousy":"Anger","guilt":"Guilt","shame":"Shame_Clinical","loneliness":"Loneliness",
    "hopelessness":"Hopelessness","frustration":"Frustration","nervousness":"Anxiety",
    "embarrassment":"Shame_Clinical","joy":"Happiness","happiness":"Happiness","neutral":"Neutral",
}

ESCONV_PROBLEM_MAP = {
    "depression":"SingleEpisodeDepressiveDisorder",
    "anxiety":"GeneralizedAnxietyDisorder",
    "relationship issues":"AdjustmentDisorder","relationship_issues":"AdjustmentDisorder",
    "work/study stress":"AdjustmentDisorder","work_study_stress":"AdjustmentDisorder",
    "family issues":"AdjustmentDisorder","family_issues":"AdjustmentDisorder",
    "grief":"ProlongedGriefDisorder",
    "academic pressure":"AdjustmentDisorder","academic_pressure":"AdjustmentDisorder",
    "health issues":"AdjustmentDisorder","health_issues":"AdjustmentDisorder",
    "trauma":"PostTraumaticStressDisorder",
    "substance use":"AlcoholDependence","substance_use":"AlcoholDependence",
    "other":"GeneralizedAnxietyDisorder",
}

COUNSELCHAT_TOPIC_MAP = {
    "depression":"SingleEpisodeDepressiveDisorder",
    "anxiety":"GeneralizedAnxietyDisorder","stress":"AdjustmentDisorder",
    "trauma":"PostTraumaticStressDisorder","ptsd":"PostTraumaticStressDisorder",
    "relationships":"AdjustmentDisorder","relationship-dissolution":"AdjustmentDisorder",
    "grief-and-loss":"ProlongedGriefDisorder",
    "self-esteem":"SingleEpisodeDepressiveDisorder",
    "anger-management":"IntermittentExplosiveDisorder",
    "family-conflict":"AdjustmentDisorder",
    "social-relationships":"SocialAnxietyDisorder",
    "addiction":"AlcoholDependence","behavioral-change":"AdjustmentDisorder",
    "parenting":"AdjustmentDisorder","marital-issues":"AdjustmentDisorder",
    "work":"AdjustmentDisorder","spirituality":"AdjustmentDisorder",
    "sleep-improvement":"InsomniaDisorder","eating-disorders":"AnorexiaNervosa",
    "adhd":"AttentionDeficitHyperactivityDisorder","autism":"AutismSpectrumDisorder",
    "schizophrenia":"Schizophrenia","bipolar":"BipolarTypeIDisorder",
    "ocd":"ObsessiveCompulsiveDisorder","sexual-issues":"AdjustmentDisorder",
    "intrusivethoughts":"ObsessiveCompulsiveDisorder",
    "counseling-fundamentals":"GeneralizedAnxietyDisorder",
    "lgbtq+":"AdjustmentDisorder",
}

# ── BUILD PATTERNS ────────────────────────────────────────────────────────────
def build_patterns(alias_dict):
    patterns = {}
    for node_name, aliases in alias_dict.items():
        sorted_aliases = sorted(aliases, key=len, reverse=True)
        pattern = re.compile(
            r'\b(' + '|'.join(re.escape(a) for a in sorted_aliases) + r')\b',
            re.IGNORECASE
        )
        patterns[node_name] = pattern
    return patterns

DISORDER_PATS  = build_patterns(DISORDER_ALIASES)
SYMPTOM_PATS   = build_patterns(SYMPTOM_ALIASES)
EMOTION_PATS   = build_patterns(EMOTION_ALIASES)
TECHNIQUE_PATS = build_patterns(TECHNIQUE_ALIASES)
CONTEXT_PATS   = build_patterns(CONTEXT_ALIASES)
BEHAVIOUR_PATS = build_patterns(BEHAVIOUR_ALIASES)

def extract_all(text):
    text = text or ""
    return (
        [n for n, p in DISORDER_PATS.items()  if p.search(text)],
        [n for n, p in SYMPTOM_PATS.items()   if p.search(text)],
        [n for n, p in EMOTION_PATS.items()   if p.search(text)],
        [n for n, p in TECHNIQUE_PATS.items() if p.search(text)],
        [n for n, p in CONTEXT_PATS.items()   if p.search(text)],
        [n for n, p in BEHAVIOUR_PATS.items() if p.search(text)],
    )

# ── CYPHER ────────────────────────────────────────────────────────────────────
FETCH_QUERY = """
MATCH (s:Session)
RETURN elementId(s) AS eid,
       coalesce(s.patient_utterance,'') + ' ' + coalesce(s.therapist_utterance,'') AS text,
       coalesce(s.source,'') AS source,
       coalesce(s.emotion_hint,'') AS emotion_hint,
       coalesce(s.problem_hint,'') AS problem_hint,
       coalesce(s.topic,'') AS topic
SKIP $skip LIMIT $batch_size
"""

WIRE_QUERY = """
UNWIND $rows AS row
MATCH (s) WHERE elementId(s) = row.eid
FOREACH (name IN row.disorders   | MERGE (d:Disorder          {name:name}) MERGE (s)-[:INDICATES_DISORDER]->(d))
FOREACH (name IN row.symptoms    | MERGE (sym:Symptom         {name:name}) MERGE (s)-[:MENTIONS_SYMPTOM]->(sym))
FOREACH (name IN row.emotions    | MERGE (e:EmotionalState    {name:name}) MERGE (s)-[:EXPRESSES_EMOTION]->(e))
FOREACH (name IN row.techniques  | MERGE (t:TherapeuticTechnique {name:name}) MERGE (s)-[:SUGGESTS_TECHNIQUE]->(t))
FOREACH (name IN row.contexts    | MERGE (c:ContextCategory   {name:name}) MERGE (s)-[:INVOLVES_CONTEXT]->(c))
FOREACH (name IN row.behaviours  | MERGE (b:Behaviour         {name:name}) MERGE (s)-[:EXHIBITS_BEHAVIOUR]->(b))
"""

# ── MAIN ──────────────────────────────────────────────────────────────────────
def run():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    BATCH_SIZE = 300
    skip = 0
    total_processed = 0
    total_wired = 0
    start = time.time()
    stats = {"disorders":0,"symptoms":0,"emotions":0,"techniques":0,"contexts":0,"behaviours":0,"metadata_overrides":0}

    print("=" * 70)
    print("  SMART SESSION REWIRING -- 5-Level Clinical NER Pipeline")
    print("=" * 70)
    print(f"  Batch size: {BATCH_SIZE}\n")

    while True:
        with driver.session(database=NEO4J_DB) as sess:
            rows = sess.run(FETCH_QUERY, skip=skip, batch_size=BATCH_SIZE).data()
        if not rows:
            print(f"\nAll sessions processed. Total: {total_processed}")
            break

        batch = []
        for row in rows:
            text   = row["text"]
            src    = row["source"]
            ehint  = (row["emotion_hint"] or "").strip().lower()
            phint  = (row["problem_hint"] or "").strip().lower()
            topic  = (row["topic"] or "").strip().lower()

            disorders, symptoms, emotions, techniques, contexts, behaviours = extract_all(text)

            # ESConv metadata overrides
            if src == "ESConv":
                if ehint in ESCONV_EMOTION_MAP:
                    m = ESCONV_EMOTION_MAP[ehint]
                    if m not in emotions: emotions.append(m); stats["metadata_overrides"] += 1
                if phint in ESCONV_PROBLEM_MAP and not disorders:
                    disorders.append(ESCONV_PROBLEM_MAP[phint]); stats["metadata_overrides"] += 1

            # CounselChat topic overrides
            if src == "CounselChat" and topic:
                for key, dname in COUNSELCHAT_TOPIC_MAP.items():
                    if key.strip() == topic.strip():
                        if not disorders or disorders == ["GeneralizedAnxietyDisorder"]:
                            disorders = [dname]; stats["metadata_overrides"] += 1
                        break

            if disorders or symptoms or emotions or techniques or contexts or behaviours:
                batch.append({"eid":row["eid"],"disorders":disorders,"symptoms":symptoms,
                              "emotions":emotions,"techniques":techniques,"contexts":contexts,"behaviours":behaviours})
                total_wired += 1
                stats["disorders"] += len(disorders); stats["symptoms"] += len(symptoms)
                stats["emotions"]  += len(emotions);  stats["techniques"] += len(techniques)
                stats["contexts"]  += len(contexts);  stats["behaviours"] += len(behaviours)

        if batch:
            with driver.session(database=NEO4J_DB) as sess:
                sess.run(WIRE_QUERY, rows=batch)

        total_processed += len(rows)
        elapsed = time.time() - start
        rate = total_processed / elapsed if elapsed > 0 else 0
        eta  = max(0, 123926 - total_processed) / rate if rate > 0 else 0
        print(f"  [{total_processed:>7}/~123926] wired:{total_wired:>7} batch:{len(batch):>4}/{len(rows):>4} {rate:.0f}/s ETA:{eta/60:.1f}m", flush=True)

        if len(rows) < BATCH_SIZE:
            break
        skip += BATCH_SIZE

    driver.close()
    elapsed = time.time() - start
    print(f"\n{'='*70}")
    print(f"  REWIRING COMPLETE in {elapsed/60:.1f} minutes")
    print(f"  Sessions processed : {total_processed:>8}")
    print(f"  Sessions wired     : {total_wired:>8}")
    print(f"  Metadata overrides : {stats['metadata_overrides']:>8}")
    print(f"  Disorder links     : {stats['disorders']:>8}")
    print(f"  Symptom links      : {stats['symptoms']:>8}")
    print(f"  Emotion links      : {stats['emotions']:>8}")
    print(f"  Technique links    : {stats['techniques']:>8}")
    print(f"  Context links      : {stats['contexts']:>8}")
    print(f"  Behaviour links    : {stats['behaviours']:>8}")

def verify():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    print(f"\n{'='*70}\n  POST-WIRING VERIFICATION\n{'='*70}")
    with driver.session(database=NEO4J_DB) as s:
        for label, q in [
            ("Total Nodes",    "MATCH (n) RETURN count(n) AS c"),
            ("Total Edges",    "MATCH ()-[r]->() RETURN count(r) AS c"),
            ("Sessions",       "MATCH (s:Session) RETURN count(s) AS c"),
            ("Isolated Nodes", "MATCH (n) WHERE NOT (n)--() RETURN count(n) AS c"),
        ]:
            print(f"  {label:<20}: {s.run(q).single()['c']:>10}")
        print()
        for rel in ["INDICATES_DISORDER","MENTIONS_SYMPTOM","EXPRESSES_EMOTION",
                    "SUGGESTS_TECHNIQUE","INVOLVES_CONTEXT","EXHIBITS_BEHAVIOUR"]:
            cnt = s.run(f"MATCH (x)-[r:{rel}]->() RETURN count(r) AS c").single()["c"]
            uniq = s.run(f"MATCH (x:Session)-[r:{rel}]->() RETURN count(DISTINCT x) AS c").single()["c"]
            print(f"  :{rel:<28} total:{cnt:>9}  sessions:{uniq:>9}")
        print()
        dis_cnt  = s.run("MATCH (d:Disorder) RETURN count(d) AS c").single()["c"]
        dis_with = s.run("MATCH (d:Disorder)<-[:INDICATES_DISORDER]-(:Session) RETURN count(DISTINCT d) AS c").single()["c"]
        print(f"  Disorders with sessions: {dis_with} / {dis_cnt}")
        print("\n  Top 15 disorders by session count:")
        rows = s.run("""
            MATCH (d:Disorder)<-[:INDICATES_DISORDER]-(s:Session)
            RETURN d.name AS disorder, count(s) AS cnt ORDER BY cnt DESC LIMIT 15
        """).data()
        for r in rows:
            print(f"    {r['disorder']:<45} : {r['cnt']:>8}")
    driver.close()

if __name__ == "__main__":
    run()
    verify()
