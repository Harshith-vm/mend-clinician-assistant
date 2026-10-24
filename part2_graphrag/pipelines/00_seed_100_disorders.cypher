// ============================================================================
// 10_canonical_100_disorders.cypher
// ----------------------------------------------------------------------------
// AUTHORITATIVE SOURCE : FINAL CORRECTION AUDIT & VALIDATION REPORT (Section I,
//                        'The Mathematical 100'). This file supersedes the
//                        disorder definitions in 00-04 / 09 for Layer 1.
//
// CONTENT              : Exactly 100 primary :Disorder nodes (count_as_primary_disorder=true)
//                        + 1 :DiagnosticQualifier (Borderline pattern, 6D11.5) which is
//                        NOT one of the 100 and is linked via -[:HAS_QUALIFIER]->
//                        from PersonalityDisorder (6D10).
//
// KEY / DETERMINISM    : `name` == `canonical_name` is the deterministic unique key
//                        (matches the existing disorder_name uniqueness constraint and
//                        keeps a stable ID for the later semantic/vector-search layer).
//                        No embeddings / similarity are used to establish equivalence here.
//
// SAFE TO RE-RUN       : all writes are MERGE ... ON CREATE SET (idempotent).
// TARGET DATABASE      : therapy   (never system / neo4j).
// PROVENANCE           : ICD entities -> ICD-11 2026-01 (baseline 2024-01);
//                        DSM-only entities -> DSM-5-TR (source_url is provenance only).
// ============================================================================

CREATE CONSTRAINT disorder_name IF NOT EXISTS
FOR (n:Disorder) REQUIRE (n.name) IS UNIQUE;

CREATE CONSTRAINT diagnostic_qualifier_name IF NOT EXISTS
FOR (n:DiagnosticQualifier) REQUIRE (n.name) IS UNIQUE;

// ---- Neurodevelopmental disorders (6A0x) ----
//   1. AttentionDeficitHyperactivityDisorder  [ICD-11 6A05]  status=ESTABLISHED_DISORDER
MERGE (d1:Disorder {name:'AttentionDeficitHyperactivityDisorder'})
ON CREATE SET
  d1.canonical_name = 'AttentionDeficitHyperactivityDisorder',
  d1.official_name = 'Attention deficit hyperactivity disorder',
  d1.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d1.icd11_code = '6A05',
  d1.icd11_release = '2026-01',
  d1.icd11_baseline_release = '2024-01',
  d1.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d1.dsm5_tr_relationship = 'EXACT',
  d1.classification_status = 'ESTABLISHED_DISORDER',
  d1.count_as_primary_disorder = true,
  d1.audit_row = 1,
  d1.verification_status = 'VERIFIED',
  d1.verification_date = date('2026-09-05'),
  d1.date_added = date();

//   2. AutismSpectrumDisorder  [ICD-11 6A02]  status=ESTABLISHED_DISORDER
MERGE (d2:Disorder {name:'AutismSpectrumDisorder'})
ON CREATE SET
  d2.canonical_name = 'AutismSpectrumDisorder',
  d2.official_name = 'Autism spectrum disorder',
  d2.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d2.icd11_code = '6A02',
  d2.icd11_release = '2026-01',
  d2.icd11_baseline_release = '2024-01',
  d2.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d2.dsm5_tr_relationship = 'EXACT',
  d2.classification_status = 'ESTABLISHED_DISORDER',
  d2.count_as_primary_disorder = true,
  d2.audit_row = 2,
  d2.verification_status = 'VERIFIED',
  d2.verification_date = date('2026-09-05'),
  d2.date_added = date();

//   3. DisorderOfIntellectualDevelopment  [ICD-11 6A00]  status=ESTABLISHED_DISORDER
MERGE (d3:Disorder {name:'DisorderOfIntellectualDevelopment'})
ON CREATE SET
  d3.canonical_name = 'DisorderOfIntellectualDevelopment',
  d3.official_name = 'Disorder of intellectual development',
  d3.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d3.icd11_code = '6A00',
  d3.icd11_release = '2026-01',
  d3.icd11_baseline_release = '2024-01',
  d3.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d3.dsm5_tr_relationship = 'EXACT',
  d3.classification_status = 'ESTABLISHED_DISORDER',
  d3.count_as_primary_disorder = true,
  d3.audit_row = 3,
  d3.verification_status = 'VERIFIED',
  d3.verification_date = date('2026-09-05'),
  d3.date_added = date();

//   4. DevelopmentalLearningDisorder  [ICD-11 6A03]  status=ESTABLISHED_DISORDER
MERGE (d4:Disorder {name:'DevelopmentalLearningDisorder'})
ON CREATE SET
  d4.canonical_name = 'DevelopmentalLearningDisorder',
  d4.official_name = 'Developmental learning disorder',
  d4.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d4.icd11_code = '6A03',
  d4.icd11_release = '2026-01',
  d4.icd11_baseline_release = '2024-01',
  d4.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d4.dsm5_tr_relationship = 'EXACT',
  d4.classification_status = 'ESTABLISHED_DISORDER',
  d4.count_as_primary_disorder = true,
  d4.audit_row = 4,
  d4.verification_status = 'VERIFIED',
  d4.verification_date = date('2026-09-05'),
  d4.date_added = date();

//   5. DevelopmentalMotorCoordinationDisorder  [ICD-11 6A04]  status=ESTABLISHED_DISORDER
MERGE (d5:Disorder {name:'DevelopmentalMotorCoordinationDisorder'})
ON CREATE SET
  d5.canonical_name = 'DevelopmentalMotorCoordinationDisorder',
  d5.official_name = 'Developmental motor coordination disorder',
  d5.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d5.icd11_code = '6A04',
  d5.icd11_release = '2026-01',
  d5.icd11_baseline_release = '2024-01',
  d5.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d5.dsm5_tr_relationship = 'EXACT',
  d5.classification_status = 'ESTABLISHED_DISORDER',
  d5.count_as_primary_disorder = true,
  d5.audit_row = 5,
  d5.verification_status = 'VERIFIED',
  d5.verification_date = date('2026-09-05'),
  d5.date_added = date();

//   6. DevelopmentalSpeechSoundDisorder  [ICD-11 6A01.0]  status=ESTABLISHED_DISORDER
MERGE (d6:Disorder {name:'DevelopmentalSpeechSoundDisorder'})
ON CREATE SET
  d6.canonical_name = 'DevelopmentalSpeechSoundDisorder',
  d6.official_name = 'Developmental speech sound disorder',
  d6.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d6.icd11_code = '6A01.0',
  d6.icd11_release = '2026-01',
  d6.icd11_baseline_release = '2024-01',
  d6.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d6.dsm5_tr_relationship = 'EXACT',
  d6.classification_status = 'ESTABLISHED_DISORDER',
  d6.count_as_primary_disorder = true,
  d6.audit_row = 6,
  d6.verification_status = 'VERIFIED',
  d6.verification_date = date('2026-09-05'),
  d6.date_added = date();

//   7. DevelopmentalLanguageDisorder  [ICD-11 6A01.2]  status=ESTABLISHED_DISORDER
MERGE (d7:Disorder {name:'DevelopmentalLanguageDisorder'})
ON CREATE SET
  d7.canonical_name = 'DevelopmentalLanguageDisorder',
  d7.official_name = 'Developmental language disorder',
  d7.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d7.icd11_code = '6A01.2',
  d7.icd11_release = '2026-01',
  d7.icd11_baseline_release = '2024-01',
  d7.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d7.dsm5_tr_relationship = 'EXACT',
  d7.classification_status = 'ESTABLISHED_DISORDER',
  d7.count_as_primary_disorder = true,
  d7.audit_row = 7,
  d7.verification_status = 'VERIFIED',
  d7.verification_date = date('2026-09-05'),
  d7.date_added = date();

//   8. StereotypedMovementDisorder  [ICD-11 6A06]  status=ESTABLISHED_DISORDER
MERGE (d8:Disorder {name:'StereotypedMovementDisorder'})
ON CREATE SET
  d8.canonical_name = 'StereotypedMovementDisorder',
  d8.official_name = 'Stereotyped movement disorder',
  d8.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d8.icd11_code = '6A06',
  d8.icd11_release = '2026-01',
  d8.icd11_baseline_release = '2024-01',
  d8.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d8.dsm5_tr_relationship = 'EXACT',
  d8.classification_status = 'ESTABLISHED_DISORDER',
  d8.count_as_primary_disorder = true,
  d8.audit_row = 8,
  d8.verification_status = 'VERIFIED',
  d8.verification_date = date('2026-09-05'),
  d8.date_added = date();

// ---- Schizophrenia & other primary psychotic disorders (6A2x) ----
//   9. Schizophrenia  [ICD-11 6A20]  status=ESTABLISHED_DISORDER
MERGE (d9:Disorder {name:'Schizophrenia'})
ON CREATE SET
  d9.canonical_name = 'Schizophrenia',
  d9.official_name = 'Schizophrenia',
  d9.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d9.icd11_code = '6A20',
  d9.icd11_release = '2026-01',
  d9.icd11_baseline_release = '2024-01',
  d9.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d9.dsm5_tr_relationship = 'EXACT',
  d9.classification_status = 'ESTABLISHED_DISORDER',
  d9.count_as_primary_disorder = true,
  d9.audit_row = 9,
  d9.verification_status = 'VERIFIED',
  d9.verification_date = date('2026-09-05'),
  d9.date_added = date();

//  10. SchizoaffectiveDisorder  [ICD-11 6A21]  status=ESTABLISHED_DISORDER
MERGE (d10:Disorder {name:'SchizoaffectiveDisorder'})
ON CREATE SET
  d10.canonical_name = 'SchizoaffectiveDisorder',
  d10.official_name = 'Schizoaffective disorder',
  d10.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d10.icd11_code = '6A21',
  d10.icd11_release = '2026-01',
  d10.icd11_baseline_release = '2024-01',
  d10.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d10.dsm5_tr_relationship = 'EXACT',
  d10.classification_status = 'ESTABLISHED_DISORDER',
  d10.count_as_primary_disorder = true,
  d10.audit_row = 10,
  d10.verification_status = 'VERIFIED',
  d10.verification_date = date('2026-09-05'),
  d10.date_added = date();

//  11. SchizotypalDisorder  [ICD-11 6A22]  status=ESTABLISHED_DISORDER
MERGE (d11:Disorder {name:'SchizotypalDisorder'})
ON CREATE SET
  d11.canonical_name = 'SchizotypalDisorder',
  d11.official_name = 'Schizotypal disorder',
  d11.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d11.icd11_code = '6A22',
  d11.icd11_release = '2026-01',
  d11.icd11_baseline_release = '2024-01',
  d11.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d11.dsm5_tr_relationship = 'EXACT',
  d11.classification_status = 'ESTABLISHED_DISORDER',
  d11.count_as_primary_disorder = true,
  d11.audit_row = 11,
  d11.verification_status = 'VERIFIED',
  d11.verification_date = date('2026-09-05'),
  d11.date_added = date();

