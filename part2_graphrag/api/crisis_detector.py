"""
crisis_detector.py
==================
Safety-first layer that runs BEFORE any LLM call.
Detects crisis signals (suicidal ideation, self-harm, immediate danger)
and short-circuits the pipeline to return emergency resources.

This module is LLM-agnostic and must always be invoked first.
"""

import re
from dataclasses import dataclass

# ── Crisis keyword categories ──────────────────────────────────────────────────
_CRISIS_PATTERNS = [
    # Suicidal ideation / plans
    r"\b(want to die|wanna die|want to end (my|this) life|end it all)\b",
    r"\b(kill myself|killing myself|suicide|suicidal|take my (own )?life)\b",
    r"\b(no reason to live|not worth living|better off dead|better off without me)\b",
    r"\b(planning to (hurt|kill)|have a plan|goodbye (letter|note))\b",
    # Active self-harm
    r"\b(cutting myself|cut myself|hurt myself|harming myself|self.harm|self.injur)\b",
    r"\b(burning myself|scratching until|hit myself)\b",
    # Immediate danger
    r"\b(someone (is )?hurting me|being (abused|attacked)|in danger)\b",
    r"\b(overdose|took too many pills|swallowed)\b",
    r"\b(don'?t want to (wake up|be here|exist|live))\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _CRISIS_PATTERNS]

CRISIS_RESPONSE = """\
I'm really glad you reached out, and I want you to know I'm here with you.

What you're going through sounds incredibly painful, and you deserve real support \
right now — more than I'm able to provide alone.

🆘 Please reach out to a crisis professional immediately:

  • iCall (India):              9152987821  (Mon–Sat 8am–10pm)
  • Vandrevala Foundation:      1860-2662-345 (24/7)
  • NIMHANS (Bengaluru):        080-46110007
  • International Association:  https://www.iasp.info/resources/Crisis_Centres/

If you are in immediate danger, please call 112 (India emergency services).

You are not alone. Would you like to talk about what's been happening?
"""


@dataclass
class CrisisResult:
    is_crisis: bool
    matched_pattern: str | None
    response: str | None


def detect(text: str) -> CrisisResult:
    """
    Scans user text for crisis signals.
    Returns CrisisResult with is_crisis=True and a ready-made response if detected.
    """
    for pattern in _COMPILED:
        m = pattern.search(text)
        if m:
            return CrisisResult(
                is_crisis=True,
                matched_pattern=m.group(0),
                response=CRISIS_RESPONSE,
            )
    return CrisisResult(is_crisis=False, matched_pattern=None, response=None)
