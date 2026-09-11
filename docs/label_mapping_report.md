# Label Mapping Report — Phase 1

**Date**: 2026-09-10
**Branch**: `ai/relationship-precursor`
**Dataset**: `data/January2015toNovember2025.csv` (105,996 OSHA reports)

---

## 1. Mapping Methodology

### 1.1 Approach

Each of the 570 unique OSHA `EventTitle` values was mapped to the project's
SIF precursor taxonomy using **ordered substring pattern matching**:

1. The `EventTitle` string is lowercased.
2. An ordered list of 200+ pattern rules is evaluated sequentially.
3. The **first matching rule** determines the (hazard, exposure, confidence) label.
4. If no rule matches, the row receives `null` for both labels.

### 1.2 Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Full 14-hazard taxonomy** | Includes `lifting_operation`, `confined_space`, `hydrocarbon_or_process_hazard` even though they have zero EventTitle-derived samples. These will be populated via narrative-based labeling in a later phase. |
| **Scalar labels** | One hazard + one exposure per row. Preserves the `SafetyReport` contract used by the downstream `RelationshipEngine`. |
| **FALL_OTHER → null/null** | 6,978 ambiguous fall events kept as null. EventTitle alone cannot distinguish same-level vs height falls. |
| **STRUCK_AGAINST → null/null** | 2,964 "worker struck object" events kept as null. Semantically distinct from "object struck worker" (`struck_by`). |
| **Confidence levels** | Each mapping carries `high` / `medium` / `low` to enable confidence-weighted training loss. |
| **None = negative example** | Null labels are intentional — they teach the model when NOT to predict a label. |

### 1.3 Label Sources

| Label Type | Source Signal | Direction |
|-----------|-------------|-----------|
| **Exposure** | EventTitle describes *how* the person was injured | Direct mapping |
| **Hazard** | EventTitle implies *what* dangerous condition existed | Indirect inference |

---

## 2. Coverage Statistics

### 2.1 Hazard Labels

| Hazard Label | Count | % of 105,996 |
|-------------|------:|:------------:|
| `working_at_height` | 18,384 | 17.3% |
| `moving_machinery` | 17,625 | 16.6% |
| `slip_trip_fall` | 14,188 | 13.4% |
| `mobile_equipment` | 8,330 | 7.9% |
| `line_of_fire` | 6,530 | 6.2% |
| `falling_object` | 6,238 | 5.9% |
| `fire_or_hot_work` | 5,789 | 5.5% |
| `electrical_energy` | 2,106 | 2.0% |
| `chemical_exposure` | 1,913 | 1.8% |
| `stored_energy` | 626 | 0.6% |
| `excavation` | 111 | 0.1% |
| `lifting_operation` | 0 | 0.0% * |
| `confined_space` | 0 | 0.0% * |
| `hydrocarbon_or_process_hazard` | 0 | 0.0% * |
| **(null — unmapped)** | **24,156** | **22.8%** |

\* Narrative-only labels — require future narrative-based labeling.

**Total mapped to a hazard: 81,840 (77.2%)**

### 2.2 Exposure Labels

| Exposure Label | Count | % of 105,996 |
|---------------|------:|:------------:|
| `fall_from_height` | 19,108 | 18.0% |
| `struck_by` | 18,649 | 17.6% |
| `caught_in` | 17,787 | 16.8% |
| `caught_between` | 7,656 | 7.2% |
| `falling_object_exposure` | 6,238 | 5.9% |
| `electrical_exposure` | 2,106 | 2.0% |
| `chemical_exposure` | 1,905 | 1.8% |
| `fire_exposure` | 1,249 | 1.2% |
| **(null — unmapped)** | **31,298** | **29.5%** |

**Total mapped to an exposure: 74,698 (70.5%)**

### 2.3 Joint Mapping

| Category | Count | % |
|----------|------:|:-:|
| Both hazard + exposure mapped | 61,397 | 57.9% |
| Hazard only (exposure null) | 20,443 | 19.3% |
| Exposure only (hazard null) | 13,301 | 12.5% |
| Both null | 10,855 | 10.2% |

### 2.4 Confidence Distribution

| Confidence | Count | % |
|-----------|------:|:-:|
| `high` | 74,721 | 70.5% |
| `medium` | 18,597 | 17.5% |
| `low` | 1,823 | 1.7% |
| `(null)` | 10,855 | 10.2% |

---

## 3. Class Imbalance Analysis

### 3.1 Hazard Imbalance

The top-3 hazard classes (`working_at_height`, `moving_machinery`, `slip_trip_fall`)
account for **50,197 / 81,840 = 61.3%** of mapped labels. The bottom-3
(`stored_energy`, `excavation`, plus 3 zero-sample labels) are severely
underrepresented.