//  12. AcuteAndTransientPsychoticDisorder  [ICD-11 6A23]  status=ESTABLISHED_DISORDER
MERGE (d12:Disorder {name:'AcuteAndTransientPsychoticDisorder'})
ON CREATE SET
  d12.canonical_name = 'AcuteAndTransientPsychoticDisorder',
  d12.official_name = 'Acute and transient psychotic disorder',
  d12.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d12.icd11_code = '6A23',
  d12.icd11_release = '2026-01',
  d12.icd11_baseline_release = '2024-01',
  d12.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d12.dsm5_tr_relationship = 'APPROXIMATE',
  d12.classification_status = 'ESTABLISHED_DISORDER',
  d12.count_as_primary_disorder = true,
  d12.audit_row = 12,
  d12.verification_status = 'VERIFIED',
  d12.verification_date = date('2026-09-05'),
  d12.date_added = date();

//  13. DelusionalDisorder  [ICD-11 6A24]  status=ESTABLISHED_DISORDER
MERGE (d13:Disorder {name:'DelusionalDisorder'})
ON CREATE SET
  d13.canonical_name = 'DelusionalDisorder',
  d13.official_name = 'Delusional disorder',
  d13.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d13.icd11_code = '6A24',
  d13.icd11_release = '2026-01',
  d13.icd11_baseline_release = '2024-01',
  d13.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d13.dsm5_tr_relationship = 'EXACT',
  d13.classification_status = 'ESTABLISHED_DISORDER',
  d13.count_as_primary_disorder = true,
  d13.audit_row = 13,
  d13.verification_status = 'VERIFIED',
  d13.verification_date = date('2026-09-05'),
  d13.date_added = date();

// ---- Bipolar & related disorders (6A6x) ----
//  14. BipolarTypeIDisorder  [ICD-11 6A60]  status=ESTABLISHED_DISORDER
MERGE (d14:Disorder {name:'BipolarTypeIDisorder'})
ON CREATE SET
  d14.canonical_name = 'BipolarTypeIDisorder',
  d14.official_name = 'Bipolar type I disorder',
  d14.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d14.icd11_code = '6A60',
  d14.icd11_release = '2026-01',
  d14.icd11_baseline_release = '2024-01',
  d14.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d14.dsm5_tr_relationship = 'EXACT',
  d14.classification_status = 'ESTABLISHED_DISORDER',
  d14.count_as_primary_disorder = true,
  d14.audit_row = 14,
  d14.verification_status = 'VERIFIED',
  d14.verification_date = date('2026-09-05'),
  d14.date_added = date();

//  15. BipolarTypeIIDisorder  [ICD-11 6A61]  status=ESTABLISHED_DISORDER
MERGE (d15:Disorder {name:'BipolarTypeIIDisorder'})
ON CREATE SET
  d15.canonical_name = 'BipolarTypeIIDisorder',
  d15.official_name = 'Bipolar type II disorder',
  d15.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d15.icd11_code = '6A61',
  d15.icd11_release = '2026-01',
  d15.icd11_baseline_release = '2024-01',
  d15.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d15.dsm5_tr_relationship = 'EXACT',
  d15.classification_status = 'ESTABLISHED_DISORDER',
  d15.count_as_primary_disorder = true,
  d15.audit_row = 15,
  d15.verification_status = 'VERIFIED',
  d15.verification_date = date('2026-09-05'),
  d15.date_added = date();

//  16. CyclothymicDisorder  [ICD-11 6A62]  status=ESTABLISHED_DISORDER
MERGE (d16:Disorder {name:'CyclothymicDisorder'})
ON CREATE SET
  d16.canonical_name = 'CyclothymicDisorder',
  d16.official_name = 'Cyclothymic disorder',
  d16.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d16.icd11_code = '6A62',
  d16.icd11_release = '2026-01',
  d16.icd11_baseline_release = '2024-01',
  d16.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d16.dsm5_tr_relationship = 'EXACT',
  d16.classification_status = 'ESTABLISHED_DISORDER',
  d16.count_as_primary_disorder = true,
  d16.audit_row = 16,
  d16.verification_status = 'VERIFIED',
  d16.verification_date = date('2026-09-05'),
  d16.date_added = date();

// ---- Depressive disorders (6A7x) ----
//  17. SingleEpisodeDepressiveDisorder  [ICD-11 6A70]  status=ESTABLISHED_DISORDER
MERGE (d17:Disorder {name:'SingleEpisodeDepressiveDisorder'})
ON CREATE SET
  d17.canonical_name = 'SingleEpisodeDepressiveDisorder',
  d17.official_name = 'Single episode depressive disorder',
  d17.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d17.icd11_code = '6A70',
  d17.icd11_release = '2026-01',
  d17.icd11_baseline_release = '2024-01',
  d17.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d17.dsm5_tr_relationship = 'APPROXIMATE',
  d17.classification_status = 'ESTABLISHED_DISORDER',
  d17.count_as_primary_disorder = true,
  d17.audit_row = 17,
  d17.verification_status = 'VERIFIED',
  d17.verification_date = date('2026-09-05'),
  d17.date_added = date();

//  18. RecurrentDepressiveDisorder  [ICD-11 6A71]  status=ESTABLISHED_DISORDER
MERGE (d18:Disorder {name:'RecurrentDepressiveDisorder'})
ON CREATE SET
  d18.canonical_name = 'RecurrentDepressiveDisorder',
  d18.official_name = 'Recurrent depressive disorder',
  d18.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d18.icd11_code = '6A71',
  d18.icd11_release = '2026-01',
  d18.icd11_baseline_release = '2024-01',
  d18.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d18.dsm5_tr_relationship = 'APPROXIMATE',
  d18.classification_status = 'ESTABLISHED_DISORDER',
  d18.count_as_primary_disorder = true,
  d18.audit_row = 18,
  d18.verification_status = 'VERIFIED',
  d18.verification_date = date('2026-09-05'),
  d18.date_added = date();

//  19. DysthymicDisorder  [ICD-11 6A72]  status=ESTABLISHED_DISORDER
MERGE (d19:Disorder {name:'DysthymicDisorder'})
ON CREATE SET
  d19.canonical_name = 'DysthymicDisorder',
  d19.official_name = 'Dysthymic disorder',
  d19.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d19.icd11_code = '6A72',
  d19.icd11_release = '2026-01',
  d19.icd11_baseline_release = '2024-01',
  d19.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d19.dsm5_tr_relationship = 'CLOSE',
  d19.classification_status = 'ESTABLISHED_DISORDER',
  d19.count_as_primary_disorder = true,
  d19.audit_row = 19,
  d19.verification_status = 'VERIFIED',
  d19.verification_date = date('2026-09-05'),
  d19.date_added = date();

// ---- Mixed depressive & anxiety disorder (6A73) ----
//  89. MixedDepressiveAndAnxietyDisorder  [ICD-11 6A73]  status=ESTABLISHED_DISORDER
MERGE (d89:Disorder {name:'MixedDepressiveAndAnxietyDisorder'})
ON CREATE SET
  d89.canonical_name = 'MixedDepressiveAndAnxietyDisorder',
  d89.official_name = 'Mixed depressive and anxiety disorder',
  d89.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d89.icd11_code = '6A73',
  d89.icd11_release = '2026-01',
  d89.icd11_baseline_release = '2024-01',
  d89.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d89.dsm5_tr_relationship = 'NO_DIRECT_EQUIVALENT',
  d89.classification_status = 'ESTABLISHED_DISORDER',
  d89.count_as_primary_disorder = true,
  d89.audit_row = 89,
  d89.verification_status = 'VERIFIED',
  d89.verification_date = date('2026-09-05'),
  d89.date_added = date();

// ---- Anxiety & fear-related disorders (6B0x) ----
//  20. GeneralizedAnxietyDisorder  [ICD-11 6B00]  status=ESTABLISHED_DISORDER
MERGE (d20:Disorder {name:'GeneralizedAnxietyDisorder'})
ON CREATE SET
  d20.canonical_name = 'GeneralizedAnxietyDisorder',
  d20.official_name = 'Generalised anxiety disorder',
  d20.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d20.icd11_code = '6B00',
  d20.icd11_release = '2026-01',
  d20.icd11_baseline_release = '2024-01',
  d20.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d20.dsm5_tr_relationship = 'EXACT',
  d20.classification_status = 'ESTABLISHED_DISORDER',
  d20.count_as_primary_disorder = true,
  d20.audit_row = 20,
  d20.verification_status = 'VERIFIED',
  d20.verification_date = date('2026-09-05'),
  d20.date_added = date();

//  21. PanicDisorder  [ICD-11 6B01]  status=ESTABLISHED_DISORDER
MERGE (d21:Disorder {name:'PanicDisorder'})
ON CREATE SET
  d21.canonical_name = 'PanicDisorder',
  d21.official_name = 'Panic disorder',
  d21.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d21.icd11_code = '6B01',
  d21.icd11_release = '2026-01',
  d21.icd11_baseline_release = '2024-01',
  d21.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d21.dsm5_tr_relationship = 'EXACT',
  d21.classification_status = 'ESTABLISHED_DISORDER',
  d21.count_as_primary_disorder = true,
  d21.audit_row = 21,
  d21.verification_status = 'VERIFIED',
  d21.verification_date = date('2026-09-05'),
  d21.date_added = date();

//  22. Agoraphobia  [ICD-11 6B02]  status=ESTABLISHED_DISORDER
MERGE (d22:Disorder {name:'Agoraphobia'})
ON CREATE SET
  d22.canonical_name = 'Agoraphobia',
  d22.official_name = 'Agoraphobia',
  d22.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d22.icd11_code = '6B02',
  d22.icd11_release = '2026-01',
  d22.icd11_baseline_release = '2024-01',
  d22.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d22.dsm5_tr_relationship = 'EXACT',
  d22.classification_status = 'ESTABLISHED_DISORDER',
  d22.count_as_primary_disorder = true,
  d22.audit_row = 22,
  d22.verification_status = 'VERIFIED',
  d22.verification_date = date('2026-09-05'),
  d22.date_added = date();

//  23. SpecificPhobia  [ICD-11 6B03]  status=ESTABLISHED_DISORDER
MERGE (d23:Disorder {name:'SpecificPhobia'})
ON CREATE SET
  d23.canonical_name = 'SpecificPhobia',
  d23.official_name = 'Specific phobia',
  d23.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d23.icd11_code = '6B03',
  d23.icd11_release = '2026-01',
  d23.icd11_baseline_release = '2024-01',
  d23.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d23.dsm5_tr_relationship = 'EXACT',
  d23.classification_status = 'ESTABLISHED_DISORDER',
  d23.count_as_primary_disorder = true,
  d23.audit_row = 23,
  d23.verification_status = 'VERIFIED',
  d23.verification_date = date('2026-09-05'),
  d23.date_added = date();

