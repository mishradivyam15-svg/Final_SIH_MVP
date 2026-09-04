from ai.extraction import extract_safety_signals


def test_extract_working_at_height():
    report = {
        "report_id": "test-001",
        "narrative": "Employee was working from a ladder and fell.",
    }

    result = extract_safety_signals(report)

    assert result["hazard"] == "working_at_height"


def test_extract_fall_from_height():
    report = {
        "report_id": "test-003",
        "narrative": (
            "Employee was on a step ladder on an elevated deck "
            "and fell 12-15 feet."
        ),
    }

    result = extract_safety_signals(report)

    assert result["hazard"] == "working_at_height"
    assert result["exposure"] == "fall_from_height"


def test_do_not_classify_steps_as_fall_from_height():
    report = {
        "report_id": "test-004",
        "narrative": "Employee tripped and fell down the front steps.",
    }

    result = extract_safety_signals(report)

    assert result["hazard"] is None
    assert result["exposure"] is None


def test_extract_moving_machinery():
    report = {
        "report_id": "test-005",
        "narrative": (
            "Employee was operating a packing machine when "
            "a product became jammed."
        ),
    }

    result = extract_safety_signals(report)

    assert result["hazard"] == "moving_machinery"


def test_extract_electrical_energy_and_exposure():
    report = {
        "report_id": "test-006",
        "narrative": (
            "Employee was performing switching and grounding tasks "
            "when they contacted an energized conductor."
        ),
    }

    result = extract_safety_signals(report)

    assert result["hazard"] == "electrical_energy"
    assert result["exposure"] == "electrical_exposure"


def test_extract_mobile_equipment():
    report = {
        "report_id": "test-007",
        "narrative": (
            "Employee was fixing a tractor when it moved "
            "and struck the employee."
        ),
    }

    result = extract_safety_signals(report)

    assert result["hazard"] == "mobile_equipment"


def test_extract_excavation():
    report = {
        "report_id": "test-008",
        "narrative": (
            "Employee was digging an excavation when "
            "the excavation collapsed."
        ),
    }

    result = extract_safety_signals(report)

    assert result["hazard"] == "excavation"


def test_extract_caught_between():
    report = {
        "report_id": "test-009",
        "narrative": (
            "The employee's finger was caught between "
            "the bin and the chain."
        ),
    }

    result = extract_safety_signals(report)

    assert result["exposure"] == "caught_between"


def test_extract_caught_in():
    report = {
        "report_id": "test-010",
        "narrative": (
            "Employee was operating a conveyor when "
            "their hand was caught in the moving equipment."
        ),
    }

    result = extract_safety_signals(report)

    assert result["exposure"] == "caught_in"


def test_extract_struck_by():
    report = {
        "report_id": "test-011",
        "narrative": (
            "A heavy object fell from a platform "
            "and struck the employee's foot."
        ),
    }

    result = extract_safety_signals(report)

    assert result["exposure"] == "struck_by"


def test_extract_inadequate_fall_protection():
    report = {
        "report_id": "test-012",
        "narrative": (
            "The employee fell from an elevated deck. "
            "Fall protection was not worn at the time of the incident."
        ),
    }

    result = extract_safety_signals(report)

    assert result["barrier_failure"] == "inadequate_fall_protection"


def test_extract_failed_guard():
    report = {
        "report_id": "test-013",
        "narrative": (
            "The employee fell into a temporary guardrail. "
            "The guardrail gave away."
        ),
    }

    result = extract_safety_signals(report)

    assert result["barrier_failure"] == "failed_guard"
def test_extract_unsafe_positioning_on_forklift_box():
    report = {
        "report_id": "2020087536",
        "narrative": (
            "An employee was working from a heavy-duty plastic utility "
            "storage box placed on the forks of a forklift. The box shifted, "
            "tossing him to the concrete floor about 9 feet below."
        ),
    }

    result = extract_safety_signals(report)

    assert result["barrier_failure"] == "unsafe_positioning"


def test_extract_missing_guard():
    report = {
        "report_id": "2025044043",
        "narrative": (
            "The employee fell into an unguarded elevator shaft."
        ),
    }

    result = extract_safety_signals(report)

    assert result["barrier_failure"] == "missing_guard"


def test_extract_inadequate_fall_protection():
    report = {
        "report_id": "2025044043",
        "narrative": (
            "Fall protection was not in place at the time."
        ),
    }

    result = extract_safety_signals(report)

    assert result["barrier_failure"] == "inadequate_fall_protection"


def test_extract_sop_violation_lockout_tagout():
    report = {
        "report_id": "2017087462",
        "narrative": (
            "The press machine was not locked/tagged out at the time."
        ),
    }

    result = extract_safety_signals(report)

    assert result["barrier_failure"] == "SOP_violation"


def test_extract_unsafe_positioning_rolling_forklift():
    report = {
        "report_id": "2017066029",
        "narrative": (
            "An employee attempted to stop a forklift from rolling "
            "by placing a piece of wood under the tire."
        ),
    }

    result = extract_safety_signals(report)

    assert result["barrier_failure"] == "unsafe_positioning"