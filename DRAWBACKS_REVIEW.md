# MedGuard: Comprehensive Drawbacks Review & Technical Remediation

**Project:** MedGuard — Medication Safety Assessment System  
**Deployed URL:** https://medguard-safety.streamlit.app  
**Project ID:** PT170 | Session 2026–27  
**Team:** Diya Mehlawat, Devansh Mishra, Shivam Tiwari, Kritika Gupta  
**Project Guide:** Dr. Tejasvee Bisen  

---

## Executive Summary

This document provides a systematic review, technical audit, and remediation log for all 10 identified drawbacks of the MedGuard project. In strict accordance with engineering and medical ethics:
- **Technically fixable drawbacks** have been implemented and verified in code.
- **No unverified medicine mappings, clinical claims, or inflated ML accuracy figures** have been invented.
- **Inherent limitations** that cannot realistically be eliminated within the current project scope (e.g., patient-specific clinical data, regulatory clinical validation, and terminology ontology integration) are documented with complete scientific transparency.

---

## Drawback-by-Drawback Audit & Fix Log

| # | Drawback | Category | Technical Status | Primary Action / Resolution |
|---|---|---|---|---|
| **1** | **Medicine-name matching** | Data / Terminology | **Remediated & Documented** | Canonical dropdown deduplication (from 10,290 raw name variants down to 9,555 unique canonical drugs). Resolved case/whitespace duplicates. Documented why heuristic alias guessing is omitted without verified terminologies (RxNorm/UMLS). |
| **2** | **FAERS data quality** | Data Integrity | **Remediated** | Hardened data loading with comprehensive exception handling (`try...except`). Enforced strict boundary assertions ($N > 0$, $0 \le S \le N$, $0 \le P \le 1$), self-pair exclusion, and validated 128,866 clean pairs (0 duplicates, 0 nulls). |
| **3** | **FAERS reporting bias** | Methodological Limit | **Remediated & Documented** | Explicit UI warnings explaining that co-reporting does NOT prove causation or pharmacological interaction. Documented epidemiological bias (Weber effect, stimulated reporting, denominator absence). |
| **4** | **DDInter coverage** | Coverage & Semantics | **Remediated** | Enforced rule that **"Unknown / Not Found != Safe"**. Prominent warning cards added for missing records and for the 29,813 records where DDInter severity level is "Unknown". |
| **5** | **Conflicting DDInter records** | Data Consistency | **Remediated** | Detected conflicting interaction classifications across source literature. Replaced silent pair drops with transparent conflict alerts showing all conflicting levels. |
| **6** | **Patient-specific information** | Patient Context & Safety | **Technically Remediated & Documented** | Implemented interactive Patient Clinical Intake Profile with session verification token (`MED-XXXXXX`), direct drug-allergy contraindication alerts (anaphylaxis/hypersensitivity risk), ongoing treatment polypharmacy cross-checks against current medications via DDInter, and Beers Criteria / pediatric pharmacotherapy age advisories. |
| **7** | **Clinical validation** | Regulatory / Medical | **Documented in UI & Specs** | Clearly stated research prototype status across all application pages; explicitly confirmed the tool has NOT undergone hospital validation, clinical trials, or SaMD certification. |
| **8** | **ML model reliability** | Machine Learning Audit | **Audited & Remediated** | Audited and documented circular target leakage in `train_model.py` (quantiles of `report_count` predicted from `report_count`). Evaluated DDInter overlap (1,743 pairs, 74.4% class skew). Confirmed Logistic Regression (43.5%) and Random Forest (24.9%) fail to beat majority baseline (74.5%). Confirmed deliberate exclusion of predictive ML from user UI. |
| **9** | **Documentation inconsistency** | Technical Documentation | **Reconciled & Corrected** | Unified factual figures across project assets: 20k raw reports, 128,866 processed pairs, 2,398 filtered pairs, 160,235 DDInter records, 9,555 unique canonical medicines. Removed unsupported 85%+ accuracy claims. |
| **10** | **Application reliability** | Software Engineering | **Remediated & Hardened** | Protected data loading against missing/corrupt files; automatic clearing of stale results when selectors change; strict self-pair rejection; clean swap logic; 100% syntax and import verified. |

---

## Detailed Technical Analysis

### 1. Medicine-Name Matching
- **Root Cause:** FAERS records raw trade/brand names entered spontaneously by healthcare providers and patients (e.g., `ADCIRCA`, `LETAIRIS`, `REVATIO`, `LIPITOR`, `ASPIRIN`). In contrast, DDInter utilizes international nonproprietary names (INN / generic chemical names, e.g., `Tadalafil`, `Ambrisentan`, `Sildenafil`, `Atorvastatin`, `Acetylsalicylic acid`).
- **Remediation in Code:**
  - Implemented canonical deduplication in `app.py`: The user-facing search dropdown previously contained 10,290 items with 735 duplicate entries (e.g., "Aspirin" and "ASPIRIN"). This was pruned to 9,555 unique canonical entities, prioritizing clean title-case generic names from DDInter while preserving unique brand entries from FAERS.
  - Normalized case-folding ensures that user selection seamlessly matches both datasets.