//  24. SocialAnxietyDisorder  [ICD-11 6B04]  status=ESTABLISHED_DISORDER
MERGE (d24:Disorder {name:'SocialAnxietyDisorder'})
ON CREATE SET
  d24.canonical_name = 'SocialAnxietyDisorder',
  d24.official_name = 'Social anxiety disorder',
  d24.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d24.icd11_code = '6B04',
  d24.icd11_release = '2026-01',
  d24.icd11_baseline_release = '2024-01',
  d24.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d24.dsm5_tr_relationship = 'EXACT',
  d24.classification_status = 'ESTABLISHED_DISORDER',
  d24.count_as_primary_disorder = true,
  d24.audit_row = 24,
  d24.verification_status = 'VERIFIED',
  d24.verification_date = date('2026-09-05'),
  d24.date_added = date();

//  25. SeparationAnxietyDisorder  [ICD-11 6B05]  status=ESTABLISHED_DISORDER
MERGE (d25:Disorder {name:'SeparationAnxietyDisorder'})
ON CREATE SET
  d25.canonical_name = 'SeparationAnxietyDisorder',
  d25.official_name = 'Separation anxiety disorder',
  d25.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d25.icd11_code = '6B05',
  d25.icd11_release = '2026-01',
  d25.icd11_baseline_release = '2024-01',
  d25.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d25.dsm5_tr_relationship = 'EXACT',
  d25.classification_status = 'ESTABLISHED_DISORDER',
  d25.count_as_primary_disorder = true,
  d25.audit_row = 25,
  d25.verification_status = 'VERIFIED',
  d25.verification_date = date('2026-09-05'),
  d25.date_added = date();

//  26. SelectiveMutism  [ICD-11 6B06]  status=ESTABLISHED_DISORDER
MERGE (d26:Disorder {name:'SelectiveMutism'})
ON CREATE SET
  d26.canonical_name = 'SelectiveMutism',
  d26.official_name = 'Selective mutism',
  d26.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d26.icd11_code = '6B06',
  d26.icd11_release = '2026-01',
  d26.icd11_baseline_release = '2024-01',
  d26.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d26.dsm5_tr_relationship = 'EXACT',
  d26.classification_status = 'ESTABLISHED_DISORDER',
  d26.count_as_primary_disorder = true,
  d26.audit_row = 26,
  d26.verification_status = 'VERIFIED',
  d26.verification_date = date('2026-09-05'),
  d26.date_added = date();

// ---- Obsessive-compulsive & related disorders (6B2x) ----
//  27. ObsessiveCompulsiveDisorder  [ICD-11 6B20]  status=ESTABLISHED_DISORDER
MERGE (d27:Disorder {name:'ObsessiveCompulsiveDisorder'})
ON CREATE SET
  d27.canonical_name = 'ObsessiveCompulsiveDisorder',
  d27.official_name = 'Obsessive-compulsive disorder',
  d27.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d27.icd11_code = '6B20',
  d27.icd11_release = '2026-01',
  d27.icd11_baseline_release = '2024-01',
  d27.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d27.dsm5_tr_relationship = 'EXACT',
  d27.classification_status = 'ESTABLISHED_DISORDER',
  d27.count_as_primary_disorder = true,
  d27.audit_row = 27,
  d27.verification_status = 'VERIFIED',
  d27.verification_date = date('2026-09-05'),
  d27.date_added = date();

//  28. BodyDysmorphicDisorder  [ICD-11 6B21]  status=ESTABLISHED_DISORDER
MERGE (d28:Disorder {name:'BodyDysmorphicDisorder'})
ON CREATE SET
  d28.canonical_name = 'BodyDysmorphicDisorder',
  d28.official_name = 'Body dysmorphic disorder',
  d28.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d28.icd11_code = '6B21',
  d28.icd11_release = '2026-01',
  d28.icd11_baseline_release = '2024-01',
  d28.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d28.dsm5_tr_relationship = 'EXACT',
  d28.classification_status = 'ESTABLISHED_DISORDER',
  d28.count_as_primary_disorder = true,
  d28.audit_row = 28,
  d28.verification_status = 'VERIFIED',
  d28.verification_date = date('2026-09-05'),
  d28.date_added = date();

//  29. OlfactoryReferenceDisorder  [ICD-11 6B22]  status=ESTABLISHED_DISORDER
MERGE (d29:Disorder {name:'OlfactoryReferenceDisorder'})
ON CREATE SET
  d29.canonical_name = 'OlfactoryReferenceDisorder',
  d29.official_name = 'Olfactory reference disorder',
  d29.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d29.icd11_code = '6B22',
  d29.icd11_release = '2026-01',
  d29.icd11_baseline_release = '2024-01',
  d29.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d29.dsm5_tr_relationship = 'NO_DIRECT_EQUIVALENT',
  d29.classification_status = 'ESTABLISHED_DISORDER',
  d29.count_as_primary_disorder = true,
  d29.audit_row = 29,
  d29.verification_status = 'VERIFIED',
  d29.verification_date = date('2026-09-05'),
  d29.date_added = date();

//  30. Hypochondriasis  [ICD-11 6B23]  status=ESTABLISHED_DISORDER
MERGE (d30:Disorder {name:'Hypochondriasis'})
ON CREATE SET
  d30.canonical_name = 'Hypochondriasis',
  d30.official_name = 'Hypochondriasis',
  d30.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d30.icd11_code = '6B23',
  d30.icd11_release = '2026-01',
  d30.icd11_baseline_release = '2024-01',
  d30.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d30.dsm5_tr_relationship = 'CLOSE',
  d30.classification_status = 'ESTABLISHED_DISORDER',
  d30.count_as_primary_disorder = true,
  d30.audit_row = 30,
  d30.verification_status = 'VERIFIED',
  d30.verification_date = date('2026-09-05'),
  d30.date_added = date();

//  31. HoardingDisorder  [ICD-11 6B24]  status=ESTABLISHED_DISORDER
MERGE (d31:Disorder {name:'HoardingDisorder'})
ON CREATE SET
  d31.canonical_name = 'HoardingDisorder',
  d31.official_name = 'Hoarding disorder',
  d31.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d31.icd11_code = '6B24',
  d31.icd11_release = '2026-01',
  d31.icd11_baseline_release = '2024-01',
  d31.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d31.dsm5_tr_relationship = 'EXACT',
  d31.classification_status = 'ESTABLISHED_DISORDER',
  d31.count_as_primary_disorder = true,
  d31.audit_row = 31,
  d31.verification_status = 'VERIFIED',
  d31.verification_date = date('2026-09-05'),
  d31.date_added = date();

//  32. Trichotillomania  [ICD-11 6B25.0]  status=ESTABLISHED_DISORDER
MERGE (d32:Disorder {name:'Trichotillomania'})
ON CREATE SET
  d32.canonical_name = 'Trichotillomania',
  d32.official_name = 'Trichotillomania',
  d32.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d32.icd11_code = '6B25.0',
  d32.icd11_release = '2026-01',
  d32.icd11_baseline_release = '2024-01',
  d32.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d32.dsm5_tr_relationship = 'EXACT',
  d32.classification_status = 'ESTABLISHED_DISORDER',
  d32.count_as_primary_disorder = true,
  d32.audit_row = 32,
  d32.verification_status = 'VERIFIED',
  d32.verification_date = date('2026-09-05'),
  d32.date_added = date();

//  33. ExcoriationDisorder  [ICD-11 6B25.1]  status=ESTABLISHED_DISORDER
MERGE (d33:Disorder {name:'ExcoriationDisorder'})
ON CREATE SET
  d33.canonical_name = 'ExcoriationDisorder',
  d33.official_name = 'Excoriation disorder',
  d33.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d33.icd11_code = '6B25.1',
  d33.icd11_release = '2026-01',
  d33.icd11_baseline_release = '2024-01',
  d33.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d33.dsm5_tr_relationship = 'EXACT',
  d33.classification_status = 'ESTABLISHED_DISORDER',
  d33.count_as_primary_disorder = true,
  d33.audit_row = 33,
  d33.verification_status = 'VERIFIED',
  d33.verification_date = date('2026-09-05'),
  d33.date_added = date();

// ---- Disorders specifically associated with stress (6B4x) ----
//  34. PostTraumaticStressDisorder  [ICD-11 6B40]  status=ESTABLISHED_DISORDER
MERGE (d34:Disorder {name:'PostTraumaticStressDisorder'})
ON CREATE SET
  d34.canonical_name = 'PostTraumaticStressDisorder',
  d34.official_name = 'Post traumatic stress disorder',
  d34.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d34.icd11_code = '6B40',
  d34.icd11_release = '2026-01',
  d34.icd11_baseline_release = '2024-01',
  d34.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d34.dsm5_tr_relationship = 'EXACT',
  d34.classification_status = 'ESTABLISHED_DISORDER',
  d34.count_as_primary_disorder = true,
  d34.audit_row = 34,
  d34.verification_status = 'VERIFIED',
  d34.verification_date = date('2026-09-05'),
  d34.date_added = date();

//  35. ComplexPTSD  [ICD-11 6B41]  status=ESTABLISHED_DISORDER
MERGE (d35:Disorder {name:'ComplexPTSD'})
ON CREATE SET
  d35.canonical_name = 'ComplexPTSD',
  d35.official_name = 'Complex post traumatic stress disorder',
  d35.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d35.icd11_code = '6B41',
  d35.icd11_release = '2026-01',
  d35.icd11_baseline_release = '2024-01',
  d35.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d35.dsm5_tr_relationship = 'NO_DIRECT_EQUIVALENT',
  d35.classification_status = 'ESTABLISHED_DISORDER',
  d35.count_as_primary_disorder = true,
  d35.audit_row = 35,
  d35.verification_status = 'VERIFIED',
  d35.verification_date = date('2026-09-05'),
  d35.date_added = date();

//  36. ProlongedGriefDisorder  [ICD-11 6B42]  status=ESTABLISHED_DISORDER
MERGE (d36:Disorder {name:'ProlongedGriefDisorder'})
ON CREATE SET
  d36.canonical_name = 'ProlongedGriefDisorder',
  d36.official_name = 'Prolonged grief disorder',
  d36.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d36.icd11_code = '6B42',
  d36.icd11_release = '2026-01',
  d36.icd11_baseline_release = '2024-01',
  d36.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d36.dsm5_tr_relationship = 'EXACT',
  d36.classification_status = 'ESTABLISHED_DISORDER',
  d36.count_as_primary_disorder = true,
  d36.audit_row = 36,
  d36.verification_status = 'VERIFIED',
  d36.verification_date = date('2026-09-05'),
  d36.date_added = date();