**Mitigation for model training:**
- Class-weighted cross-entropy loss
- Stratified train/val/test splits
- Possible oversampling of `excavation` and `stored_energy`

### 3.2 Exposure Imbalance

The top-3 exposure classes (`fall_from_height`, `struck_by`, `caught_in`)
account for **55,544 / 74,698 = 74.4%** of mapped labels.
`fire_exposure` (1,249) and `chemical_exposure` (1,905) are the smallest.

**Mitigation**: Same as hazard — weighted loss + stratified splits.

---

## 4. Unmapped / Ambiguous EventTitles

### 4.1 Null Categories (both hazard + exposure = null)

These 10,855 rows have EventTitles outside the SIF precursor taxonomy:

| Category | Example EventTitles | Rows |
|----------|-------------------|-----:|
| Violence/intentional | Shooting, Stabbing, Hitting/kicking | ~1,431 |
| Animal/insect | Animal bites, Stings, Kicked by animal | ~1,268 |
| Overexertion | Overexertion in lifting, Bending/crawling | ~1,240 |
| Generic contact | Contact with objects, Contact incidents | ~1,482 |
| Nonclassifiable | OSHA "Nonclassifiable" | ~790 |
| Fall other | Fall while sitting, Fall from pedal cycle | ~6,978 * |
| Struck against | Struck against machinery, Walked into object | ~2,964 * |
| Transport other | Aircraft, rail, water vehicle incidents | ~198 |
| Bodily motion | Walking, Standing, Kneeling | ~279 |
| Other | Generic unspecified, rubbed/abraded | ~80 |

\* Explicitly approved as null by the user (conservative mapping).

### 4.2 Partial Mappings

13,301 rows have an exposure but no hazard (ambiguous hazard source):
- Generic "Caught in or compressed" (hazard could be machinery or objects)
- "Struck by object" without clear hazard context
- Door/gate strikes
- Generic "struck by" catch-all

20,443 rows have a hazard but no exposure (ambiguous exposure mechanism):
- Jack-knifed/overturned vehicles (hazard = mobile_equipment, exposure varies)
- Heat exposure (hazard = fire_or_hot_work, not technically fire_exposure)
- Explosions (hazard = stored_energy, exposure could be struck_by or fire)
- Slip/trip events (hazard = slip_trip_fall, no exposure in taxonomy for same-level falls)

---

## 5. Validation Results

All 8 validation checks passed:

| Check | Result |
|-------|--------|
| All hazard labels are valid taxonomy members | ✅ 11 unique + null |
| All exposure labels are valid taxonomy members | ✅ 8 unique + null |
| Row count matches input dataset | ✅ 105,996 |
| Output file exists and is non-trivial | ✅ 42.5 MB |
| No orphan confidence values | ✅ |
| All labeled rows have confidence | ✅ |
| All narratives non-empty | ✅ |
| Narrative-only labels have 0 EventTitle samples | ✅ |

---

## 6. Files Created

| File | Purpose | Size |
|------|---------|------|
| `ai/label_mapping.py` | Canonical EventTitle → (hazard, exposure, confidence) mapping module | 766 lines |
| `ai/label_construction.py` | Label generation pipeline with statistics and validation | 227 lines |
| `data/labeled/training_labels.csv` | Generated training labels (18 columns, 105,996 rows) | 42.5 MB |
| `docs/label_mapping_report.md` | This report | — |

### Files NOT Modified

- `ai/extraction.py` — untouched
- `ai/relationship.py` — untouched
- `data/January2015toNovember2025.csv` — untouched (original dataset)
- All other existing AI modules — untouched

---

## 7. Output Schema

The generated `training_labels.csv` has 18 columns:

| Column | Source | Description |
|--------|--------|-------------|
| `ID` | Original | OSHA report identifier |
| `EventDate` | Original | Incident date |
| `EventTitle` | Original | OSHA event classification (source of labels) |
| `Primary NAICS` | Original | Industry code |
| `Hospitalized` | Original | Hospitalization indicator |
| `Amputation` | Original | Amputation indicator |
| `Loss of Eye` | Original | Eye loss indicator |
| `Nature` | Original | Injury nature code |
| `NatureTitle` | Original | Injury nature label |
| `Part of Body` | Original | Body part code |
| `Part of Body Title` | Original | Body part label |
| `Event` | Original | Event code |
| `Source` | Original | Source of injury code |
| `SourceTitle` | Original | Source of injury label |
| `Final Narrative` | Original | Free-text incident description |
| **`hazard_label`** | **Generated** | **Mapped hazard (or empty)** |
| **`exposure_label`** | **Generated** | **Mapped exposure (or empty)** |
| **`mapping_confidence`** | **Generated** | **high / medium / low (or empty)** |
