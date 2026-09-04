from typing import Any
import re


def extract_safety_signals(report: dict[str, Any]) -> dict[str, Any]:
    """
    Extract structured safety signals from one preprocessed report.

    Current approach:
    - Rule-based extraction
    - Only uses explicit evidence from the narrative
    - Missing signals remain None
    - Evidence stores the phrase that triggered the signal
    """

    narrative = report.get("narrative", "")
    text = narrative.lower()

    hazard = None
    exposure = None
    activity = None
    equipment = None
    barrier_failure = None
    evidence = {}

    # ---------------------------------------------------------
    # Hazard extraction
    # ---------------------------------------------------------
    hazard_indicators = {
        "moving_machinery": [
            "moving machine",
            "moving machinery",
            "rotating shaft",
            "rotating equipment",
            "rotating machinery",
            "pinch roller",
            "power press",
            "brake press",
            "chop saw",
            "cutoff saw",
            "lathe",
            "conveyor",
            "packing machine",
            "tape machine",
        ],

        "electrical_energy": [
            "energized conductor",
            "energized wire",
            "live electrical wire",
            "live wire",
            "electrical shock",
            "electric shock",
            "arc flash",
            "electrical injury",
            "electrical energy",
        ],

        "mobile_equipment": [
            "forklift",
            "reach truck",
            "tractor",
            "order picker",
            "golf cart",
            "tug",
            "mobile equipment",
        ],

        "excavation": [
            "excavation",
            "excavating",
            "trench",
            "ditch",
            "digging",
        ],

        "falling_object": [
            "falling object",
            "object fell",
            "material fell",
            "racks fell",
            "fell onto",
        ],

        "line_of_fire": [
            "line of fire",
            "kicked back",
            "rolled over",
            "shifted unexpectedly",
            "swinging load",
        ],

        "lifting_operation": [
            "lifting operation",
            "lifting chain",
            "rigging",
            "rigging up",
            "suspended load",
        ],

        "chemical_exposure": [
            "chemical splash",
            "chemical exposure",
            "sodium hydroxide",
            "corrosive",
        ],

        "stored_energy": [
            "pressurized",
            "pressure was released",
            "stored energy",
            "tension was released",
        ],
    }

    for hazard_label, indicators in hazard_indicators.items():
        for indicator in indicators:
            if indicator in text:
                hazard = hazard_label
                evidence["hazard"] = [indicator]
                break

        if hazard is not None:
            break

    # Working-at-height requires actual elevated-position context.
    height_context = [
        "working from a ladder",
        "working on a ladder",
        "working from scaffold",
        "working on scaffold",
        "working from scaffolding",
        "working on scaffolding",
        "on an elevated platform",
        "on an elevated deck",
        "working at height",
        "working from an elevated",
        "working on an elevated",
        "on the roof",
        "working on the roof",
        "on the roof of",
        "second floor",
        "third floor",
        "fourth floor",
        "fixed ladder",
        "portable ladder",
        "on a ladder",
        "on the ladder",
        "scissor lift",
        "warehouse lift",
        "elevated deck",
        "rig floor",
        "fell from a boat",
        "fell off the ladder",
        "fell from the rear of the trailer",
        "fell off the tug",
        "walking along the ridge of a roof",
    ]

    if hazard is None:
        for indicator in height_context:
            if indicator in text:
                hazard = "working_at_height"
                evidence["hazard"] = [indicator]
                break

    # ---------------------------------------------------------
    # Exposure extraction
    # ---------------------------------------------------------
    #
    # Current contract remains scalar.
    #
    # Ordering is intentional:
    #
    # 1. electrical
    # 2. caught-between
    # 3. caught-in
    # 4. falling-object
    # 5. struck-by
    # 6. fall-from-height
    # 7. fire
    # 8. chemical
    #
    # Important:
    # Specific caught-in patterns such as "caught in moving
    # equipment" must be checked before generic "hand was caught"
    # patterns so that caught-in is not misclassified as
    # caught-between.
    # ---------------------------------------------------------

    exposure_indicators = {

        # -----------------------------------------------------
        # Electrical exposure
        # -----------------------------------------------------
        "electrical_exposure": [
            "contacted an energized conductor",
            "contacted an energized wire",
            "contact with energized conductor",
            "contact with energized wire",
            "contacted a live wire",
            "contact with live wire",
            "contacted the primary conductor",
            "contacted primary conductor",
            "shocked by",
            "was shocked",
            "received a shock",
            "received an electrical shock",
            "electrical shock",
            "electric shock",
            "electrical injury",
            "arc flash",
            "voltage was discharged",
            "voltage discharged",
            "indirectly shocked",
            "exposed to electrical energy",
        ],

        # -----------------------------------------------------
        # Caught-in
        # -----------------------------------------------------
        #
        # Specific machinery/entanglement patterns come before
        # caught-between so that:
        #
        # "hand was caught in moving equipment"
        #
        # remains caught_in.
        # -----------------------------------------------------
        "caught_in": [
            "caught in the",
            "caught in moving",
            "caught in machinery",
            "caught in machine",
            "caught in conveyor",
            "caught in a conveyor",
            "caught by the lathe",
            "caught by a lathe",
            "caught by the machine",
            "caught by machinery",
            "became caught in",
            "caught in some",
            "entangled in",
            "became entangled",
            "wrapped around",
            "hand entered the stroke path",
            "finger entered the stroke path",
            "arm entered the stroke path",
        ],

        # -----------------------------------------------------
        # Caught-between
        # -----------------------------------------------------
        "caught_between": [
            # Direct caught-between language
            "caught between",
            "caught in between",
            "pinched between",
            "trapped between",
            "crushed between",
            "pinned between",
            "caught against",
            "pinned against",
            "crushed against",
            "caught underneath",
            "pinned underneath",
            "pinned under",
            "pinched under",
            "crushed under",

            # Explicit pinch-point language
            "pinch point",
            "caught in a pinch point",

            # Explicit hand/finger caught language
            "finger was caught",
            "fingers were caught",
            "hand was caught",
            "hand caught",

            # Excavation/trench collapse patterns
            "excavation collapsed on",
            "trench collapsed on",
            "trench wall collapsed",
            "trench collapsed",
            "ditch caved in",
            "ditch caved",
        ],

        # -----------------------------------------------------
        # Falling-object exposure
        # -----------------------------------------------------
        "falling_object_exposure": [
            "falling object",
            "falling objects",
            "object fell onto the employee",
            "object fell on the employee",
            "object fell onto employee",
            "object fell on employee",
            "material fell onto the employee",
            "material fell on the employee",
            "material fell onto employee",
            "material fell on employee",
            "racks fell onto the employee",
            "racks fell on the employee",
            "racks fell onto employee",
            "racks fell on employee",
            "car fell off the jack",
            "car fell off a jack",
            "fell onto the employee",
            "fell on the employee",
        ],

        # -----------------------------------------------------
        # Struck-by
        # -----------------------------------------------------
        "struck_by": [
            "struck by",
            "struck the employee",
            "struck employee",
            "struck his",
            "struck her",
            "struck their",
            "strike the employee",
            "striking the employee",
            "striking employee",
            "hit by",
            "hit the employee",
            "hit employee",
            "hit his",
            "hit her",
            "hit their",
            "object struck",
            "tool struck",
            "equipment struck",
            "vehicle struck",
            "truck struck",
            "forklift struck",
            "kicked back and struck",
            "kicked back, striking",
            "was struck",
            "were struck",
            "t-boned",
            "ran into",
            "lacerated by",
            "rolled over onto",

            # Tool/object rebound or flyback
            "fly back",
            "flew back",
            "flyback",
        ],

        # -----------------------------------------------------
        # Fall from height
        # -----------------------------------------------------
        "fall_from_height": [
            "fell from",
            "fell off",
            "fell out of",
            "fell approximately",
            "fell about",
            "fell to the floor below",
            "fell to the ground",
            "fell to ground",
            "fell to the walking surface below",
            "fell to the working surface below",
            "fell to the walking/working surface below",
            "fell from the rear of the trailer",
            "fell off the tug",
            "fell out of the driver's cage",
            "fell from the driver's cage",
            "fell off the ladder",
            "fell off a ladder",
            "fell off scaffold",
            "fell from scaffold",
            "fell off the scaffold",
            "fell from the platform",
            "fell from the roof",

            # Specific elevated-position wording
            "knocked from the rig floor",

            # Elevator shaft
            "fell into an unguarded elevator shaft",
            "fell into the elevator shaft",
        ],

        # -----------------------------------------------------
        # Fire exposure
        # -----------------------------------------------------
        "fire_exposure": [
            "caught fire",
            "caught on fire",
            "vehicle caught fire",
            "equipment caught fire",
            "fire engulfed",
            "exposed to fire",
            "exposed to flames",
            "burned when",
            "burned by the fire",
            "burned by fire",
        ],

        # -----------------------------------------------------
        # Chemical exposure
        # -----------------------------------------------------
        "chemical_exposure": [
            "chemical splash",
            "chemical exposure",
            "splashed with sodium hydroxide",
            "sodium hydroxide splash",
            "sodium hydroxide contacted",
            "sodium hydroxide exposure",
            "showering the employee with sodium hydroxide",
            "showering employee with sodium hydroxide",
            "splashed with chemical",
            "splashed by chemical",
            "chemical splashed",
            "corrosive chemical",
            "chemical got into",
        ],
    }

    # ---------------------------------------------------------
    # Direct exposure indicators
    # ---------------------------------------------------------
    for exposure_label, indicators in exposure_indicators.items():
        for indicator in indicators:
            if indicator in text:
                exposure = exposure_label
                evidence["exposure"] = [indicator]
                break

        if exposure is not None:
            break

    # ---------------------------------------------------------
    # Contextual caught-between detection
    # ---------------------------------------------------------
    #
    # Some reports express a pinch/caught-between event without
    # using an exact "caught between" phrase.
    #
    # We keep these contextual patterns narrow to avoid treating
    # every occurrence of "between" as a safety exposure.
    # ---------------------------------------------------------

    if exposure is None:
        caught_between_contexts = [
            r"\b(?:finger|fingers|hand|hands|thumb|arm)\b"
            r".{0,60}\bbetween\b",

            r"\bbetween\b.{0,60}"
            r"\b(?:finger|fingers|hand|hands|thumb|arm)\b",

            r"\b(?:finger|fingers|hand|hands|thumb|arm)\b"
            r".{0,60}\bhinge area\b",

            r"\b(?:finger|fingers|hand|hands|thumb|arm)\b"
            r".{0,60}\bpinch point\b",
        ]

        for pattern in caught_between_contexts:
            match = re.search(pattern, text)

            if match:
                exposure = "caught_between"
                evidence["exposure"] = [match.group(0)]
                break

    # ---------------------------------------------------------
    # Fall-from-height contextual detection
    # ---------------------------------------------------------
    if exposure is None:
        elevated_fall_patterns = [
            r"\b(?:tossed|tossing|ejected|ejecting)\b"
            r".{0,100}\b\d+(?:\.\d+)?"
            r"(?:-\d+(?:\.\d+)?)?\s*(?:feet|ft)\b"
            r".{0,30}\b(?:below|down)\b",

            r"\b(?:tossed|tossing|ejected|ejecting)\b"
            r".{0,100}\b(?:floor|ground|surface)\b"
            r".{0,40}\bbelow\b",
        ]

        for pattern in elevated_fall_patterns:
            match = re.search(pattern, text)

            if match:
                exposure = "fall_from_height"
                evidence["exposure"] = [match.group(0)]
                break

    # ---------------------------------------------------------
    # Numerical fall-height detection
    # ---------------------------------------------------------
    if exposure is None:
        fall_height_match = re.search(
            r"\bfell\s+(?:approximately\s+|about\s+)?"
            r"\d+(?:\.\d+)?"
            r"(?:-\d+(?:\.\d+)?)?"
            r"\s*(?:feet|ft)\b",
            text,
        )

        if fall_height_match:
            exposure = "fall_from_height"
            evidence["exposure"] = [fall_height_match.group(0)]

    # ---------------------------------------------------------
    # Barrier failure extraction
    # ---------------------------------------------------------
       # ---------------------------------------------------------
    # Barrier failure extraction
    # ---------------------------------------------------------
    #
    # Only classify a barrier failure when the narrative gives
    # explicit evidence that a control/procedure was missing,
    # inadequate, violated, or unsafe.
    #
    # Current contract remains scalar: one barrier failure label.
    # ---------------------------------------------------------

    barrier_indicators = {
        # -----------------------------------------------------
        # Inadequate fall protection
        # -----------------------------------------------------
        "inadequate_fall_protection": [
            "fall protection was not worn",
            "fall protection was not provided",
            "fall protection was missing",
            "fall protection was not in place",
            "no fall protection",
            "without fall protection",
            "inadequate fall protection",
        ],

        # -----------------------------------------------------
        # Missing guard
        # -----------------------------------------------------
        "missing_guard": [
            "guard was missing",
            "guardrail was missing",
            "missing guard",
            "missing guardrail",
            "no guard",
            "without a guard",
            "unguarded elevator shaft",
            "unguarded shaft",
            "unguarded opening",
            "unguarded edge",
        ],

        # -----------------------------------------------------
        # Failed guard
        # -----------------------------------------------------
        "failed_guard": [
            "guard gave away",
            "guardrail gave away",
            "guard failed",
            "guardrail failed",
            "failed guard",
            "failed guardrail",
        ],

        # -----------------------------------------------------
        # Unsafe positioning
        # -----------------------------------------------------
        "unsafe_positioning": [
            "standing in the line of fire",
            "positioned in the line of fire",
            "unsafe position",
            "unsafe positioning",
        ],

        # -----------------------------------------------------
        # SOP violation
        # -----------------------------------------------------
        "SOP_violation": [
            "did not follow the procedure",
            "failed to follow the procedure",
            "procedure was not followed",
            "not following the procedure",
            "violated the procedure",
            "did not follow the sop",

            # Explicit lockout/tagout failures
            "not locked/tagged out",
            "not locked out",
            "not tagged out",
            "was not locked/tagged out",
            "was not locked out",
            "was not tagged out",
            "not locked or tagged out",
            "lockout/tagout was not performed",
            "lockout tagout was not performed",
            "lockout/tagout was not used",
            "lockout tagout was not used",
        ],
    }

    # ---------------------------------------------------------
    # Direct barrier indicators
    # ---------------------------------------------------------
    for barrier_label, indicators in barrier_indicators.items():
        for indicator in indicators:
            if indicator in text:
                barrier_failure = barrier_label
                evidence["barrier_failure"] = [indicator]
                break

        if barrier_failure is not None:
            break

    # ---------------------------------------------------------
    # Contextual unsafe-positioning detection
    # ---------------------------------------------------------
    #
    # These cases do not use the literal phrase "unsafe
    # positioning", but the narrative explicitly describes
    # an unsafe position/intervention.
    #
    # Keep these patterns narrow to avoid broad false positives.
    # ---------------------------------------------------------
    if barrier_failure is None:

        unsafe_positioning_patterns = [
            # Working from an improvised object placed on
            # forklift forks.
            r"\b(?:working|standing|painting|spray[- ]painting)\b"
            r".{0,100}\b(?:box|bin|container)\b"
            r".{0,100}\bon the forks of (?:a|the) forklift\b",

            # Manually attempting to stop rolling equipment
            # by placing an object under a tire.
            r"\battempted to stop\b"
            r".{0,100}\b(?:forklift|vehicle|equipment)\b"
            r".{0,100}\bfrom rolling\b"
            r".{0,100}\bplacing\b"
            r".{0,80}\bunder the (?:tire|wheel)\b",
        ]

        for pattern in unsafe_positioning_patterns:
            match = re.search(pattern, text)

            if match:
                barrier_failure = "unsafe_positioning"
                evidence["barrier_failure"] = [match.group(0)]
                break

    # ---------------------------------------------------------
    # Equipment extraction
    # ---------------------------------------------------------
    equipment_indicators = {
        "scissor_lift": [
            "scissor lift",
        ],
        "forklift": [
            "forklift",
            "reach truck",
            "walkie rider",
        ],
        "crane": [
            "overhead crane",
            "eot crane",
            "crane",
        ],
        "backhoe": [
            "backhoe",
        ],
        "conveyor": [
            "conveyor",
        ],
        "ladder": [
            "ladder",
        ],
        "scaffold": [
            "scaffold",
            "scaffolding",
        ],
        "pipeline": [
            "pipeline",
            "drain line",
            "sodium hydroxide line",
        ],
        "trailer": [
            "trailer",
        ],
        "truck": [
            "truck",
            "tractor trailer",
        ],
        "vehicle": [
            "vehicle",
            "order picker",
            "atv",
            "golf cart",
            "tug",
        ],
        "machinery": [
            "machinery",
            "machine",
            "power press",
            "press machine",
            "brake press",
            "chop saw",
            "cutoff saw",
            "lathe",
            "edger",
            "auto-trimmer",
            "tape machine",
        ],
        "cable": [
            "cable tray",
            "cable",
        ],
    }

    detected_equipment = []

    for equipment_label, indicators in equipment_indicators.items():
        for indicator in indicators:
            if indicator in text:
                detected_equipment.append(equipment_label)
                break

    if "forklift" in detected_equipment:
        detected_equipment = [
            label
            for label in detected_equipment
            if label not in {"truck", "vehicle"}
        ]

    if "scissor_lift" in detected_equipment:
        detected_equipment = [
            label
            for label in detected_equipment
            if label not in {"vehicle"}
        ]

    if "trailer" in detected_equipment and "truck" in detected_equipment:
        detected_equipment.remove("trailer")

    if detected_equipment:
        equipment = "|".join(dict.fromkeys(detected_equipment))
        evidence["equipment"] = detected_equipment

    # ---------------------------------------------------------
    # Activity extraction
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # 1. Maintenance overrides
    # ---------------------------------------------------------
    maintenance_override_indicators = [
        "remove a jam",
        "remove the jam",
        "remove it",
        "clearing a plug",
        "clear the plug",
        "dislodge",
        "free the tilt lock",
        "repairing",
        "repair",
        "fixing",
        "fix",
        "replacing",
        "replace",
        "disconnecting",
        "disconnect",
        "dismantling",
        "dismantle",
        "servicing",
        "service",
        "preparing to clean",
        "cleaning the equipment",
        "cleaning equipment",
        "cleaning the machine",
        "cleaning machine",
        "cleaning the press machine",
        "cleaning a press machine",
        "cleaning out top flash",
        "cleaning out top flash and trimmings",
        "maintenance",
    ]

    for indicator in maintenance_override_indicators:
        if indicator in text:
            activity = "maintenance"
            evidence["activity"] = [indicator]
            break

    # ---------------------------------------------------------
    # 2. Explicit equipment operation
    # ---------------------------------------------------------
    if activity is None:
        equipment_operation_indicators = [
            "operating a forklift",
            "operating forklifts",
            "operating a vehicle",
            "operating the vehicle",
            "operating an atv",
            "operating the atv",
            "operating an order picker",
            "operating a reach truck",
            "driving a forklift",
            "driving the forklift",
            "driving a work vehicle",
            "driving the vehicle",
            "driving an atv",
            "driving the atv",
            "driving a truck",
            "driving the truck",
            "driving a tractor",
            "driving a golf cart",
            "reversing a forklift",
            "reversing the forklift",
            "traveling on a forklift",
            "traveling in a forklift",
            "traveling with the forklift",
            "boarded a forklift",
            "using a forklift to",
            "using the forklift to",
            "using an atv",
            "using the atv",
            "operating",
            "operate",
            "running",
            "traveling",
            "riding",
        ]

        for indicator in equipment_operation_indicators:
            if indicator in text:
                activity = "equipment_operation"
                evidence["activity"] = [indicator]
                break

    # ---------------------------------------------------------
    # 3. Electrical work
    # ---------------------------------------------------------
    if activity is None:
        electrical_indicators = [
            "switching and grounding",
            "electrical wiring",
            "energized conductor",
            "electrical work",
            "powerline switches",
            "electrical pole",
            "ceiling light fixture",
            "light fixture",
            "changing light fixtures",
            "change light fixtures",
        ]

        for indicator in electrical_indicators:
            if indicator in text:
                activity = "electrical_work"
                evidence["activity"] = [indicator]
                break

    # ---------------------------------------------------------
    # 4. Excavation
    # ---------------------------------------------------------
    if activity is None:
        excavation_indicators = [
            "excavation",
            "excavating",
            "digging a trench",
            "digging",
            "trench",
            "ditch",
        ]

        for indicator in excavation_indicators:
            if indicator in text:
                activity = "excavation"
                evidence["activity"] = [indicator]
                break

    # ---------------------------------------------------------
    # 5. Lifting operation
    # ---------------------------------------------------------
    if activity is None:
        lifting_indicators = [
            "lifting operation",
            "lifting chain",
            "rigging up",
            "rigging",
            "suspended load",
            "lowering the load",
        ]

        for indicator in lifting_indicators:
            if indicator in text:
                activity = "lifting"
                evidence["activity"] = [indicator]
                break

    # ---------------------------------------------------------
    # 6. Installation
    # ---------------------------------------------------------
    if activity is None:
        installation_indicators = [
            "installing",
            "installation",
            "installed",
        ]

        for indicator in installation_indicators:
            if indicator in text:
                activity = "installation"
                evidence["activity"] = [indicator]
                break

    # ---------------------------------------------------------
    # 7. Material handling
    # ---------------------------------------------------------
    if activity is None:
        material_handling_indicators = [
            "loading",
            "unloading",
            "stacking",
            "stack",
            "stocking",
            "stock",
            "transferring",
            "transfer",
            "carrying",
            "handling",
            "picking up",
            "moving materials",
            "moving material",
            "move the",
            "moving the",
            "move a",
            "moving a",
            "move an",
            "moving an",
            "move fiber",
            "moving fiber",
            "lifting boxes",
            "lifting a box",
            "lifting a case",
            "lifting a jug",
            "lifting a tote",
            "lifting totes",
            "lifting return totes",
            "lifting a dryer",
            "lifting the machine",
            "lifting the bin",
            "lifting the",
        ]

        for indicator in material_handling_indicators:
            if indicator in text:
                activity = "material_handling"
                evidence["activity"] = [indicator]
                break

    # ---------------------------------------------------------
    # 8. Cleaning
    # ---------------------------------------------------------
    if activity is None:
        cleaning_indicators = [
            "power washing",
            "power washing a",
            "cleaning",
        ]

        for indicator in cleaning_indicators:
            if indicator in text:
                activity = "cleaning"
                evidence["activity"] = [indicator]
                break

    # ---------------------------------------------------------
    # 9. Transport
    # ---------------------------------------------------------
    if activity is None:
        transport_indicators = [
            "transporting",
            "transport",
            "delivering",
            "delivery",
            "deliver",
        ]

        for indicator in transport_indicators:
            if indicator in text:
                activity = "transport"
                evidence["activity"] = [indicator]
                break

    # ---------------------------------------------------------
    # Return structured safety report
    # ---------------------------------------------------------
    return {
        "report_id": report.get("report_id"),
        "timestamp": report.get("timestamp"),
        "site": report.get("site"),
        "source_type": report.get("source_type", "unknown"),
        "narrative": narrative,
        "hazard": hazard,
        "activity": activity,
        "equipment": equipment,
        "barrier_failure": barrier_failure,
        "exposure": exposure,
        "severity_potential": None,
        "evidence": evidence,
    }