//  37. AdjustmentDisorder  [ICD-11 6B43]  status=ESTABLISHED_DISORDER
MERGE (d37:Disorder {name:'AdjustmentDisorder'})
ON CREATE SET
  d37.canonical_name = 'AdjustmentDisorder',
  d37.official_name = 'Adjustment disorder',
  d37.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d37.icd11_code = '6B43',
  d37.icd11_release = '2026-01',
  d37.icd11_baseline_release = '2024-01',
  d37.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d37.dsm5_tr_relationship = 'EXACT',
  d37.classification_status = 'ESTABLISHED_DISORDER',
  d37.count_as_primary_disorder = true,
  d37.audit_row = 37,
  d37.verification_status = 'VERIFIED',
  d37.verification_date = date('2026-09-05'),
  d37.date_added = date();

//  38. ReactiveAttachmentDisorder  [ICD-11 6B44]  status=ESTABLISHED_DISORDER
MERGE (d38:Disorder {name:'ReactiveAttachmentDisorder'})
ON CREATE SET
  d38.canonical_name = 'ReactiveAttachmentDisorder',
  d38.official_name = 'Reactive attachment disorder',
  d38.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d38.icd11_code = '6B44',
  d38.icd11_release = '2026-01',
  d38.icd11_baseline_release = '2024-01',
  d38.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d38.dsm5_tr_relationship = 'EXACT',
  d38.classification_status = 'ESTABLISHED_DISORDER',
  d38.count_as_primary_disorder = true,
  d38.audit_row = 38,
  d38.verification_status = 'VERIFIED',
  d38.verification_date = date('2026-09-05'),
  d38.date_added = date();

//  39. DisinhibitedSocialEngagementDisorder  [ICD-11 6B45]  status=ESTABLISHED_DISORDER
MERGE (d39:Disorder {name:'DisinhibitedSocialEngagementDisorder'})
ON CREATE SET
  d39.canonical_name = 'DisinhibitedSocialEngagementDisorder',
  d39.official_name = 'Disinhibited social engagement disorder',
  d39.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d39.icd11_code = '6B45',
  d39.icd11_release = '2026-01',
  d39.icd11_baseline_release = '2024-01',
  d39.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d39.dsm5_tr_relationship = 'EXACT',
  d39.classification_status = 'ESTABLISHED_DISORDER',
  d39.count_as_primary_disorder = true,
  d39.audit_row = 39,
  d39.verification_status = 'VERIFIED',
  d39.verification_date = date('2026-09-05'),
  d39.date_added = date();

// ---- Dissociative disorders (6B6x) ----
//  40. DissociativeNeurologicalSymptomDisorder  [ICD-11 6B60]  status=ESTABLISHED_DISORDER
MERGE (d40:Disorder {name:'DissociativeNeurologicalSymptomDisorder'})
ON CREATE SET
  d40.canonical_name = 'DissociativeNeurologicalSymptomDisorder',
  d40.official_name = 'Dissociative neurological symptom disorder',
  d40.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d40.icd11_code = '6B60',
  d40.icd11_release = '2026-01',
  d40.icd11_baseline_release = '2024-01',
  d40.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d40.dsm5_tr_relationship = 'CLOSE',
  d40.classification_status = 'ESTABLISHED_DISORDER',
  d40.count_as_primary_disorder = true,
  d40.audit_row = 40,
  d40.verification_status = 'VERIFIED',
  d40.verification_date = date('2026-09-05'),
  d40.date_added = date();

//  41. DissociativeAmnesia  [ICD-11 6B61]  status=ESTABLISHED_DISORDER
MERGE (d41:Disorder {name:'DissociativeAmnesia'})
ON CREATE SET
  d41.canonical_name = 'DissociativeAmnesia',
  d41.official_name = 'Dissociative amnesia',
  d41.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d41.icd11_code = '6B61',
  d41.icd11_release = '2026-01',
  d41.icd11_baseline_release = '2024-01',
  d41.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d41.dsm5_tr_relationship = 'EXACT',
  d41.classification_status = 'ESTABLISHED_DISORDER',
  d41.count_as_primary_disorder = true,
  d41.audit_row = 41,
  d41.verification_status = 'VERIFIED',
  d41.verification_date = date('2026-09-05'),
  d41.date_added = date();

//  42. TranceDisorder  [ICD-11 6B62]  status=ESTABLISHED_DISORDER
MERGE (d42:Disorder {name:'TranceDisorder'})
ON CREATE SET
  d42.canonical_name = 'TranceDisorder',
  d42.official_name = 'Trance disorder',
  d42.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d42.icd11_code = '6B62',
  d42.icd11_release = '2026-01',
  d42.icd11_baseline_release = '2024-01',
  d42.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d42.dsm5_tr_relationship = 'NO_DIRECT_EQUIVALENT',
  d42.classification_status = 'ESTABLISHED_DISORDER',
  d42.count_as_primary_disorder = true,
  d42.audit_row = 42,
  d42.verification_status = 'VERIFIED',
  d42.verification_date = date('2026-09-05'),
  d42.date_added = date();

//  43. PossessionTranceDisorder  [ICD-11 6B63]  status=ESTABLISHED_DISORDER
MERGE (d43:Disorder {name:'PossessionTranceDisorder'})
ON CREATE SET
  d43.canonical_name = 'PossessionTranceDisorder',
  d43.official_name = 'Possession trance disorder',
  d43.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d43.icd11_code = '6B63',
  d43.icd11_release = '2026-01',
  d43.icd11_baseline_release = '2024-01',
  d43.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d43.dsm5_tr_relationship = 'NO_DIRECT_EQUIVALENT',
  d43.classification_status = 'ESTABLISHED_DISORDER',
  d43.count_as_primary_disorder = true,
  d43.audit_row = 43,
  d43.verification_status = 'VERIFIED',
  d43.verification_date = date('2026-09-05'),
  d43.date_added = date();

//  44. DissociativeIdentityDisorder  [ICD-11 6B64]  status=ESTABLISHED_DISORDER
MERGE (d44:Disorder {name:'DissociativeIdentityDisorder'})
ON CREATE SET
  d44.canonical_name = 'DissociativeIdentityDisorder',
  d44.official_name = 'Dissociative identity disorder',
  d44.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d44.icd11_code = '6B64',
  d44.icd11_release = '2026-01',
  d44.icd11_baseline_release = '2024-01',
  d44.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d44.dsm5_tr_relationship = 'EXACT',
  d44.classification_status = 'ESTABLISHED_DISORDER',
  d44.count_as_primary_disorder = true,
  d44.audit_row = 44,
  d44.verification_status = 'VERIFIED',
  d44.verification_date = date('2026-09-05'),
  d44.date_added = date();

//  45. PartialDissociativeIdentityDisorder  [ICD-11 6B65]  status=ESTABLISHED_DISORDER
MERGE (d45:Disorder {name:'PartialDissociativeIdentityDisorder'})
ON CREATE SET
  d45.canonical_name = 'PartialDissociativeIdentityDisorder',
  d45.official_name = 'Partial dissociative identity disorder',
  d45.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d45.icd11_code = '6B65',
  d45.icd11_release = '2026-01',
  d45.icd11_baseline_release = '2024-01',
  d45.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d45.dsm5_tr_relationship = 'NO_DIRECT_EQUIVALENT',
  d45.classification_status = 'ESTABLISHED_DISORDER',
  d45.count_as_primary_disorder = true,
  d45.audit_row = 45,
  d45.verification_status = 'VERIFIED',
  d45.verification_date = date('2026-09-05'),
  d45.date_added = date();

//  46. DepersonalizationDerealizationDisorder  [ICD-11 6B66]  status=ESTABLISHED_DISORDER
MERGE (d46:Disorder {name:'DepersonalizationDerealizationDisorder'})
ON CREATE SET
  d46.canonical_name = 'DepersonalizationDerealizationDisorder',
  d46.official_name = 'Depersonalization-derealization disorder',
  d46.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d46.icd11_code = '6B66',
  d46.icd11_release = '2026-01',
  d46.icd11_baseline_release = '2024-01',
  d46.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d46.dsm5_tr_relationship = 'EXACT',
  d46.classification_status = 'ESTABLISHED_DISORDER',
  d46.count_as_primary_disorder = true,
  d46.audit_row = 46,
  d46.verification_status = 'VERIFIED',
  d46.verification_date = date('2026-09-05'),
  d46.date_added = date();

// ---- Feeding & eating disorders (6B8x) ----
//  47. AnorexiaNervosa  [ICD-11 6B80]  status=ESTABLISHED_DISORDER
MERGE (d47:Disorder {name:'AnorexiaNervosa'})
ON CREATE SET
  d47.canonical_name = 'AnorexiaNervosa',
  d47.official_name = 'Anorexia Nervosa',
  d47.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d47.icd11_code = '6B80',
  d47.icd11_release = '2026-01',
  d47.icd11_baseline_release = '2024-01',
  d47.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d47.dsm5_tr_relationship = 'EXACT',
  d47.classification_status = 'ESTABLISHED_DISORDER',
  d47.count_as_primary_disorder = true,
  d47.audit_row = 47,
  d47.verification_status = 'VERIFIED',
  d47.verification_date = date('2026-09-05'),
  d47.date_added = date();

//  48. BulimiaNervosa  [ICD-11 6B81]  status=ESTABLISHED_DISORDER
MERGE (d48:Disorder {name:'BulimiaNervosa'})
ON CREATE SET
  d48.canonical_name = 'BulimiaNervosa',
  d48.official_name = 'Bulimia Nervosa',
  d48.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d48.icd11_code = '6B81',
  d48.icd11_release = '2026-01',
  d48.icd11_baseline_release = '2024-01',
  d48.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d48.dsm5_tr_relationship = 'EXACT',
  d48.classification_status = 'ESTABLISHED_DISORDER',
  d48.count_as_primary_disorder = true,
  d48.audit_row = 48,
  d48.verification_status = 'VERIFIED',
  d48.verification_date = date('2026-09-05'),
  d48.date_added = date();

//  49. BingeEatingDisorder  [ICD-11 6B82]  status=ESTABLISHED_DISORDER
MERGE (d49:Disorder {name:'BingeEatingDisorder'})
ON CREATE SET
  d49.canonical_name = 'BingeEatingDisorder',
  d49.official_name = 'Binge eating disorder',
  d49.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d49.icd11_code = '6B82',
  d49.icd11_release = '2026-01',
  d49.icd11_baseline_release = '2024-01',
  d49.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d49.dsm5_tr_relationship = 'EXACT',
  d49.classification_status = 'ESTABLISHED_DISORDER',
  d49.count_as_primary_disorder = true,
  d49.audit_row = 49,
  d49.verification_status = 'VERIFIED',
  d49.verification_date = date('2026-09-05'),
  d49.date_added = date();

