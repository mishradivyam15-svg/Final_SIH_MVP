# AI ↔ Backend Integration

## 1. Purpose

This document defines the integration contract between the AI pipeline and
the backend for the NeuroNexus SIF precursor detection prototype.

The integration layer consumes structured SafetyReport objects from the
backend, passes them through the AI-2 relationship and precursor pipeline,
and exposes explainable JSON-compatible results.

The current AI-2 implementation is a deterministic prototype based on
heuristic relationship and prioritization logic. The scores are not
validated predictions of fatalities or accidents.

---

## 2. Current Architecture

The current prototype flow is:

Backend
  ↓
SafetyReport
  ↓
RelationshipEngine
  ↓
RelationshipResult
  ↓
RelationshipGraph
  ↓
ClusterEngine
  ↓
PrecursorGroup
  ↓
PrecursorEngine
  ↓
Precursor / Priority Output

AI-1 is responsible for safety signal extraction and producing structured
SafetyReport data.

AI-2 consumes SafetyReport data and performs relationship detection,
graph construction, precursor grouping, and priority summarization.

---

## 3. SafetyReport Input Contract

The backend sends structured safety reports using the following field names.

| Field | Meaning |
|---|---|
| report_id | Stable report identifier |
| timestamp | Event/report timestamp |
| site | Site/location |
| source_type | Report source/type |
| narrative | Original safety-event narrative |
| hazard | Hazard; may be null |
| activity | Activity; may be null |
| equipment | Equipment; may be null |
| barrier_failure | Barrier failure; may be null |
| exposure | Exposure; may be null |
| severity_potential | Severity potential, when available |

### Missing values

Missing structured signals are treated as unknown.

A missing value must not be interpreted as a negative match.

For example, if one report has:

    hazard = "working_at_height"

and another has:

    hazard = null

the system must not treat this as evidence that the hazards are different.

The current relationship implementation uses a neutral score of 0.50 for
missing structured values by default.

---

## 4. RelationshipResult Output Contract

The relationship layer produces a RelationshipResult containing:

| Field | Meaning |
|---|---|
| source_report_id | Identifier of the first report |
| target_report_id | Identifier of the second report |
| semantic_similarity | Semantic similarity between report narratives |
| hazard_match | Hazard match score |
| activity_match | Activity match score |
| barrier_match | Barrier-failure match score |
| site_match | Site match score |
| temporal_relation | Temporal proximity score |
| relationship_strength | Weighted overall relationship score |
| evidence | Explainable evidence supporting the relationship |

The current implementation also exposes:

    is_related

This indicates whether the relationship passes the current relationship
decision rule.

The RelationshipResult can be converted to a JSON-compatible dictionary
using:

    result.as_dict()

---

## 5. Relationship Decision

The current prototype combines:

- semantic similarity
- hazard match
- activity match
- barrier-failure match
- site match
- temporal relation

The default relationship weights are:

| Signal | Weight |
|---|---:|
| Semantic similarity | 0.30 |
| Hazard | 0.20 |
| Activity | 0.15 |
| Barrier failure | 0.15 |
| Site | 0.10 |
| Temporal | 0.10 |

The default related threshold is 0.55.

A relationship also requires meaningful known contextual evidence. Unknown
contextual fields do not create positive evidence.

---

## 6. Explainable Evidence

RelationshipResult contains an `evidence` list.

Evidence can describe:

- semantic similarity
- matching hazard
- matching activity
- matching barrier failure
- matching site
- known contextual differences
- unknown contextual fields
- temporal distance between reports

Example:

    Same hazard: working_at_height

    Same activity: maintenance

    Same barrier failure: fall_protection_missing

    Same site: site_a

    Reports occurred 2 days apart

This evidence is intended to support human HSE review.

---

## 7. Multi-Report Flow

For multiple SafetyReport objects, the current AI-2 pipeline is:

    SafetyReports
        ↓
    RelationshipGraph
        ↓
    ClusterEngine
        ↓
    PrecursorGroup
        ↓
    PrecursorEngine
        ↓
    Precursor

RelationshipGraph performs pairwise comparisons for unique report pairs.

