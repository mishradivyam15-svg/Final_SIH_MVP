# SIH26165 Safety Signal Taxonomy — Version 1

## Purpose

This taxonomy defines the safety signals extracted from individual safety
reports before cross-report relationship analysis.

The extraction layer must describe only information supported by the report.
It must not invent missing information.

---

## 1. Hazard

### Definition

The dangerous condition, energy, or hazardous situation that creates the
potential for harm.

### Initial categories

- `working_at_height`
- `line_of_fire`
- `lifting_operation`
- `electrical_energy`
- `mobile_equipment`
- `moving_machinery`
- `excavation`
- `confined_space`
- `fire_or_hot_work`
- `hydrocarbon_or_process_hazard`
- `stored_energy`
- `chemical_exposure`
- `slip_trip_fall`
- `falling_object`

### Examples

Narrative:

"Employee was working from a ladder and fell."

```text
hazard = working_at_height