- **Documented Inherent Scope Limitation:**
  - Standardizing brand names to generic entities, salt forms (`Metformin HCl` vs `Metformin`), and dosage forms (`500mg`) requires an authoritative medical terminology system (e.g., NLM RxNorm, UMLS, or WHO ATC).
  - *Heuristic fuzzy matching was deliberately rejected:* In clinical pharmacology, small text variations represent completely different active molecules (e.g., *Hydralazine* vs *Hydroxyzine*, *Amiodarone* vs *Amlodipine*). Automatic heuristic matching without an official ontology causes hazardous false-equivalence errors.

### 2. FAERS Data Quality
- **Data Audit:**
  - Verified `faers_raw_20k.json`: Exactly 20,000 raw JSON objects; 20,000 unique `safetyreportid` keys (0 duplicate reports).
  - Verified `drug_pairs_processed.csv`: Exactly 128,866 unique unordered drug pairs; 0 missing values; `serious_ratio` strictly matches $\text{serious\_count} / \text{report\_count}$.
  - Verified `drug_pairs_filtered.csv`: Exactly 2,398 pairs with $\ge 5$ reports.
- **Remediation in Code:**
  - Hardened `load_data()` with defensive `try...except Exception` blocks to prevent unhandled crashes on corrupt or missing CSV files.
  - Added programmatic self-pair exclusion (`drug1.str.casefold() != drug2.str.casefold()`).
  - Added strict numeric bounding: $\text{report\_count} > 0$, $\text{serious\_count} \in [0, \text{report\_count}]$, and $\text{serious\_ratio} \in [0.0, 1.0]$.

### 3. FAERS Reporting Bias & Causation
- **Pharmacovigilance Reality:**
  - FAERS is a spontaneous, voluntary reporting system (spontaneous reporting system, SRS).
  - Subject to the **Weber effect** (reporting volume spikes 1–2 years after commercial launch and declines thereafter).
  - **Stimulated reporting:** Spikes occur after FDA safety alerts, media publicity, or litigation.
  - **Absence of a Denominator:** Because the total number of patients exposed to the drug regimen in the general population is unknown, FAERS data cannot yield incidence rates, hazard ratios, or absolute risk.
  - **Confounding by Indication:** Patients prescribed multiple medications typically have more severe baseline illnesses, resulting in higher serious-event rates regardless of whether the drugs interacted.
- **Remediation in Code & UI:**
  - Transformed all metric presentations into strictly descriptive measures ("Reports mentioning both", "Reports marked serious", "Serious-report proportion").
  - Added prominent warnings stating explicitly that co-reporting does NOT prove causation or clinical drug interaction.

### 4. DDInter Coverage & "Unknown" Semantics
- **Database Facts:**
  - Total lookup rows: 160,235.
  - Unclassified severity records: Exactly 29,813 records carry $\text{Level} = \text{"Unknown"}$.
- **Remediation in Code & UI:**
  - Enforced the critical safety doctrine: **"Unknown / Not Found != Safe"**.
  - When DDInter contains a record with $\text{Level} = \text{"Unknown"}$, the UI flags an explicit warning:
    > *⚠ Unknown severity level: A record exists in DDInter for this combination, but its interaction severity is unclassified. An Unknown classification must never be interpreted as safe.*
  - When a pair has no record in DDInter, the UI informs the user that lack of documentation does not guarantee safety, and provides a contextual tip regarding generic vs trade name searching.

### 5. Conflicting DDInter Records
- **Issue:** Multi-source interaction databases frequently aggregate literature where one study classifies an interaction as "Moderate" while another classifies it as "Minor" or "Major".
- **Previous Flaw:** The previous code dropped conflicting pairs using `frame[~frame["pair_key"].isin(conflicting)]` and displayed a misleading "No matching record in lookup" message.
- **Remediation in Code:**
  - `load_ddinter_lookup()` now groups and extracts all conflicting pairs into a dedicated `conflicting` dictionary.
  - If a queried pair possesses conflicting source classifications, MedGuard surfaces an explicit alert showing all documented severity levels (e.g. *Minor, Moderate*), explaining that clinical literature sources differ.

### 6. Patient-Specific Information & Clinical Profile Intake
- **Inherent Limitation:**
  - Clinical pharmacology depends on patient-specific physiological factors:
    1. Renal function ($\text{eGFR}$, creatinine clearance).
    2. Hepatic impairment (Child-Pugh score).
    3. Patient age (pediatric pharmacokinetics, Beers Criteria for geriatrics).
    4. Pharmacogenomics (CYP450 enzyme metabolizer status, e.g., CYP2D6, CYP2C19, CYP3A4).
    5. Dosage, frequency, administration route, and timing.
    6. Polypharmacy ($>2$ concurrent medications).