//  50. AvoidantRestrictiveFoodIntakeDisorder  [ICD-11 6B83]  status=ESTABLISHED_DISORDER
MERGE (d50:Disorder {name:'AvoidantRestrictiveFoodIntakeDisorder'})
ON CREATE SET
  d50.canonical_name = 'AvoidantRestrictiveFoodIntakeDisorder',
  d50.official_name = 'Avoidant-restrictive food intake disorder',
  d50.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d50.icd11_code = '6B83',
  d50.icd11_release = '2026-01',
  d50.icd11_baseline_release = '2024-01',
  d50.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d50.dsm5_tr_relationship = 'EXACT',
  d50.classification_status = 'ESTABLISHED_DISORDER',
  d50.count_as_primary_disorder = true,
  d50.audit_row = 50,
  d50.verification_status = 'VERIFIED',
  d50.verification_date = date('2026-09-05'),
  d50.date_added = date();

//  51. Pica  [ICD-11 6B84]  status=ESTABLISHED_DISORDER
MERGE (d51:Disorder {name:'Pica'})
ON CREATE SET
  d51.canonical_name = 'Pica',
  d51.official_name = 'Pica',
  d51.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d51.icd11_code = '6B84',
  d51.icd11_release = '2026-01',
  d51.icd11_baseline_release = '2024-01',
  d51.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d51.dsm5_tr_relationship = 'EXACT',
  d51.classification_status = 'ESTABLISHED_DISORDER',
  d51.count_as_primary_disorder = true,
  d51.audit_row = 51,
  d51.verification_status = 'VERIFIED',
  d51.verification_date = date('2026-09-05'),
  d51.date_added = date();

//  52. RuminationRegurgitationDisorder  [ICD-11 6B85]  status=ESTABLISHED_DISORDER
MERGE (d52:Disorder {name:'RuminationRegurgitationDisorder'})
ON CREATE SET
  d52.canonical_name = 'RuminationRegurgitationDisorder',
  d52.official_name = 'Rumination-regurgitation disorder',
  d52.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d52.icd11_code = '6B85',
  d52.icd11_release = '2026-01',
  d52.icd11_baseline_release = '2024-01',
  d52.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d52.dsm5_tr_relationship = 'EXACT',
  d52.classification_status = 'ESTABLISHED_DISORDER',
  d52.count_as_primary_disorder = true,
  d52.audit_row = 52,
  d52.verification_status = 'VERIFIED',
  d52.verification_date = date('2026-09-05'),
  d52.date_added = date();

// ---- Elimination disorders (6C0x) ----
//  53. Enuresis  [ICD-11 6C00]  status=ESTABLISHED_DISORDER
MERGE (d53:Disorder {name:'Enuresis'})
ON CREATE SET
  d53.canonical_name = 'Enuresis',
  d53.official_name = 'Enuresis',
  d53.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d53.icd11_code = '6C00',
  d53.icd11_release = '2026-01',
  d53.icd11_baseline_release = '2024-01',
  d53.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d53.dsm5_tr_relationship = 'EXACT',
  d53.classification_status = 'ESTABLISHED_DISORDER',
  d53.count_as_primary_disorder = true,
  d53.audit_row = 53,
  d53.verification_status = 'VERIFIED',
  d53.verification_date = date('2026-09-05'),
  d53.date_added = date();

//  54. Encopresis  [ICD-11 6C01]  status=ESTABLISHED_DISORDER
MERGE (d54:Disorder {name:'Encopresis'})
ON CREATE SET
  d54.canonical_name = 'Encopresis',
  d54.official_name = 'Encopresis',
  d54.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d54.icd11_code = '6C01',
  d54.icd11_release = '2026-01',
  d54.icd11_baseline_release = '2024-01',
  d54.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d54.dsm5_tr_relationship = 'EXACT',
  d54.classification_status = 'ESTABLISHED_DISORDER',
  d54.count_as_primary_disorder = true,
  d54.audit_row = 54,
  d54.verification_status = 'VERIFIED',
  d54.verification_date = date('2026-09-05'),
  d54.date_added = date();

// ---- Disorders of bodily distress / bodily experience (6C2x) ----
//  55. BodilyDistressDisorder  [ICD-11 6C20]  status=ESTABLISHED_DISORDER
MERGE (d55:Disorder {name:'BodilyDistressDisorder'})
ON CREATE SET
  d55.canonical_name = 'BodilyDistressDisorder',
  d55.official_name = 'Bodily distress disorder',
  d55.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d55.icd11_code = '6C20',
  d55.icd11_release = '2026-01',
  d55.icd11_baseline_release = '2024-01',
  d55.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d55.dsm5_tr_relationship = 'CLOSE',
  d55.classification_status = 'ESTABLISHED_DISORDER',
  d55.count_as_primary_disorder = true,
  d55.audit_row = 55,
  d55.verification_status = 'VERIFIED',
  d55.verification_date = date('2026-09-05'),
  d55.date_added = date();

//  56. BodyIntegrityDysphoria  [ICD-11 6C21]  status=ESTABLISHED_DISORDER
MERGE (d56:Disorder {name:'BodyIntegrityDysphoria'})
ON CREATE SET
  d56.canonical_name = 'BodyIntegrityDysphoria',
  d56.official_name = 'Body integrity dysphoria',
  d56.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d56.icd11_code = '6C21',
  d56.icd11_release = '2026-01',
  d56.icd11_baseline_release = '2024-01',
  d56.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d56.dsm5_tr_relationship = 'NO_DIRECT_EQUIVALENT',
  d56.classification_status = 'ESTABLISHED_DISORDER',
  d56.count_as_primary_disorder = true,
  d56.audit_row = 56,
  d56.verification_status = 'VERIFIED',
  d56.verification_date = date('2026-09-05'),
  d56.date_added = date();

// ---- Disorders due to substance use — dependence (6C4x) ----
//  57. AlcoholDependence  [ICD-11 6C40.2]  status=ESTABLISHED_DISORDER
MERGE (d57:Disorder {name:'AlcoholDependence'})
ON CREATE SET
  d57.canonical_name = 'AlcoholDependence',
  d57.official_name = 'Alcohol dependence',
  d57.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d57.icd11_code = '6C40.2',
  d57.icd11_release = '2026-01',
  d57.icd11_baseline_release = '2024-01',
  d57.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d57.dsm5_tr_relationship = 'CLOSE',
  d57.classification_status = 'ESTABLISHED_DISORDER',
  d57.count_as_primary_disorder = true,
  d57.audit_row = 57,
  d57.verification_status = 'VERIFIED',
  d57.verification_date = date('2026-09-05'),
  d57.date_added = date();

//  58. CannabisDependence  [ICD-11 6C41.2]  status=ESTABLISHED_DISORDER
MERGE (d58:Disorder {name:'CannabisDependence'})
ON CREATE SET
  d58.canonical_name = 'CannabisDependence',
  d58.official_name = 'Disorders due to use of cannabis',
  d58.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d58.icd11_code = '6C41.2',
  d58.icd11_release = '2026-01',
  d58.icd11_baseline_release = '2024-01',
  d58.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d58.dsm5_tr_relationship = 'CLOSE',
  d58.classification_status = 'ESTABLISHED_DISORDER',
  d58.count_as_primary_disorder = true,
  d58.audit_row = 58,
  d58.verification_status = 'VERIFIED',
  d58.verification_date = date('2026-09-05'),
  d58.date_added = date();

//  59. OpioidDependence  [ICD-11 6C43.2]  status=ESTABLISHED_DISORDER
MERGE (d59:Disorder {name:'OpioidDependence'})
ON CREATE SET
  d59.canonical_name = 'OpioidDependence',
  d59.official_name = 'Opioid dependence',
  d59.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d59.icd11_code = '6C43.2',
  d59.icd11_release = '2026-01',
  d59.icd11_baseline_release = '2024-01',
  d59.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d59.dsm5_tr_relationship = 'CLOSE',
  d59.classification_status = 'ESTABLISHED_DISORDER',
  d59.count_as_primary_disorder = true,
  d59.audit_row = 59,
  d59.verification_status = 'VERIFIED',
  d59.verification_date = date('2026-09-05'),
  d59.date_added = date();

//  60. SedativeHypnoticAnxiolyticDependence  [ICD-11 6C44.2]  status=ESTABLISHED_DISORDER
MERGE (d60:Disorder {name:'SedativeHypnoticAnxiolyticDependence'})
ON CREATE SET
  d60.canonical_name = 'SedativeHypnoticAnxiolyticDependence',
  d60.official_name = 'Sedative, hypnotic or anxiolytic dependence',
  d60.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d60.icd11_code = '6C44.2',
  d60.icd11_release = '2026-01',
  d60.icd11_baseline_release = '2024-01',
  d60.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d60.dsm5_tr_relationship = 'CLOSE',
  d60.classification_status = 'ESTABLISHED_DISORDER',
  d60.count_as_primary_disorder = true,
  d60.audit_row = 60,
  d60.verification_status = 'VERIFIED',
  d60.verification_date = date('2026-09-05'),
  d60.date_added = date();

//  61. CocaineDependence  [ICD-11 6C45.2]  status=ESTABLISHED_DISORDER
MERGE (d61:Disorder {name:'CocaineDependence'})
ON CREATE SET
  d61.canonical_name = 'CocaineDependence',
  d61.official_name = 'Cocaine dependence',
  d61.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d61.icd11_code = '6C45.2',
  d61.icd11_release = '2026-01',
  d61.icd11_baseline_release = '2024-01',
  d61.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d61.dsm5_tr_relationship = 'CLOSE',
  d61.classification_status = 'ESTABLISHED_DISORDER',
  d61.count_as_primary_disorder = true,
  d61.audit_row = 61,
  d61.verification_status = 'VERIFIED',
  d61.verification_date = date('2026-09-05'),
  d61.date_added = date();

//  62. StimulantDependence  [ICD-11 6C46.2]  status=ESTABLISHED_DISORDER
MERGE (d62:Disorder {name:'StimulantDependence'})
ON CREATE SET
  d62.canonical_name = 'StimulantDependence',
  d62.official_name = 'Stimulant dependence',
  d62.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d62.icd11_code = '6C46.2',
  d62.icd11_release = '2026-01',
  d62.icd11_baseline_release = '2024-01',
  d62.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d62.dsm5_tr_relationship = 'CLOSE',
  d62.classification_status = 'ESTABLISHED_DISORDER',
  d62.count_as_primary_disorder = true,
  d62.audit_row = 62,
  d62.verification_status = 'VERIFIED',
  d62.verification_date = date('2026-09-05'),
  d62.date_added = date();

//  63. NicotineDependence  [ICD-11 6C4A.2]  status=ESTABLISHED_DISORDER
MERGE (d63:Disorder {name:'NicotineDependence'})
ON CREATE SET
  d63.canonical_name = 'NicotineDependence',
  d63.official_name = 'Nicotine dependence',
  d63.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d63.icd11_code = '6C4A.2',
  d63.icd11_release = '2026-01',
  d63.icd11_baseline_release = '2024-01',
  d63.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d63.dsm5_tr_relationship = 'CLOSE',
  d63.classification_status = 'ESTABLISHED_DISORDER',
  d63.count_as_primary_disorder = true,
  d63.audit_row = 63,
  d63.verification_status = 'VERIFIED',
  d63.verification_date = date('2026-09-05'),
  d63.date_added = date();