ClusterEngine creates deterministic precursor candidates using connected
components of meaningful relationship edges.

PrecursorEngine summarizes a candidate group and calculates the current
prototype priority score.

---

## 8. Precursor / Priority Output

The current Precursor object exposes:

| Field | Meaning |
|---|---|
| precursor_id | Stable precursor candidate identifier |
| title | Explainable precursor title |
| priority | HIGH, MEDIUM, or LOW |
| priority_score | Prototype priority score from 0 to 100 |
| report_ids | Reports supporting the precursor |
| common_hazard | Common hazard when supported by the reports |
| common_barrier_failure | Common barrier failure when supported |
| time_window | Time span covered by the reports |
| evidence | Explainable evidence |
| review_status | Current HSE review status |

The current implementation uses:

    HIGH >= 70
    MEDIUM >= 40
    LOW < 40

The Precursor object can be converted to JSON-compatible data using:

    precursor.as_dict()

---

## 9. Priority Scoring

The current prototype priority score combines:

- BFS: barrier-failure severity component
- RF: recurrence frequency
- SSC: mean semantic similarity
- TP: temporal proximity
- AHE: activity/hazard exposure component

The current implementation does not define an ordinal severity mapping for
the exposure representation, so AHE is currently unavailable and contributes
0.0.

These values are prototype heuristics for HSE review prioritization and are
not predictions of accidents or fatalities.

---

## 10. Backend Integration Notes

### Backend sends

The backend should send SafetyReport objects containing the agreed field
names:

    report_id
    timestamp
    site
    source_type
    narrative
    hazard
    activity
    equipment
    barrier_failure
    exposure
    severity_potential

Structured fields may be null when information is unavailable.

### AI returns

For pairwise relationships, the AI returns RelationshipResult data with:

    source_report_id
    target_report_id
    semantic_similarity
    hazard_match
    activity_match
    barrier_match
    site_match
    temporal_relation
    relationship_strength
    is_related
    evidence

For precursor candidates, the current AI-2 implementation returns Precursor
objects with the fields documented in Section 8.

### Explainability

Relationship-level explanations are available in:

    RelationshipResult.evidence

Precursor-level explanations are available in:

    Precursor.evidence

These evidence fields should be preserved when the backend exposes results
to the frontend or HSE review interface.

---

## 11. JSON Compatibility

The current implementation provides explicit conversion methods:

    RelationshipResult.as_dict()
    RelationshipGraph.to_dict()
    PrecursorGroup.as_dict()
    GroupingResult.to_dict()
    Precursor.as_dict()

These return dictionaries, lists, strings, numbers, booleans, and null
values suitable for JSON serialization.

The integration test verifies JSON serialization of the end-to-end result.

---

## 12. Offline Integration Test

The integration test is located at:

    tests/test_ai_integration.py

The test uses deterministic mock SafetyReport objects and a deterministic
embedding substitute.

It does not require the real OSHA/OISD dataset or internet access.

The test verifies:

1. Two SafetyReports can be passed through RelationshipEngine.
2. A RelationshipResult is produced.
3. Relationship scores are present.
4. Explainable evidence is present.
5. Multiple reports can be converted into a RelationshipGraph.
6. Related reports can form a precursor group.
7. The precursor can be summarized and prioritized.
8. Relationship and precursor outputs can be converted to JSON-compatible
   data.

---

## 13. Backend Handoff

The backend integration should preserve:

- exact SafetyReport field names
- null values for unavailable structured signals
- RelationshipResult evidence
- Precursor evidence
- report identifiers
- priority score and priority label

No AI algorithm rewrite is required for this integration.

No serialized `.pkl` artifact is required by the current AI-2 implementation.
The current implementation consumes SafetyReport objects directly.

If a future backend design requires serialization, the exact component or
model requiring serialization should first be identified.

---

## 14. Current Limitations

The current AI-2 implementation is a prototype.

Relationship weights, temporal decay, grouping rules, and priority scoring are
configurable heuristics and have not been validated as production safety
prediction models.

HSE review remains a human-in-the-loop step.

The output should therefore be interpreted as a candidate precursor and
review-prioritization signal rather than an automated determination of
serious injury or fatality risk.