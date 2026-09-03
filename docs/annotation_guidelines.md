# SIH26165 Annotation Guidelines — Version 1

## 1. Objective

Annotate safety reports for the following safety signals:

- Hazard
- Activity
- Equipment
- Barrier Failure
- Exposure

The annotation must represent only information explicitly supported by
the report.

Do not infer missing information.

---

## 2. General Rules

### Rule 1 — Evidence first

Every label must have supporting evidence in the narrative.

### Rule 2 — Missing information

If a signal cannot be determined:

null

Do not guess.

### Rule 3 — Multiple labels

Multiple values are allowed when the narrative clearly describes multiple
independent safety signals.

### Rule 4 — Separate concepts

Do not confuse:

Hazard → dangerous condition/energy

Activity → work being performed

Equipment → object/equipment involved

Barrier Failure → failed/missing/ineffective safety control

Exposure → how the person was exposed to the hazard

### Rule 5 — Injury is not automatically a safety signal

The injury outcome must not be used as a substitute for the hazard,
barrier failure, or exposure.

---

# 3. Hazard Annotation

## Definition

The dangerous condition, energy, or hazardous situation that creates
potential for harm.

### Examples

"Worker was standing beneath a suspended load."

hazard:
lifting_operation

"Employee was working from a ladder."

hazard:
working_at_height

"Worker's hand became caught in a running conveyor."

hazard:
moving_machinery

### Do not infer

A fall does not automatically mean:

working_at_height

unless the narrative supports exposure to an elevated location.

---

# 4. Activity Annotation

## Definition

The work activity being performed.

### Examples

"Employee was performing preventive maintenance."

activity:
maintenance

"Workers were lifting a pipe spool."

activity:
lifting

"Employee was installing electrical cable."

activity:
electrical_work

### Rule

The activity must be supported by the narrative.

---

# 5. Equipment Annotation

## Definition

The equipment, machinery, tool, structure, or physical object directly
involved in the event.

### Examples

ladder
scaffold
crane
EOT_crane
forklift
conveyor
road_roller
truck
pipeline

### Rule

Do not infer equipment from the activity.

Example:

"Employee was performing maintenance."

equipment:
null

unless equipment is mentioned.

---

# 6. Barrier Failure Annotation

## Definition

A missing, inadequate, failed, bypassed, or ineffective safety control
that contributed to the hazardous situation.

### Examples

"Harness was not anchored."

barrier_failure:
inadequate_fall_protection

"Crane was used instead of the air winch required by SOP."

barrier_failure:
SOP_violation

"Worker was standing directly below the suspended load."

barrier_failure:
unsafe_positioning

### Important

Do NOT infer barrier failure from the event alone.

Example:

"Employee fell from a ladder."

barrier_failure:
null

unless the narrative provides evidence of a failed or missing control.

---

# 7. Exposure Annotation

## Definition

The manner in which a person was exposed to the hazard.

### Examples

"Worker fell approximately 2.8 meters."

exposure:
fall_from_height

"Worker was pinned between two road rollers."

exposure:
caught_between

"Rigger was struck by a falling pipe spool."

exposure:
struck_by

"Worker's hand was caught in the conveyor."

exposure:
caught_in

---

# 8. Evidence

Each annotation should retain the supporting text span or short evidence
phrase.

Example:

Narrative:

"The full body safety harness was not anchored."

Annotation:

barrier_failure:
inadequate_fall_protection

evidence:
"The full body safety harness was not anchored."

---

# 9. Annotation Output

Each annotated record should contain:

- report_id
- source
- timestamp
- site
- source_type
- narrative
- hazard
- activity
- equipment
- barrier_failure
- exposure
- evidence

---

# 10. Confidence

Use:

high
medium
low

Confidence reflects how clearly the narrative supports the annotation.

It is not model confidence.

---

# 11. Annotation Philosophy

The objective is not to maximize the number of labels.

The objective is to create accurate, evidence-supported safety signals.

A partially annotated report with null values is preferable to a
report containing guessed labels.

---

# 12. Version

Taxonomy version:

v1

Annotation guideline version:

v1

Status:

Initial annotation