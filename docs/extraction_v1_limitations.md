# Extraction v1 — Known Limitations

## Status

Extraction v1 is frozen at commit `5b76d68`.

The extractor is a deterministic, rule-based prototype for converting
safety narratives into the shared SafetyReport representation.

The current version is intentionally not modified while the
Relationship → Precursor pipeline is being integrated.

## 1. Working-at-height context

Some narratives describe elevated work indirectly through equipment,
specific heights, elevated surfaces, trailers, boats, or other context.

These cases are not consistently classified as `working_at_height`.

Representative examples:
- 2020032573
- 2020087536
- 20181212558
- 2024010832
- 2019076738
- 2022053827

Potential v1.1 improvement:
Context-aware working-at-height detection.

## 2. Slip/trip/fall classification

The annotation taxonomy contains `slip_trip_fall`, but Extraction v1
does not infer this label from generic trip/fall wording.

This avoids unsupported classification from generic fall language.

Representative examples:
- 2024109475
- 2016053967
- 2024043119

Potential v1.1 improvement:
Define explicit evidence criteria before enabling this classification.

## 3. Activity context

Some narratives require contextual interpretation to distinguish
activities such as:
- maintenance
- cleaning
- lifting
- equipment operation
- material handling
- electrical work

Representative examples:
- 20161211967
- 2022087540
- 2019065852
- 2022053971
- 2025077419

Potential v1.1 improvement:
Improve context-aware activity extraction.

## 4. Equipment false positives

Generic equipment terms can trigger equipment labels even when the
mentioned equipment is not the primary event-relevant equipment.

Representative examples:
- 2020032573
- 20181111625
- 2016032226
- 2020021801
- 2022053971

Potential v1.1 improvement:
Improve contextual equipment association.

## 5. Line-of-fire detection

Some narratives describe shifting, swinging, rotating, or moving
objects/equipment that create line-of-fire conditions without
explicitly using the phrase `line of fire`.

Representative examples:
- 20181111625
- 2025066296
- 2025088688
- 2015041889
- 2016098325

Potential v1.1 improvement:
Add context-aware line-of-fire detection.

## 6. Caught-in vs caught-between

Some narratives contain overlapping mechanisms where simple keyword
matching cannot reliably distinguish `caught_in` from `caught_between`.

Representative examples:
- 2020032676
- 2021032590
- 2019065827
- 2021098316

Potential v1.1 improvement:
Improve contextual exposure classification and rule precedence.

## 7. Multiple-label limitation

The current SafetyReport contract represents `barrier_failure` and
`exposure` as scalar fields.

Some annotated reports contain multiple explicit labels.

For example, report `2025044043` contains both:
- `inadequate_fall_protection`
- `missing_guard`

Extraction v1 may return only one value.

This is a known v1 representation limitation.

The SafetyReport contract is not modified to solve this limitation.

## 8. Annotation ambiguity

Some evaluation differences may arise from differences between explicit
evidence requirements and gold-label interpretation.

Gold labels should not be changed solely to improve extraction metrics.

## 9. Generic equipment/hazard inference

Mentioning an equipment type does not necessarily mean that the
corresponding hazard should be assigned.

Examples include mobile equipment being mentioned in narratives whose
gold hazard is `working_at_height`.

Potential v1.1 improvement:
Separate entity mention from event-relevant safety-context classification.