//  64. HallucinogenDependence  [ICD-11 6C49.2]  status=ESTABLISHED_DISORDER
MERGE (d64:Disorder {name:'HallucinogenDependence'})
ON CREATE SET
  d64.canonical_name = 'HallucinogenDependence',
  d64.official_name = 'Hallucinogen dependence',
  d64.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d64.icd11_code = '6C49.2',
  d64.icd11_release = '2026-01',
  d64.icd11_baseline_release = '2024-01',
  d64.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d64.dsm5_tr_relationship = 'CLOSE',
  d64.classification_status = 'ESTABLISHED_DISORDER',
  d64.count_as_primary_disorder = true,
  d64.audit_row = 64,
  d64.verification_status = 'VERIFIED',
  d64.verification_date = date('2026-09-05'),
  d64.date_added = date();

// ---- Disorders due to addictive behaviours (6C5x) ----
//  65. GamblingDisorder  [ICD-11 6C50]  status=ESTABLISHED_DISORDER
MERGE (d65:Disorder {name:'GamblingDisorder'})
ON CREATE SET
  d65.canonical_name = 'GamblingDisorder',
  d65.official_name = 'Gambling disorder',
  d65.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d65.icd11_code = '6C50',
  d65.icd11_release = '2026-01',
  d65.icd11_baseline_release = '2024-01',
  d65.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d65.dsm5_tr_relationship = 'EXACT',
  d65.classification_status = 'ESTABLISHED_DISORDER',
  d65.count_as_primary_disorder = true,
  d65.audit_row = 65,
  d65.verification_status = 'VERIFIED',
  d65.verification_date = date('2026-09-05'),
  d65.date_added = date();

//  66. GamingDisorder  [ICD-11 6C51]  status=ESTABLISHED_DISORDER
MERGE (d66:Disorder {name:'GamingDisorder'})
ON CREATE SET
  d66.canonical_name = 'GamingDisorder',
  d66.official_name = 'Gaming disorder',
  d66.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d66.icd11_code = '6C51',
  d66.icd11_release = '2026-01',
  d66.icd11_baseline_release = '2024-01',
  d66.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d66.dsm5_tr_relationship = 'NO_DIRECT_EQUIVALENT',
  d66.classification_status = 'ESTABLISHED_DISORDER',
  d66.count_as_primary_disorder = true,
  d66.audit_row = 66,
  d66.verification_status = 'VERIFIED',
  d66.verification_date = date('2026-09-05'),
  d66.date_added = date();

// ---- Impulse control disorders (6C7x) ----
//  67. Pyromania  [ICD-11 6C70]  status=ESTABLISHED_DISORDER
MERGE (d67:Disorder {name:'Pyromania'})
ON CREATE SET
  d67.canonical_name = 'Pyromania',
  d67.official_name = 'Pyromania',
  d67.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d67.icd11_code = '6C70',
  d67.icd11_release = '2026-01',
  d67.icd11_baseline_release = '2024-01',
  d67.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d67.dsm5_tr_relationship = 'EXACT',
  d67.classification_status = 'ESTABLISHED_DISORDER',
  d67.count_as_primary_disorder = true,
  d67.audit_row = 67,
  d67.verification_status = 'VERIFIED',
  d67.verification_date = date('2026-09-05'),
  d67.date_added = date();

//  68. Kleptomania  [ICD-11 6C71]  status=ESTABLISHED_DISORDER
MERGE (d68:Disorder {name:'Kleptomania'})
ON CREATE SET
  d68.canonical_name = 'Kleptomania',
  d68.official_name = 'Kleptomania',
  d68.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d68.icd11_code = '6C71',
  d68.icd11_release = '2026-01',
  d68.icd11_baseline_release = '2024-01',
  d68.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d68.dsm5_tr_relationship = 'EXACT',
  d68.classification_status = 'ESTABLISHED_DISORDER',
  d68.count_as_primary_disorder = true,
  d68.audit_row = 68,
  d68.verification_status = 'VERIFIED',
  d68.verification_date = date('2026-09-05'),
  d68.date_added = date();

//  69. CompulsiveSexualBehaviourDisorder  [ICD-11 6C72]  status=ESTABLISHED_DISORDER
MERGE (d69:Disorder {name:'CompulsiveSexualBehaviourDisorder'})
ON CREATE SET
  d69.canonical_name = 'CompulsiveSexualBehaviourDisorder',
  d69.official_name = 'Compulsive sexual behaviour disorder',
  d69.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d69.icd11_code = '6C72',
  d69.icd11_release = '2026-01',
  d69.icd11_baseline_release = '2024-01',
  d69.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d69.dsm5_tr_relationship = 'NO_DIRECT_EQUIVALENT',
  d69.classification_status = 'ESTABLISHED_DISORDER',
  d69.count_as_primary_disorder = true,
  d69.audit_row = 69,
  d69.verification_status = 'VERIFIED',
  d69.verification_date = date('2026-09-05'),
  d69.date_added = date();

//  70. IntermittentExplosiveDisorder  [ICD-11 6C73]  status=ESTABLISHED_DISORDER
MERGE (d70:Disorder {name:'IntermittentExplosiveDisorder'})
ON CREATE SET
  d70.canonical_name = 'IntermittentExplosiveDisorder',
  d70.official_name = 'Intermittent explosive disorder',
  d70.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d70.icd11_code = '6C73',
  d70.icd11_release = '2026-01',
  d70.icd11_baseline_release = '2024-01',
  d70.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d70.dsm5_tr_relationship = 'EXACT',
  d70.classification_status = 'ESTABLISHED_DISORDER',
  d70.count_as_primary_disorder = true,
  d70.audit_row = 70,
  d70.verification_status = 'VERIFIED',
  d70.verification_date = date('2026-09-05'),
  d70.date_added = date();

// ---- Disruptive behaviour & dissocial disorders (6C9x) ----
//  71. OppositionalDefiantDisorder  [ICD-11 6C90]  status=ESTABLISHED_DISORDER
MERGE (d71:Disorder {name:'OppositionalDefiantDisorder'})
ON CREATE SET
  d71.canonical_name = 'OppositionalDefiantDisorder',
  d71.official_name = 'Oppositional defiant disorder',
  d71.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d71.icd11_code = '6C90',
  d71.icd11_release = '2026-01',
  d71.icd11_baseline_release = '2024-01',
  d71.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d71.dsm5_tr_relationship = 'EXACT',
  d71.classification_status = 'ESTABLISHED_DISORDER',
  d71.count_as_primary_disorder = true,
  d71.audit_row = 71,
  d71.verification_status = 'VERIFIED',
  d71.verification_date = date('2026-09-05'),
  d71.date_added = date();

//  72. ConductDissocialDisorder  [ICD-11 6C91]  status=ESTABLISHED_DISORDER
MERGE (d72:Disorder {name:'ConductDissocialDisorder'})
ON CREATE SET
  d72.canonical_name = 'ConductDissocialDisorder',
  d72.official_name = 'Conduct-dissocial disorder',
  d72.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d72.icd11_code = '6C91',
  d72.icd11_release = '2026-01',
  d72.icd11_baseline_release = '2024-01',
  d72.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d72.dsm5_tr_relationship = 'EXACT',
  d72.classification_status = 'ESTABLISHED_DISORDER',
  d72.count_as_primary_disorder = true,
  d72.audit_row = 72,
  d72.verification_status = 'VERIFIED',
  d72.verification_date = date('2026-09-05'),
  d72.date_added = date();

// ---- Personality disorders (6D10) ----
//  73. PersonalityDisorder  [ICD-11 6D10]  status=ESTABLISHED_DISORDER
MERGE (d73:Disorder {name:'PersonalityDisorder'})
ON CREATE SET
  d73.canonical_name = 'PersonalityDisorder',
  d73.official_name = 'Personality disorder',
  d73.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d73.icd11_code = '6D10',
  d73.icd11_release = '2026-01',
  d73.icd11_baseline_release = '2024-01',
  d73.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d73.dsm5_tr_relationship = 'EXACT',
  d73.classification_status = 'ESTABLISHED_DISORDER',
  d73.count_as_primary_disorder = true,
  d73.audit_row = 73,
  d73.verification_status = 'VERIFIED',
  d73.verification_date = date('2026-09-05'),
  d73.date_added = date();

// ---- Paraphilic disorders (6D3x) ----
//  86. ExhibitionisticDisorder  [ICD-11 6D30]  status=ESTABLISHED_DISORDER
MERGE (d86:Disorder {name:'ExhibitionisticDisorder'})
ON CREATE SET
  d86.canonical_name = 'ExhibitionisticDisorder',
  d86.official_name = 'Exhibitionistic disorder',
  d86.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d86.icd11_code = '6D30',
  d86.icd11_release = '2026-01',
  d86.icd11_baseline_release = '2024-01',
  d86.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d86.dsm5_tr_relationship = 'EXACT',
  d86.classification_status = 'ESTABLISHED_DISORDER',
  d86.count_as_primary_disorder = true,
  d86.audit_row = 86,
  d86.verification_status = 'VERIFIED',
  d86.verification_date = date('2026-09-05'),
  d86.date_added = date();

//  87. VoyeuristicDisorder  [ICD-11 6D31]  status=ESTABLISHED_DISORDER
MERGE (d87:Disorder {name:'VoyeuristicDisorder'})
ON CREATE SET
  d87.canonical_name = 'VoyeuristicDisorder',
  d87.official_name = 'Voyeuristic disorder',
  d87.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d87.icd11_code = '6D31',
  d87.icd11_release = '2026-01',
  d87.icd11_baseline_release = '2024-01',
  d87.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d87.dsm5_tr_relationship = 'EXACT',
  d87.classification_status = 'ESTABLISHED_DISORDER',
  d87.count_as_primary_disorder = true,
  d87.audit_row = 87,
  d87.verification_status = 'VERIFIED',
  d87.verification_date = date('2026-09-05'),
  d87.date_added = date();

//  88. PedophilicDisorder  [ICD-11 6D32]  status=ESTABLISHED_DISORDER
MERGE (d88:Disorder {name:'PedophilicDisorder'})
ON CREATE SET
  d88.canonical_name = 'PedophilicDisorder',
  d88.official_name = 'Pedophilic disorder',
  d88.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d88.icd11_code = '6D32',
  d88.icd11_release = '2026-01',
  d88.icd11_baseline_release = '2024-01',
  d88.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d88.dsm5_tr_relationship = 'EXACT',
  d88.classification_status = 'ESTABLISHED_DISORDER',
  d88.count_as_primary_disorder = true,
  d88.audit_row = 88,
  d88.verification_status = 'VERIFIED',
  d88.verification_date = date('2026-09-05'),
  d88.date_added = date();