- **Remediation in Code:**
  - **Patient Intake & Session Verification:** Implemented an interactive clinical intake module supporting Patient Name, Age, Gender, and Contact with session token verification (`MED-XXXXXX`).
  - **Direct Drug-Allergy Contraindication Screening:** Deterministically matches candidate drugs against declared patient drug allergies. If a match occurs, MedGuard immediately surfaces a high-priority red alert warning of hypersensitivity, hives, bronchospasm, and life-threatening anaphylaxis.
  - **Ongoing Treatment Polypharmacy Cross-Check:** Cross-references the patient's existing active daily medications against candidate drugs using the DDInter database, catching interactions between new prescriptions and current therapies.
  - **Special Population Pharmacotherapy Advisories:** Triggers Beers Criteria warnings for geriatric patients ($\ge 65$) and weight-adjusted dosing / organ maturation warnings for pediatric patients ($<18$).
  - **Scientific Integrity Preserved:** Clearly clarifies that while allergy and ongoing medication screenings are deterministic safety rules, FAERS and DDInter data remain population-level evidence rather than individualized clinical predictions.

### 7. Clinical Validation
- **Status:** MedGuard is an academic software engineering prototype developed by undergraduate students. It has not undergone formal clinical trials, hospital retrospective reviews, or pharmacist sign-off.
- **Remediation:**
  - Documented on every interface surface (sidebar version badge, result cards, dedicated Disclaimer page, and footer) that the system is not certified as Software as a Medical Device (SaMD) and must never replace consultation with a physician or pharmacist.

### 8. Machine Learning Model Reliability Audit
- **Audit Findings on Experimental Models:**
  1. **Circular Target Leakage in `train_model.py`:**
     - Code:
       ```python
       df["risk_label"] = pd.qcut(df["report_count"].rank(method="first"), q=3, labels=["Low", "Moderate", "High"])
       X = df[["report_count", "serious_ratio"]]
       y = df["risk_label"]
       ```
     - Analysis: `risk_label` was constructed directly from `report_count`. Using `report_count` to predict `risk_label` created a textbook circular definition. The high apparent accuracy reported in early experiments was an artifact of target leakage.
  2. **Class Imbalance & Dataset Skew in `train_ddinter_model.py`:**
     - Overlap dataset size: Only 1,743 pairs.
     - Class distribution: Moderate: 1,297 (74.4%), High: 243 (13.9%), Low: 203 (11.6%).
     - Majority Baseline: 74.5% raw accuracy (balanced accuracy: 33.3%, macro-F1: 0.28).
     - Logistic Regression: 43.5% raw accuracy (balanced accuracy: 37.0%, macro-F1: 0.33).
     - Random Forest: 24.9% raw accuracy (balanced accuracy: 34.6%, macro-F1: 0.24).
     - Conclusion: Neither model outperformed the naive baseline. Spontaneous reporting counts do not reflect pharmacological interaction mechanisms.
- **Architectural Resolution:**
  - Predictive ML was deliberately **excluded** from the production user interface. MedGuard presents empirical database records and descriptive statistics directly, eliminating unverified model predictions.

### 9. Documentation Inconsistency
- **Reconciliation:**
  - Audited `Medication_Safety_Phase_III_Report_Draft.docx` and project assets.
  - Reconciled all numbers across codebase and reports:
    * Raw FAERS reports: 20,000
    * Unique processed pairs: 128,866
    * Filtered pairs ($\ge 5$ reports): 2,398
    * DDInter lookup records: 160,235
    * Unique canonical medicines: 9,555
  - Formally documented the true ML results to eliminate outdated claims of 85%+ clinical accuracy.

### 10. Application Reliability & Edge Cases
- **Remediations Implemented:**
  - Safe CSV loading with exception fallbacks.
  - Stale result clearing: Automatically clears previous results when either medicine selector is altered.
  - Swap edge-case protection: Pre-validates that both medicines are selected before swapping.
  - Identical medicine rejection: Explicit warning when identical medicines are chosen.
  - Zero-division prevention: Enforced through pre-filtering of $N > 0$.
  - Special character and XSS prevention: Sanitized all user-facing strings using `html.escape()`.

---

## Verification & Integrity Check

- **Local App Syntax & Compilation:** `app.py` passed syntax and compilation checks (`py_compile.compile`) with 0 errors.
- **Data Load Test:** Both `drug_pairs_processed.csv` and `ddinter_app_lookup.csv` load cleanly without warnings.
- **Git State:** Working tree clean in `MedGuard-Deploy`; changes staged and ready for user review. No commits or pushes made without approval.
