# Layer 6 — Datasets used (provenance manifest)

Every `:Session` node carries its `source` dataset and provenance tier so gold-only
views can be filtered later. Tiers reflect clinical authority, not size.

| Dataset | Tier | What it is | Sessions | Used |
|---------|------|-----------|---------:|:----:|
| **AnnoMI** | 🥇 gold | Real motivational-interviewing therapy transcripts, expert-annotated | 133 | ✅ |
| **CounselChat** | 🥇 gold | Real **licensed-therapist** Q&A (counselchat.com) + topic tags | 2,775 | ✅ |
| **Mental Health Counseling** | 🥇 gold | Real **licensed-professional** Context→Response pairs (Amod, DOI 10.57967/hf/1581) | 3,512 | ✅ |
| **ESConv** | 🥈 silver | Emotional-support dialogues by crowdworkers trained in Hill's helping skills | 1,300 | ✅ |
| **ExTES** | 🟠 synthetic | LLM-generated emotional-support dialogues (ACL 2023) | ~90,063 | ✅ (volume) |
| **EmpatheticDialogues** | 🟠 synthetic | Crowdsourced empathetic chit-chat, 32 emotions (FAIR, ACL 2019) | ~24,850 | ✅ (volume) |
| **EPITOME / PHR** | — | **Dropped** — on-disk copy is a duplicate of Mental Health Counseling (same schema + row count) | 3,512 | ❌ dup |
| **HOPE** | 🥇 gold | 202 real dyadic psychotherapy transcripts (WSDM 2022) | 202 | ❌ **gated** — request access at LCS2-IIITD/SPARTA_WSDM2022, then add |

**Totals ingested:** ~122,633 sessions (README rounds to the ~123,926 loaded incl. multi-split).
**Real/professional (gold):** ~6,420 · **silver:** 1,300 · **synthetic (volume):** ~114,900.

## How provenance is stored on each `:Session`
- `s.source` — exact dataset, e.g. `'CounselChat'`, `'AnnoMI'`, `'ExTES_ACL2023'`.
- `s.tier`   — **1** = real/professional + structured (AnnoMI, CounselChat, MHCC, ESConv ≈ 8,270);
              **2** = synthetic bulk (ExTES, EmpatheticDialogues).
- `s.clinical_grade` — finer text label carried from ingestion.

Clinically-authoritative retrieval → filter `WHERE s.tier = 1` (optionally a specific
`s.source`). Use tier 2 for volume/semantic coverage only.

## Notes
- "Gold standard" = authored by real clinicians/professionals (AnnoMI, CounselChat, MHCC).
  Full *real* transcribed sessions (HOPE) require a manual access request — the only missing gold source.
- EPITOME_PHR was ingested then **removed** (3,512 sessions) — its on-disk data is a
  byte-for-byte duplicate of MHCC (verified 995/995 identical utterances).
- Session→disorder links come from keyword + semantic classification, then the P0
  cleanup (`10_cleanup_canonical_100.py`). Precision on the synthetic bulk is
  approximate — prefer tier-1 sessions for clinical claims. Re-running
  `semantic_disorder_classifier.py` with tighter thresholds is the recommended
  precision follow-up.