// ---- Paraphilic disorders — coercive sexual sadism (6D33) ----
//  74. CoerciveSexualSadismDisorder  [ICD-11 6D33]  status=ESTABLISHED_DISORDER
MERGE (d74:Disorder {name:'CoerciveSexualSadismDisorder'})
ON CREATE SET
  d74.canonical_name = 'CoerciveSexualSadismDisorder',
  d74.official_name = 'Coercive sexual sadism disorder',
  d74.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d74.icd11_code = '6D33',
  d74.icd11_release = '2026-01',
  d74.icd11_baseline_release = '2024-01',
  d74.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d74.dsm5_tr_relationship = 'CLOSE',
  d74.classification_status = 'ESTABLISHED_DISORDER',
  d74.count_as_primary_disorder = true,
  d74.audit_row = 74,
  d74.verification_status = 'VERIFIED',
  d74.verification_date = date('2026-09-05'),
  d74.date_added = date();

// ---- Factitious disorders (6D5x) ----
//  75. FactitiousDisorderImposedOnSelf  [ICD-11 6D50]  status=ESTABLISHED_DISORDER
MERGE (d75:Disorder {name:'FactitiousDisorderImposedOnSelf'})
ON CREATE SET
  d75.canonical_name = 'FactitiousDisorderImposedOnSelf',
  d75.official_name = 'Factitious disorder imposed on self',
  d75.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d75.icd11_code = '6D50',
  d75.icd11_release = '2026-01',
  d75.icd11_baseline_release = '2024-01',
  d75.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d75.dsm5_tr_relationship = 'EXACT',
  d75.classification_status = 'ESTABLISHED_DISORDER',
  d75.count_as_primary_disorder = true,
  d75.audit_row = 75,
  d75.verification_status = 'VERIFIED',
  d75.verification_date = date('2026-09-05'),
  d75.date_added = date();

//  76. FactitiousDisorderImposedOnAnother  [ICD-11 6D51]  status=ESTABLISHED_DISORDER
MERGE (d76:Disorder {name:'FactitiousDisorderImposedOnAnother'})
ON CREATE SET
  d76.canonical_name = 'FactitiousDisorderImposedOnAnother',
  d76.official_name = 'Factitious disorder imposed on another',
  d76.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d76.icd11_code = '6D51',
  d76.icd11_release = '2026-01',
  d76.icd11_baseline_release = '2024-01',
  d76.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d76.dsm5_tr_relationship = 'EXACT',
  d76.classification_status = 'ESTABLISHED_DISORDER',
  d76.count_as_primary_disorder = true,
  d76.audit_row = 76,
  d76.verification_status = 'VERIFIED',
  d76.verification_date = date('2026-09-05'),
  d76.date_added = date();

// ---- Neurocognitive disorders — delirium/mild NCD/amnestic (6D7x) ----
//  79. Delirium  [ICD-11 6D70]  status=ESTABLISHED_DISORDER
MERGE (d79:Disorder {name:'Delirium'})
ON CREATE SET
  d79.canonical_name = 'Delirium',
  d79.official_name = 'Delirium',
  d79.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d79.icd11_code = '6D70',
  d79.icd11_release = '2026-01',
  d79.icd11_baseline_release = '2024-01',
  d79.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d79.dsm5_tr_relationship = 'EXACT',
  d79.classification_status = 'ESTABLISHED_DISORDER',
  d79.count_as_primary_disorder = true,
  d79.audit_row = 79,
  d79.verification_status = 'VERIFIED',
  d79.verification_date = date('2026-09-05'),
  d79.date_added = date();

//  80. MildNeurocognitiveDisorder  [ICD-11 6D71]  status=ESTABLISHED_DISORDER
MERGE (d80:Disorder {name:'MildNeurocognitiveDisorder'})
ON CREATE SET
  d80.canonical_name = 'MildNeurocognitiveDisorder',
  d80.official_name = 'Mild neurocognitive disorder',
  d80.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d80.icd11_code = '6D71',
  d80.icd11_release = '2026-01',
  d80.icd11_baseline_release = '2024-01',
  d80.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d80.dsm5_tr_relationship = 'EXACT',
  d80.classification_status = 'ESTABLISHED_DISORDER',
  d80.count_as_primary_disorder = true,
  d80.audit_row = 80,
  d80.verification_status = 'VERIFIED',
  d80.verification_date = date('2026-09-05'),
  d80.date_added = date();

//  81. AmnesticDisorder  [ICD-11 6D72]  status=ESTABLISHED_DISORDER
MERGE (d81:Disorder {name:'AmnesticDisorder'})
ON CREATE SET
  d81.canonical_name = 'AmnesticDisorder',
  d81.official_name = 'Amnestic disorder',
  d81.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d81.icd11_code = '6D72',
  d81.icd11_release = '2026-01',
  d81.icd11_baseline_release = '2024-01',
  d81.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d81.dsm5_tr_relationship = 'EXACT',
  d81.classification_status = 'ESTABLISHED_DISORDER',
  d81.count_as_primary_disorder = true,
  d81.audit_row = 81,
  d81.verification_status = 'VERIFIED',
  d81.verification_date = date('2026-09-05'),
  d81.date_added = date();

// ---- Neurocognitive disorders — dementias (6D8x) ----
//  82. DementiaAlzheimerDisease  [ICD-11 6D80]  status=ESTABLISHED_DISORDER
MERGE (d82:Disorder {name:'DementiaAlzheimerDisease'})
ON CREATE SET
  d82.canonical_name = 'DementiaAlzheimerDisease',
  d82.official_name = 'Dementia due to Alzheimer disease',
  d82.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d82.icd11_code = '6D80',
  d82.icd11_release = '2026-01',
  d82.icd11_baseline_release = '2024-01',
  d82.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d82.dsm5_tr_relationship = 'EXACT',
  d82.classification_status = 'ESTABLISHED_DISORDER',
  d82.count_as_primary_disorder = true,
  d82.audit_row = 82,
  d82.verification_status = 'VERIFIED',
  d82.verification_date = date('2026-09-05'),
  d82.date_added = date();

//  83. DementiaCerebrovascularDisease  [ICD-11 6D81]  status=ESTABLISHED_DISORDER
MERGE (d83:Disorder {name:'DementiaCerebrovascularDisease'})
ON CREATE SET
  d83.canonical_name = 'DementiaCerebrovascularDisease',
  d83.official_name = 'Dementia due to cerebrovascular disease',
  d83.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d83.icd11_code = '6D81',
  d83.icd11_release = '2026-01',
  d83.icd11_baseline_release = '2024-01',
  d83.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d83.dsm5_tr_relationship = 'EXACT',
  d83.classification_status = 'ESTABLISHED_DISORDER',
  d83.count_as_primary_disorder = true,
  d83.audit_row = 83,
  d83.verification_status = 'VERIFIED',
  d83.verification_date = date('2026-09-05'),
  d83.date_added = date();

//  84. DementiaLevyBodyDisease  [ICD-11 6D82]  status=ESTABLISHED_DISORDER
MERGE (d84:Disorder {name:'DementiaLevyBodyDisease'})
ON CREATE SET
  d84.canonical_name = 'DementiaLevyBodyDisease',
  d84.official_name = 'Dementia due to Lewy body disease',
  d84.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d84.icd11_code = '6D82',
  d84.icd11_release = '2026-01',
  d84.icd11_baseline_release = '2024-01',
  d84.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d84.dsm5_tr_relationship = 'EXACT',
  d84.classification_status = 'ESTABLISHED_DISORDER',
  d84.count_as_primary_disorder = true,
  d84.audit_row = 84,
  d84.verification_status = 'VERIFIED',
  d84.verification_date = date('2026-09-05'),
  d84.date_added = date();

//  85. FrontotemporalDementia  [ICD-11 6D83]  status=ESTABLISHED_DISORDER
MERGE (d85:Disorder {name:'FrontotemporalDementia'})
ON CREATE SET
  d85.canonical_name = 'FrontotemporalDementia',
  d85.official_name = 'Frontotemporal dementia',
  d85.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d85.icd11_code = '6D83',
  d85.icd11_release = '2026-01',
  d85.icd11_baseline_release = '2024-01',
  d85.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d85.dsm5_tr_relationship = 'EXACT',
  d85.classification_status = 'ESTABLISHED_DISORDER',
  d85.count_as_primary_disorder = true,
  d85.audit_row = 85,
  d85.verification_status = 'VERIFIED',
  d85.verification_date = date('2026-09-05'),
  d85.date_added = date();

// ---- Peripartum mental disorders — CONTEXTUAL (6E20/6E21) ----
//  77. PeripartumMentalDisorderWithoutPsychosis  [ICD-11 6E20]  status=CONTEXTUAL_DIAGNOSTIC_CATEGORY
MERGE (d77:Disorder {name:'PeripartumMentalDisorderWithoutPsychosis'})
ON CREATE SET
  d77.canonical_name = 'PeripartumMentalDisorderWithoutPsychosis',
  d77.official_name = 'Mental or behavioural disorders associated with pregnancy, childbirth or the puerperium, without psychotic symptoms',
  d77.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d77.icd11_code = '6E20',
  d77.icd11_release = '2026-01',
  d77.icd11_baseline_release = '2024-01',
  d77.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d77.dsm5_tr_relationship = 'CLOSE',
  d77.classification_status = 'CONTEXTUAL_DIAGNOSTIC_CATEGORY',
  d77.count_as_primary_disorder = true,
  d77.audit_row = 77,
  d77.verification_status = 'VERIFIED',
  d77.verification_date = date('2026-09-05'),
  d77.date_added = date();

//  78. PeripartumMentalDisorderWithPsychosis  [ICD-11 6E21]  status=CONTEXTUAL_DIAGNOSTIC_CATEGORY
MERGE (d78:Disorder {name:'PeripartumMentalDisorderWithPsychosis'})
ON CREATE SET
  d78.canonical_name = 'PeripartumMentalDisorderWithPsychosis',
  d78.official_name = 'Mental or behavioural disorders associated with pregnancy, childbirth or the puerperium, with psychotic symptoms',
  d78.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d78.icd11_code = '6E21',
  d78.icd11_release = '2026-01',
  d78.icd11_baseline_release = '2024-01',
  d78.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d78.dsm5_tr_relationship = 'CLOSE',
  d78.classification_status = 'CONTEXTUAL_DIAGNOSTIC_CATEGORY',
  d78.count_as_primary_disorder = true,
  d78.audit_row = 78,
  d78.verification_status = 'VERIFIED',
  d78.verification_date = date('2026-09-05'),
  d78.date_added = date();

