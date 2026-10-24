"""
technique_guidance.py
=====================
Human-readable clinical framing for every TherapeuticTechnique node in the KG.

Maps KG node names → {description, therapist_framing, example_phrases}
so the response engine knows *what to say* about a technique, not just its name.

Used by graphrag_bridge.py to enrich the GraphRAGResponse before sending it
back to the conversational AI layer.
"""

__all__ = ["get_guidance", "TECHNIQUE_GUIDANCE"]

TECHNIQUE_GUIDANCE: dict[str, dict] = {

    "CognitiveRestructuring": {
        "description": "Identifying and challenging unhelpful thought patterns.",
        "therapist_framing": (
            "It sounds like your thoughts may be working against you right now. "
            "Can we look at the thought '{core_thought}' together — what's the evidence for it, "
            "and what's the evidence against it?"
        ),
        "example_phrases": [
            "What would you say to a close friend who had that exact thought?",
            "Is there another way to look at this situation?",
            "How much do you believe that thought right now, on a scale of 0–100?",
        ],
    },

    "BehaviouralActivation": {
        "description": "Scheduling small, meaningful activities to combat withdrawal and low mood.",
        "therapist_framing": (
            "When we feel low, we tend to do less — and doing less makes us feel lower. "
            "What is one small activity, even just 10 minutes, that used to bring you a little pleasure?"
        ),
        "example_phrases": [
            "What's the smallest version of that activity you could try today?",
            "Even a short walk or making tea can be a meaningful step.",
            "Let's schedule one thing — not to feel better, but just to do it.",
        ],
    },

    "Mindfulness": {
        "description": "Bringing non-judgmental present-moment awareness to thoughts and feelings.",
        "therapist_framing": (
            "Rather than fighting that feeling, what if we just noticed it for a moment? "
            "Where do you feel it in your body right now?"
        ),
        "example_phrases": [
            "Can you describe what that emotion feels like physically?",
            "Let's just observe the thought without trying to change it.",
            "What do you notice when you sit with that feeling for 30 seconds?",
        ],
    },

    "GroundingExercise": {
        "description": "5-4-3-2-1 sensory technique to anchor to the present moment.",
        "therapist_framing": (
            "Let's try a quick grounding exercise. "
            "Can you name 5 things you can see around you right now?"
        ),
        "example_phrases": [
            "5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.",
            "Feel your feet on the floor — press down gently.",
            "Take a slow breath in for 4 counts, hold for 4, out for 6.",
        ],
    },

    "ExposureTherapy": {
        "description": "Gradual, structured approach to feared situations to reduce avoidance.",
        "therapist_framing": (
            "Avoidance gives immediate relief but feeds the fear over time. "
            "What is the smallest, safest version of the situation you could try this week?"
        ),
        "example_phrases": [
            "We'd start with something that feels a 3 out of 10 in difficulty, not a 10.",
            "Each small step teaches your brain that the situation is manageable.",
            "What would a tiny experiment look like here?",
        ],
    },

    "RelaxationTraining": {
        "description": "Structured techniques to reduce physiological arousal.",
        "therapist_framing": (
            "Your body is responding to stress right now. "
            "Let's try slowing the breath — breathe in for 4, hold for 4, out for 6."
        ),
        "example_phrases": [
            "Slow, deep breathing activates the parasympathetic system — it physically calms you.",
            "Notice any tension in your shoulders or jaw and consciously release it.",
            "Even 3 minutes of slow breathing has a measurable effect on anxiety.",
        ],
    },

    "ProgressiveMuscleRelaxation": {
        "description": "Systematically tensing and releasing muscle groups to reduce tension.",
        "therapist_framing": (
            "Let's release some of that physical tension. "
            "Starting with your hands — clench them tightly for 5 seconds, then let go completely."
        ),
        "example_phrases": [
            "Notice the difference between tension and release.",
            "Work through each muscle group from hands up to face.",
            "This works best practiced daily for a few minutes before sleep.",
        ],
    },

    "ProblemSolving": {
        "description": "Structured steps to break an overwhelming problem into manageable actions.",
        "therapist_framing": (
            "Let's take this one step at a time. "
            "If you could only do one thing about this situation this week, what would feel most useful?"
        ),
        "example_phrases": [
            "What are all the possible options, even imperfect ones?",
            "Which option feels most manageable to start with?",
            "What would need to happen first?",
        ],
    },

    "SocialSkillsTraining": {
        "description": "Building confidence in interpersonal situations through practice.",
        "therapist_framing": (
            "Social situations can feel very high-stakes. "
            "Is there a low-pressure interaction — a quick message to someone — you could try this week?"
        ),
        "example_phrases": [
            "What would you ideally want to say in that situation?",
            "Let's think about what 'good enough' looks like here, not perfect.",
            "Connection doesn't have to be big — a brief genuine exchange counts.",
        ],
    },

    "GriefWork": {
        "description": "Processing loss through structured reflection and meaning-making.",
        "therapist_framing": (
            "Grief doesn't move in a straight line. "
            "What does missing them feel like for you today?"
        ),
        "example_phrases": [
            "It's okay to have good days and hard days — both are part of it.",
            "What do you want people to know about who they were?",
            "Is there a small ritual or memory that feels comforting?",
        ],
    },

    "SelfCompassion": {
        "description": "Treating oneself with the same kindness one would offer a close friend.",
        "therapist_framing": (
            "I notice you're being quite hard on yourself. "
            "What would you say to a close friend who was going through exactly this?"
        ),
        "example_phrases": [
            "You don't have to earn rest or care — it's not a reward.",
            "The harshness of that inner voice — does it actually help you do better?",
            "What does being kind to yourself look like, practically, today?",
        ],
    },

    "JournallingOrThoughtRecords": {
        "description": "Writing to externalize and examine thoughts and emotional patterns.",
        "therapist_framing": (
            "Getting thoughts out of your head and onto paper can help you see them more clearly. "
            "Would you be open to writing down that thought and what triggered it?"
        ),
        "example_phrases": [
            "Just writing what happened, what you thought, and what you felt — no analysis needed.",
            "Patterns often become visible over a week of notes.",
            "It doesn't need to be long — even 5 sentences is enough.",
        ],
    },

    "ThoughtRecord": {
        "description": "Structured CBT worksheet to examine the evidence for and against a thought.",
        "therapist_framing": (
            "Let's examine that thought. "
            "What is the thought exactly, what triggered it, and what evidence do you have for and against it?"
        ),
        "example_phrases": [
            "Situation → Thought → Emotion → Evidence For → Evidence Against → Alternative Thought",
            "We're not trying to think positively, we're trying to think accurately.",
            "What's a more balanced version of that thought?",
        ],
    },

    "MotivationalInterviewingTechnique": {
        "description": "Eliciting the patient's own reasons for change through reflective listening.",
        "therapist_framing": (
            "I'm curious — what would change for you if this got even a little better?"
        ),
        "example_phrases": [
            "What matters most to you about making this change?",
            "On a scale of 1–10, how important is this to you? What would make it a higher number?",
            "You've clearly been thinking about this — what's the part you feel ready for?",
        ],
    },

    "DistressToleranceSkills": {
        "description": "DBT skills for surviving crisis moments without making things worse.",
        "therapist_framing": (
            "This moment feels unbearable, but it will pass. "
            "Let's find one thing that can help you get through the next hour."
        ),
        "example_phrases": [
            "TIPP: Temperature, Intense exercise, Paced breathing, Progressive relaxation.",
            "Hold ice in your hand — the cold sensation grounds the nervous system.",
            "Distract: ACCEPTS — Activities, Contributing, Comparisons, Emotions, Pushing Away, Thoughts, Sensations.",
        ],
    },

    "EmotionRegulationSkills": {
        "description": "DBT skills to reduce emotional vulnerability and manage intense feelings.",
        "therapist_framing": (
            "That emotion makes complete sense given what you've been through. "
            "Let's look at what might be making you more vulnerable to it right now."
        ),
        "example_phrases": [
            "PLEASE: treat PhysicaL illness, balanced Eating, Avoid mood-altering substances, Sleep, Exercise.",
            "Opposite action: act opposite to what the emotion urges when the emotion isn't justified.",
            "Check the facts: is the intensity of the emotion proportional to what actually happened?",
        ],
    },

    "TraumaProcessing": {
        "description": "Structured work to process traumatic memories and reduce their emotional charge.",
        "therapist_framing": (
            "You don't have to go through that memory alone or all at once. "
            "We can approach it at whatever pace feels safe."
        ),
        "example_phrases": [
            "The goal isn't to forget — it's to change the relationship with the memory.",
            "We'll establish a safe place first before going anywhere near the difficult material.",
            "Your system protected you then — that response made sense in context.",
        ],
    },

    "SleepHygieneIntervention": {
        "description": "Evidence-based habits to improve sleep quality and consistency.",
        "therapist_framing": (
            "Poor sleep makes everything harder — mood, focus, resilience. "
            "What does your pre-sleep routine look like right now?"
        ),
        "example_phrases": [
            "Same wake time every day is the single most effective sleep intervention.",
            "Avoid screens 45 minutes before bed — the blue light delays melatonin.",
            "Keep the bedroom for sleep only — no phone, no working in bed.",
        ],
    },

    "RelapsePreventionCounseling": {
        "description": "Identifying triggers and building a coping plan to maintain gains.",
        "therapist_framing": (
            "Progress isn't linear — that's normal. "
            "What are the early warning signs that things are starting to slip for you?"
        ),
        "example_phrases": [
            "What situations or feelings tend to come just before a hard patch?",
            "What has helped in the past, even a little?",
            "Who could you reach out to if things felt overwhelming again?",
        ],
    },

    "InterpersonalEffectiveness": {
        "description": "DBT skills for maintaining relationships while asserting needs.",
        "therapist_framing": (
            "You deserve to have your needs heard. "
            "DEAR MAN: Describe, Express, Assert, Reinforce, stay Mindful, Appear confident, Negotiate."
        ),
        "example_phrases": [
            "How can you say what you need while keeping the relationship intact?",
            "What's the minimum outcome you'd be okay with in this conversation?",
            "What tone would make you most likely to be heard?",
        ],
    },
}

# Fallback for techniques in the KG that don't have specific guidance yet
_GENERIC_GUIDANCE = {
    "description": "Evidence-based therapeutic technique.",
    "therapist_framing": (
        "There are some approaches that tend to help in situations like yours. "
        "Would you be open to exploring one together?"
    ),
    "example_phrases": [
        "Let's think about one small, concrete step.",
        "What feels most manageable to try first?",
    ],
}


def get_guidance(technique_name: str) -> dict:
    """
    Returns the clinical guidance dict for a technique node name.
    Tries exact match first, then case-insensitive, then returns generic fallback.
    """
    if technique_name in TECHNIQUE_GUIDANCE:
        return TECHNIQUE_GUIDANCE[technique_name]

    # Case-insensitive lookup
    lower = technique_name.lower()
    for k, v in TECHNIQUE_GUIDANCE.items():
        if k.lower() == lower:
            return v

    # Partial match (e.g. "SleepHygiene" matches "SleepHygieneIntervention")
    for k, v in TECHNIQUE_GUIDANCE.items():
        if lower in k.lower() or k.lower() in lower:
            return v

    return _GENERIC_GUIDANCE