// ---- CROSS-CHAPTER: Tourette syndrome (Ch08, 8A05.00) ----
//  90. TouretteSyndrome  [ICD-11 8A05.00]  status=CROSS_CHAPTER_ESTABLISHED_DISORDER
MERGE (d90:Disorder {name:'TouretteSyndrome'})
ON CREATE SET
  d90.canonical_name = 'TouretteSyndrome',
  d90.official_name = 'Tourette syndrome',
  d90.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d90.icd11_code = '8A05.00',
  d90.icd11_release = '2026-01',
  d90.icd11_baseline_release = '2024-01',
  d90.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d90.dsm5_tr_relationship = 'EXACT',
  d90.classification_status = 'CROSS_CHAPTER_ESTABLISHED_DISORDER',
  d90.count_as_primary_disorder = true,
  d90.audit_row = 90,
  d90.verification_status = 'VERIFIED',
  d90.verification_date = date('2026-09-05'),
  d90.date_added = date();

// ---- CROSS-CHAPTER: Insomnia disorder (Ch07, 7A00) ----
//  91. InsomniaDisorder  [ICD-11 7A00]  status=CROSS_CHAPTER_ESTABLISHED_DISORDER
MERGE (d91:Disorder {name:'InsomniaDisorder'})
ON CREATE SET
  d91.canonical_name = 'InsomniaDisorder',
  d91.official_name = 'Insomnia',
  d91.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d91.icd11_code = '7A00',
  d91.icd11_release = '2026-01',
  d91.icd11_baseline_release = '2024-01',
  d91.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d91.dsm5_tr_relationship = 'EXACT',
  d91.classification_status = 'CROSS_CHAPTER_ESTABLISHED_DISORDER',
  d91.count_as_primary_disorder = true,
  d91.audit_row = 91,
  d91.verification_status = 'VERIFIED',
  d91.verification_date = date('2026-09-05'),
  d91.date_added = date();

// ---- CROSS-CHAPTER: Premenstrual dysphoric disorder (Ch16, GA34.41) ----
//  92. PremenstrualDysphoricDisorder  [ICD-11 GA34.41]  status=CROSS_CHAPTER_ESTABLISHED_DISORDER
MERGE (d92:Disorder {name:'PremenstrualDysphoricDisorder'})
ON CREATE SET
  d92.canonical_name = 'PremenstrualDysphoricDisorder',
  d92.official_name = 'Premenstrual dysphoric disorder',
  d92.classification_system = 'WHO ICD-11 / DSM-5-TR',
  d92.icd11_code = 'GA34.41',
  d92.icd11_release = '2026-01',
  d92.icd11_baseline_release = '2024-01',
  d92.source_url = 'https://icd.who.int/browse/2026-01/mms/en',
  d92.dsm5_tr_relationship = 'EXACT',
  d92.classification_status = 'CROSS_CHAPTER_ESTABLISHED_DISORDER',
  d92.count_as_primary_disorder = true,
  d92.audit_row = 92,
  d92.verification_status = 'VERIFIED',
  d92.verification_date = date('2026-09-05'),
  d92.date_added = date();

// ---- DSM-5-TR ONLY: Categorical personality disorders (no ICD-11 code) ----
//  93. NarcissisticPersonalityDisorder  [DSM-5-TR NONE]  status=DSM_ONLY
MERGE (d93:Disorder {name:'NarcissisticPersonalityDisorder'})
ON CREATE SET
  d93.canonical_name = 'NarcissisticPersonalityDisorder',
  d93.official_name = 'Narcissistic Personality Disorder',
  d93.classification_system = 'DSM-5-TR',
  d93.icd11_code = null,
  d93.source_url = 'https://www.psychiatry.org/psychiatrists/practice/dsm',
  d93.dsm5_tr_relationship = 'EXACT',
  d93.classification_status = 'DSM_ONLY',
  d93.count_as_primary_disorder = true,
  d93.audit_row = 93,
  d93.verification_status = 'VERIFIED',
  d93.verification_date = date('2026-09-05'),
  d93.date_added = date();

//  94. AntisocialPersonalityDisorder  [DSM-5-TR NONE]  status=DSM_ONLY
MERGE (d94:Disorder {name:'AntisocialPersonalityDisorder'})
ON CREATE SET
  d94.canonical_name = 'AntisocialPersonalityDisorder',
  d94.official_name = 'Antisocial Personality Disorder',
  d94.classification_system = 'DSM-5-TR',
  d94.icd11_code = null,
  d94.source_url = 'https://www.psychiatry.org/psychiatrists/practice/dsm',
  d94.dsm5_tr_relationship = 'EXACT',
  d94.classification_status = 'DSM_ONLY',
  d94.count_as_primary_disorder = true,
  d94.audit_row = 94,
  d94.verification_status = 'VERIFIED',
  d94.verification_date = date('2026-09-05'),
  d94.date_added = date();

//  95. AvoidantPersonalityDisorder  [DSM-5-TR NONE]  status=DSM_ONLY
MERGE (d95:Disorder {name:'AvoidantPersonalityDisorder'})
ON CREATE SET
  d95.canonical_name = 'AvoidantPersonalityDisorder',
  d95.official_name = 'Avoidant Personality Disorder',
  d95.classification_system = 'DSM-5-TR',
  d95.icd11_code = null,
  d95.source_url = 'https://www.psychiatry.org/psychiatrists/practice/dsm',
  d95.dsm5_tr_relationship = 'EXACT',
  d95.classification_status = 'DSM_ONLY',
  d95.count_as_primary_disorder = true,
  d95.audit_row = 95,
  d95.verification_status = 'VERIFIED',
  d95.verification_date = date('2026-09-05'),
  d95.date_added = date();

//  96. DependentPersonalityDisorder  [DSM-5-TR NONE]  status=DSM_ONLY
MERGE (d96:Disorder {name:'DependentPersonalityDisorder'})
ON CREATE SET
  d96.canonical_name = 'DependentPersonalityDisorder',
  d96.official_name = 'Dependent Personality Disorder',
  d96.classification_system = 'DSM-5-TR',
  d96.icd11_code = null,
  d96.source_url = 'https://www.psychiatry.org/psychiatrists/practice/dsm',
  d96.dsm5_tr_relationship = 'EXACT',
  d96.classification_status = 'DSM_ONLY',
  d96.count_as_primary_disorder = true,
  d96.audit_row = 96,
  d96.verification_status = 'VERIFIED',
  d96.verification_date = date('2026-09-05'),
  d96.date_added = date();

//  97. ObsessiveCompulsivePersonalityDisorder  [DSM-5-TR NONE]  status=DSM_ONLY
MERGE (d97:Disorder {name:'ObsessiveCompulsivePersonalityDisorder'})
ON CREATE SET
  d97.canonical_name = 'ObsessiveCompulsivePersonalityDisorder',
  d97.official_name = 'Obsessive-Compulsive Personality Disorder',
  d97.classification_system = 'DSM-5-TR',
  d97.icd11_code = null,
  d97.source_url = 'https://www.psychiatry.org/psychiatrists/practice/dsm',
  d97.dsm5_tr_relationship = 'EXACT',
  d97.classification_status = 'DSM_ONLY',
  d97.count_as_primary_disorder = true,
  d97.audit_row = 97,
  d97.verification_status = 'VERIFIED',
  d97.verification_date = date('2026-09-05'),
  d97.date_added = date();

//  98. SchizoidPersonalityDisorder  [DSM-5-TR NONE]  status=DSM_ONLY
MERGE (d98:Disorder {name:'SchizoidPersonalityDisorder'})
ON CREATE SET
  d98.canonical_name = 'SchizoidPersonalityDisorder',
  d98.official_name = 'Schizoid Personality Disorder',
  d98.classification_system = 'DSM-5-TR',
  d98.icd11_code = null,
  d98.source_url = 'https://www.psychiatry.org/psychiatrists/practice/dsm',
  d98.dsm5_tr_relationship = 'EXACT',
  d98.classification_status = 'DSM_ONLY',
  d98.count_as_primary_disorder = true,
  d98.audit_row = 98,
  d98.verification_status = 'VERIFIED',
  d98.verification_date = date('2026-09-05'),
  d98.date_added = date();

//  99. ParanoidPersonalityDisorder  [DSM-5-TR NONE]  status=DSM_ONLY
MERGE (d99:Disorder {name:'ParanoidPersonalityDisorder'})
ON CREATE SET
  d99.canonical_name = 'ParanoidPersonalityDisorder',
  d99.official_name = 'Paranoid Personality Disorder',
  d99.classification_system = 'DSM-5-TR',
  d99.icd11_code = null,
  d99.source_url = 'https://www.psychiatry.org/psychiatrists/practice/dsm',
  d99.dsm5_tr_relationship = 'EXACT',
  d99.classification_status = 'DSM_ONLY',
  d99.count_as_primary_disorder = true,
  d99.audit_row = 99,
  d99.verification_status = 'VERIFIED',
  d99.verification_date = date('2026-09-05'),
  d99.date_added = date();

// 100. HistrionicPersonalityDisorder  [DSM-5-TR NONE]  status=DSM_ONLY
MERGE (d100:Disorder {name:'HistrionicPersonalityDisorder'})
ON CREATE SET
  d100.canonical_name = 'HistrionicPersonalityDisorder',
  d100.official_name = 'Histrionic Personality Disorder',
  d100.classification_system = 'DSM-5-TR',
  d100.icd11_code = null,
  d100.source_url = 'https://www.psychiatry.org/psychiatrists/practice/dsm',
  d100.dsm5_tr_relationship = 'EXACT',
  d100.classification_status = 'DSM_ONLY',
  d100.count_as_primary_disorder = true,
  d100.audit_row = 100,
  d100.verification_status = 'VERIFIED',
  d100.verification_date = date('2026-09-05'),
  d100.date_added = date();

// ============================================================================
// DIAGNOSTIC QUALIFIER (NOT one of the 100 primary disorders)
// Borderline pattern (6D11.5) is a prominent personality trait/pattern that
// qualifies the primary Personality disorder (6D10) diagnosis.
// ============================================================================
MERGE (q:DiagnosticQualifier {name:'BorderlinePattern'})
ON CREATE SET
  q.canonical_name = 'BorderlinePattern',
  q.official_name = 'Borderline pattern',
  q.classification_system = 'WHO ICD-11',
  q.icd11_code = '6D11.5',
  q.icd11_release = '2026-01',
  q.icd11_baseline_release = '2024-01',
  q.qualifier_of = 'PersonalityDisorder',
  q.count_as_primary_disorder = false,
  q.verification_status = 'VERIFIED',
  q.verification_date = date('2026-09-05'),
  q.date_added = date(),
  q.source_url = 'https://icd.who.int/browse/2026-01/mms/en';

MATCH (pd:Disorder {name:'PersonalityDisorder'})
MATCH (q:DiagnosticQualifier {name:'BorderlinePattern'})
MERGE (pd)-[:HAS_QUALIFIER]->(q);

// ---- Read-only self-check (safe; returns counts, writes nothing) ----
// MATCH (d:Disorder) RETURN count(d) AS primary_disorders;                      // expect 100
// MATCH (q:DiagnosticQualifier) RETURN count(q) AS qualifiers;                  // expect 1
// MATCH (:Disorder)-[r:HAS_QUALIFIER]->(:DiagnosticQualifier) RETURN count(r);  // expect 1
