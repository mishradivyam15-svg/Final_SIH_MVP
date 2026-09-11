"""
Canonical OSHA EventTitle → SIF precursor label mapping.

Maps OSHA Severe Injury Report EventTitle values to the project's
SIF precursor safety signal taxonomy for ML training label generation.

Mapping philosophy:
  - Only map when EventTitle provides clear evidence for the label
  - Unmappable events receive None (not guessed)
  - None labels serve as negative training examples
  - Each mapping carries a confidence level (high / medium / low)
  - EventTitle directly describes exposure mechanism (how the person
    was injured) and indirectly implies hazard (the dangerous condition)

Usage:
    from ai.label_mapping import map_event_title
    from ai.label_mapping import HAZARD_LABELS, EXPOSURE_LABELS

    result = map_event_title("Caught in running equipment or machinery")
    # {"hazard": "moving_machinery", "exposure": "caught_in",
    #  "confidence": "high"}
"""


# ── Full taxonomy ───────────────────────────────────────────────
#
# All valid labels in the SIF precursor safety signal taxonomy.
# Source: docs/safety_signal_taxonomy.md, docs/extraction_rules.md

HAZARD_LABELS = (
    "working_at_height",
    "moving_machinery",
    "mobile_equipment",
    "electrical_energy",
    "excavation",
    "falling_object",
    "line_of_fire",
    "lifting_operation",
    "chemical_exposure",
    "stored_energy",
    "slip_trip_fall",
    "confined_space",
    "fire_or_hot_work",
    "hydrocarbon_or_process_hazard",
)

EXPOSURE_LABELS = (
    "fall_from_height",
    "caught_in",
    "caught_between",
    "struck_by",
    "electrical_exposure",
    "fire_exposure",
    "chemical_exposure",
    "falling_object_exposure",
)

# Labels with zero EventTitle-derived training samples.
# These require narrative-based labeling in a future phase.
NARRATIVE_ONLY_LABELS = frozenset({
    "lifting_operation",
    "confined_space",
    "hydrocarbon_or_process_hazard",
})


# ── Ordered mapping rules ──────────────────────────────────────
#
# Each rule: (pattern, hazard, exposure, confidence)
#
# Rules are checked in order against the lowercased EventTitle
# using substring matching.  First match wins.
#
# IMPORTANT:
#   - More specific patterns MUST precede more general ones.
#   - Sections are ordered to prevent cross-category mismatches.
#   - None means "no label for this field" (intentional).

_RULES = [

    # ============================================================
    # 1. ELECTRICAL
    # ============================================================
    ("exposure to electric arc",
     "electrical_energy", "electrical_exposure", "high"),
    ("direct exposure to electricity",
     "electrical_energy", "electrical_exposure", "high"),
    ("indirect exposure to electricity",
     "electrical_energy", "electrical_exposure", "high"),
    ("exposure to electricity",
     "electrical_energy", "electrical_exposure", "high"),

    # ============================================================
    # 2. EXCAVATION / TRENCH  (before generic collapse rules)
    # ============================================================
    ("excavation or trenching cave-in",
     "excavation", "caught_between", "high"),
    ("collapse, engulfment  open trench or excavation",
     "excavation", "caught_between", "high"),
    ("collapse, engulfment  open trench",
     "excavation", "caught_between", "high"),

    # ============================================================
    # 3. FIRE / IGNITION  (before explosion to disambiguate)
    # ============================================================
    ("ignition of vapors",
     "fire_or_hot_work", "fire_exposure", "high"),
    ("ignition of clothing",
     "fire_or_hot_work", "fire_exposure", "high"),
    ("flash fire",
     "fire_or_hot_work", "fire_exposure", "high"),
    ("vehicle or machinery fire",
     "fire_or_hot_work", "fire_exposure", "high"),
    ("forest or brush fire",
     "fire_or_hot_work", "fire_exposure", "high"),
    ("forest fire or wildfire",
     "fire_or_hot_work", "fire_exposure", "high"),
    ("forest fire",
     "fire_or_hot_work", "fire_exposure", "high"),
    ("wildfire",
     "fire_or_hot_work", "fire_exposure", "high"),
    ("nonstructural fire",
     "fire_or_hot_work", "fire_exposure", "medium"),
    ("structural fire",
     "fire_or_hot_work", "fire_exposure", "medium"),
    ("small-scale",
     "fire_or_hot_work", "fire_exposure", "medium"),
    ("collapsing building, structure, or structural element during fire",
     "fire_or_hot_work", "fire_exposure", "medium"),
    # "fire or explosion" catches "Fire or explosion, unspecified"
    ("fire or explosion",
     "fire_or_hot_work", "fire_exposure", "medium"),
    # "explosion or fire" catches "Explosion or fire on water vehicle"
    ("explosion or fire",
     "fire_or_hot_work", "fire_exposure", "medium"),
    ("fires, explosions onboard",
     "fire_or_hot_work", "fire_exposure", "medium"),
    ("explosions and fires",
     "fire_or_hot_work", "fire_exposure", "medium"),
    ("fire, unspecified",
     "fire_or_hot_work", "fire_exposure", "medium"),
    ("fire  unspecified",
     "fire_or_hot_work", "fire_exposure", "medium"),

    # ============================================================
    # 4. EXPLOSION  (stored_energy — after fire rules)
    # ============================================================
    ("explosion of pressure vessel",
     "stored_energy", None, "high"),
    ("dust explosion",
     "stored_energy", None, "high"),
    ("explosion of nonpressurized",
     "stored_energy", None, "medium"),
    ("demolition or blasting",
     "stored_energy", None, "medium"),
    ("intentionally set explosion",
     "stored_energy", None, "medium"),
    # Catch-all for remaining explosion titles
    ("explosion",
     "stored_energy", None, "medium"),

    # ============================================================
    # 5. CHEMICAL / SUBSTANCE EXPOSURE  (before generic "exposure")
    # ============================================================
    ("inhalation of harmful substance",
     "chemical_exposure", "chemical_exposure", "high"),
    ("ingestion of harmful substance",
     "chemical_exposure", "chemical_exposure", "high"),
    ("exposure through intact skin",
     "chemical_exposure", "chemical_exposure", "high"),
    ("exposure through intact tissue",
     "chemical_exposure", "chemical_exposure", "high"),
    # More-specific "exposure to" patterns before generic
    ("exposure to other harmful substance",
     "chemical_exposure", "chemical_exposure", "medium"),
    ("exposure to harmful substance through",
     "chemical_exposure", "chemical_exposure", "medium"),
    ("exposure to harmful substance multiple",
     "chemical_exposure", "chemical_exposure", "medium"),
    ("exposure through medical injection",
     "chemical_exposure", "chemical_exposure", "low"),
    # Needlestick without actual substance exposure
    ("needlestick without exposure",
     None, None, None),
    ("exposure through unintentional needlestick",
     "chemical_exposure", "chemical_exposure", "low"),
    ("unintentional needlestick",
     "chemical_exposure", "chemical_exposure", "low"),
    ("exposure through scratch",
     "chemical_exposure", "chemical_exposure", "low"),
    ("exposure through wound",
     "chemical_exposure", "chemical_exposure", "low"),
    ("exposure through skin, eyes",
     "chemical_exposure", "chemical_exposure", "medium"),
    ("multiple types of exposures through skin",
     "chemical_exposure", "chemical_exposure", "medium"),
    ("multiple types of exposures through",
     "chemical_exposure", "chemical_exposure", "medium"),
    # Oxygen-related
    ("depletion of oxygen",
     "chemical_exposure", None, "medium"),
    ("oxygen displacement",
     "chemical_exposure", None, "medium"),
    ("oxygen deficiency",
     "chemical_exposure", None, "medium"),
    # Not chemical
    ("choking on object",
     None, None, None),
    ("drowning, submersion",
     None, None, None),
    # Broader "exposure to harmful" catch-alls
    ("exposure to harmful substances or environments",
     "chemical_exposure", "chemical_exposure", "low"),
    ("exposure to harmful substances, environments",
     "chemical_exposure", "chemical_exposure", "low"),
    ("exposure to harmful substances",
     "chemical_exposure", "chemical_exposure", "medium"),
    ("exposure to harmful substance",
     "chemical_exposure", "chemical_exposure", "medium"),

    # ============================================================
    # 6. HEAT / COLD / ENVIRONMENTAL
    # ============================================================
    ("exposure to environmental heat",
     "fire_or_hot_work", None, "medium"),
    ("exposure to environmental cold",
     None, None, None),
    ("contact with hot objects or substances",
     "fire_or_hot_work", None, "medium"),
    ("contact with cold objects",
     None, None, None),
    ("exposure to temperature extremes",
     None, None, None),
    ("exposure to light",
     None, None, None),
    ("exposure to change in water pressure",
     None, None, None),
    ("exposure to change in air pressure",
     None, None, None),

    # ============================================================
    # 7. STRUCK AGAINST → null/null  (user decision)
    #    Must precede all "struck by" rules.
    # ============================================================
    ("struck against",
     None, None, None),
    ("walked or ran into stationary",
     None, None, None),

    # ============================================================
    # 8. STRUCK BY FALLING  (specific before general "struck by")
    #    Vehicle-part / vehicle patterns first, then falling-object.
    # ============================================================
    ("struck by other falling powered vehicle",
     "mobile_equipment", "struck_by", "medium"),
    ("struck by falling part of powered vehicle",
     None, "struck_by", "medium"),
    ("struck by falling part of vehicle",
     None, "struck_by", "medium"),
    ("struck by propelled, falling, or suspended",
     "line_of_fire", "struck_by", "medium"),
    ("struck by object falling from vehicle",
     "falling_object", "falling_object_exposure", "high"),
    ("struck by falling object",
     "falling_object", "falling_object_exposure", "high"),
    ("struck by other falling",
     "falling_object", "falling_object_exposure", "high"),
    ("struck by falling",
     "falling_object", "falling_object_exposure", "high"),

    # ============================================================
    # 9. STRUCK BY POWERED EQUIPMENT / VEHICLE
    # ============================================================
    ("struck by running powered equipment  irregular movement",
     "line_of_fire", "struck_by", "high"),
    ("struck by running powered equipment",
     "moving_machinery", "struck_by", "high"),
    ("struck or run over by rolling powered vehicle",
     "mobile_equipment", "struck_by", "high"),
    ("struck by rolling powered vehicle",
     "mobile_equipment", "struck_by", "high"),
    ("struck by rolling powered",
     "mobile_equipment", "struck_by", "high"),
    ("struck by powered vehicle tipping",
     "mobile_equipment", "struck_by", "high"),
    ("struck by powered vehicle",
     "mobile_equipment", "struck_by", "high"),

    # ============================================================
    # 10. PEDESTRIAN STRUCK BY VEHICLE
    # ============================================================
    ("pedestrian struck",
     "mobile_equipment", "struck_by", "high"),
    ("non-passenger struck by rail",
     "mobile_equipment", "struck_by", "medium"),

    # ============================================================
    # 11. STRUCK BY SWINGING / DOOR / GATE
    # ============================================================
    ("struck by swinging part of powered vehicle",
     "mobile_equipment", "struck_by", "high"),
    ("struck by or caught in swinging door",
     None, "struck_by", "medium"),
    ("struck by swinging or slipping",
     "line_of_fire", "struck_by", "medium"),
    ("struck by suspended or swinging",
     "line_of_fire", "struck_by", "medium"),
    ("struck by door",
     None, "struck_by", "medium"),

    # ============================================================
    # 12. STRUCK BY FLYING / DISCHARGED / PROPELLED
    # ============================================================
    ("struck by dislodged flying",
     "line_of_fire", "struck_by", "high"),
    ("struck by dislodged or detached",
     "line_of_fire", "struck_by", "high"),
    ("struck by discharged",
     "line_of_fire", "struck_by", "high"),
    ("struck by other propelled",
     "line_of_fire", "struck_by", "medium"),
    ("struck by propelled",
     "line_of_fire", "struck_by", "medium"),
    ("struck by thrown",
     "line_of_fire", "struck_by", "medium"),

    # ============================================================
    # 13. STRUCK BY ROLLING / SHIFTING / TIPPING
    # ============================================================
    ("struck by rolling, sliding",
     "line_of_fire", "struck_by", "medium"),
    ("struck by shifting load",
     "line_of_fire", "struck_by", "medium"),
    ("struck by object tipping",
     "line_of_fire", "struck_by", "medium"),
    ("struck by rolling object",
     "line_of_fire", "struck_by", "medium"),

    # ============================================================
    # 14. STRUCK BY OBJECT (general / catch-all)
    # ============================================================
    ("struck by object or equipment dropped",
     None, "struck_by", "medium"),
    ("struck by object dropped",
     None, "struck_by", "medium"),
    ("struck by object or equipment rolling",
     None, "struck_by", "medium"),
    ("struck by object or equipment",
     None, "struck_by", "low"),
    ("vehicle struck by falling",
     None, "struck_by", "low"),
    ("vehicle struck",
     None, "struck_by", "low"),

    # ============================================================
    # 15. INJURED BY OBJECT  (before caught-in patterns)
    # ============================================================
    ("injured by slipping or swinging object",
     "line_of_fire", "struck_by", "medium"),
    ("injured by slipping or swinging",
     "line_of_fire", "struck_by", "medium"),
    ("injured by object breaking in hand",
     None, "struck_by", "medium"),
    ("injured by object pushed or pulled",
     None, "struck_by", "low"),
    ("injured by object handled",
     None, "struck_by", "low"),
    ("injured by handheld object",
     None, "struck_by", "low"),
    ("injured by object",
     None, "struck_by", "low"),

    # ============================================================
    # 16. CAUGHT IN RUNNING MACHINERY
    # ============================================================
    ("caught in running equipment or machinery",
     "moving_machinery", "caught_in", "high"),
    ("caught, entangled in running powered equipment",
     "moving_machinery", "caught_in", "high"),
    ("entangled in other object or equipment",
     None, "caught_in", "medium"),
    ("entangled in non-running",
     None, "caught_in", "medium"),
    ("entangled in",
     None, "caught_in", "medium"),

    # ============================================================
    # 17. CAUGHT IN / COMPRESSED (generic — after machinery)
    # ============================================================
    ("caught in or compressed by equipment or objects",
     None, "caught_in", "medium"),

    # ============================================================
    # 18. CAUGHT / COMPRESSED BETWEEN
    # ============================================================
    ("compressed or pinched by shifting",
     None, "caught_between", "high"),
    ("compressed or pinched between",
     None, "caught_between", "high"),
    ("compressed between running",
     None, "caught_between", "high"),
    ("caught or wedged between",
     None, "caught_between", "high"),
    ("caught between rolling",
     None, "caught_between", "high"),
    ("part of occupant",
     None, "caught_between", "high"),

    # ============================================================
    # 19. COLLAPSE / ENGULFMENT  (after excavation)
    # ============================================================
    ("struck, caught, or crushed in collapsing",
     None, "caught_between", "medium"),
    ("struck, caught, or crushed in other collapsing",
     None, "caught_between", "medium"),
    ("collapse, engulfment  building",
     None, "caught_between", "medium"),
    ("collapse, engulfment  loose materials",
     None, "caught_between", "medium"),
    ("engulfment in other collapsing",
     None, "caught_between", "medium"),
    ("collapse, engulfment",
     None, "caught_between", "medium"),

    # ============================================================
    # 20. FALL FROM VEHICLE  (before general fall patterns)
    # ============================================================
    # Rail/water vehicle falls → null (not in taxonomy)
    ("fall or jump from and struck by rail vehicle",
     None, None, None),
    ("fall or jump from rail vehicle",
     None, None, None),
    ("fall, jump from and struck by rail vehicle",
     None, None, None),
    ("fall, jump from rail vehicle",
     None, None, None),
    ("fall or jump from water vehicle",
     None, None, None),
    ("fall, jump from water vehicle",
     None, None, None),
    ("fall, jump from and struck by water vehicle",
     None, None, None),
    # Motorized vehicle falls → mobile_equipment / fall_from_height
    ("fall or jump from and struck by same vehicle",
     "mobile_equipment", "fall_from_height", "medium"),
    ("fall or jump from and struck by another vehicle",
     "mobile_equipment", "fall_from_height", "medium"),
    ("fall or jump from vehicle",
     "mobile_equipment", "fall_from_height", "medium"),

    # ============================================================
    # 21. FALL TO LOWER LEVEL
    # ============================================================
    # Near-miss / curtailed → null
    ("fall to lower level  caught self",
     None, None, None),
    ("fall or jump curtailed",
     None, None, None),
    # All fall-to-lower-level variants
    ("fall to lower level from collapsing",
     "working_at_height", "fall_from_height", "high"),
    ("fall from collapsing structure",
     "working_at_height", "fall_from_height", "high"),
    ("fall to lower level resulting from",
     "working_at_height", "fall_from_height", "high"),
    ("fall to lower level resulting in",
     "working_at_height", "fall_from_height", "high"),
    ("fall to lower level",
     "working_at_height", "fall_from_height", "high"),
    ("other fall to lower level",
     "working_at_height", "fall_from_height", "high"),
    ("fall through surface or existing opening",
     "working_at_height", "fall_from_height", "high"),
    ("other jump to lower level",
     "working_at_height", "fall_from_height", "medium"),
    ("jump to lower level",
     "working_at_height", "fall_from_height", "medium"),
    ("jump from collapsing structure",
     "working_at_height", "fall_from_height", "medium"),

    # ============================================================
    # 22. FALL ON SAME LEVEL
    # ============================================================
    ("fall on same level",
     "slip_trip_fall", None, "high"),
    ("fall onto or against object on same level",
     "slip_trip_fall", None, "medium"),

    # ============================================================
    # 23. SLIP / TRIP  (with or without fall)
    # ============================================================
    ("fall, slip, trip",
     "slip_trip_fall", None, "medium"),
    ("slip, trip, stumble while stepping",
     "slip_trip_fall", None, "medium"),
    ("slip, trip, stumble on same level",
     "slip_trip_fall", None, "medium"),
    ("slip, trip, stumble or fall",
     "slip_trip_fall", None, "medium"),
    ("slip, trip, stumble",
     "slip_trip_fall", None, "medium"),
    ("slip on substance without fall",
     "slip_trip_fall", None, "medium"),
    ("slip on vehicle without fall",
     "slip_trip_fall", None, "medium"),
    ("slip without fall",
     "slip_trip_fall", None, "medium"),
    ("slip or trip without fall",
     "slip_trip_fall", None, "medium"),
    ("trip over an object without fall",
     "slip_trip_fall", None, "medium"),
    ("trip over self without fall",
     "slip_trip_fall", None, "medium"),
    ("trip from stepping into",
     "slip_trip_fall", None, "medium"),
    ("trip on uneven surface",
     "slip_trip_fall", None, "medium"),
    ("trip on vehicle without fall",
     "slip_trip_fall", None, "medium"),
    ("trip without fall",
     "slip_trip_fall", None, "medium"),
    ("stepped on object",
     "slip_trip_fall", None, "low"),
    ("stepped or knelt on object",
     "slip_trip_fall", None, "low"),

    # ============================================================
    # 24. FALL — OTHER / UNSPECIFIED → null/null
    #     Per approved plan: do not guess between
    #     working_at_height and slip_trip_fall.
    # ============================================================
    ("fall while sitting",
     None, None, None),
    ("fall from pedal cycle",
     None, None, None),
    ("fall from skis",
     None, None, None),
    ("fall on water vehicle",
     None, None, None),
    ("fall on aircraft",
     None, None, None),
    ("fall, contact incident",
     None, None, None),
    ("fall onto or against",
     None, None, None),
    ("fall and catch",
     None, None, None),

    # ============================================================
    # 25. VEHICLE NONCOLLISION  (specific sub-patterns)
    # ============================================================
    ("noncollision  struck by shifting",
     "line_of_fire", "struck_by", "medium"),
    ("noncollision  fall or jump from and struck by",
     "mobile_equipment", "fall_from_height", "medium"),
    ("noncollision  fall or jump from",
     "mobile_equipment", "fall_from_height", "medium"),
    ("noncollision  vehicle overturn",
     "mobile_equipment", None, "medium"),
    ("noncollision  jack-knifed",
     "mobile_equipment", None, "medium"),

    # ============================================================
    # 26. VEHICLE COLLISION / TRANSPORT
    # ============================================================
    ("collision with stationary object",
     "mobile_equipment", "struck_by", "medium"),
    ("collision between",
     "mobile_equipment", "struck_by", "medium"),
    ("collision with other vehicle",
     "mobile_equipment", "struck_by", "medium"),
    ("collision with moving object",
     "mobile_equipment", "struck_by", "medium"),
    ("collision with object",
     "mobile_equipment", "struck_by", "medium"),
    ("collision on skis",
     None, None, None),
    ("collision in nonroadway",
     "mobile_equipment", "struck_by", "low"),
    ("collision in roadway",
     "mobile_equipment", "struck_by", "low"),
    ("jack-knifed or overturned",
     "mobile_equipment", None, "medium"),
    ("ran off driving surface",
     "mobile_equipment", None, "medium"),
    ("ran off roadway",
     "mobile_equipment", None, "medium"),
    ("sudden start or stop",
     "mobile_equipment", None, "medium"),
    ("struck bump, hole",
     "mobile_equipment", None, "medium"),
    ("moving in opposite directions",
     "mobile_equipment", "struck_by", "medium"),
    ("moving in same direction",
     "mobile_equipment", "struck_by", "low"),

    # ============================================================
    # 27. NULL — Violence / intentional
    # ============================================================
    ("shooting",      None, None, None),
    ("stabbing",      None, None, None),
    ("hitting, kicking, beating",  None, None, None),
    ("intentional injury",         None, None, None),
    ("intentional violence",       None, None, None),
    ("intentional self-harm",      None, None, None),
    ("self-inflicted",             None, None, None),
    ("bombing",       None, None, None),
    ("strangulation", None, None, None),
    ("threat, verbal", None, None, None),
    ("violent acts",  None, None, None),
    ("multiple violent acts",      None, None, None),
    ("horseplay",     None, None, None),
    ("gun discharge", None, None, None),

    # ============================================================
    # 28. NULL — Person contact
    # ============================================================
    ("injured by physical contact",    None, None, None),
    ("injured by person",              None, None, None),
    ("injury by person",               None, None, None),
    ("injury by other person",         None, None, None),
    ("contact with other person",      None, None, None),
    ("contact with animals",           None, None, None),
    ("multiple types of contact with animals",  None, None, None),
    ("multiple types of animal",       None, None, None),

    # ============================================================
    # 29. NULL — Animal / insect
    # ============================================================
    ("animal bite",           None, None, None),
    ("other animal bite",     None, None, None),
    ("venomous animal bite",  None, None, None),
    ("non-venomous animal",   None, None, None),
    ("nonvenomous insect",    None, None, None),
    ("bite or sting",         None, None, None),
    ("bites and stings",      None, None, None),
    ("stings and venomous",   None, None, None),
    ("kicked by animal",      None, None, None),
    ("gored or rammed",       None, None, None),
    ("gored, rammed",         None, None, None),
    ("trampled",              None, None, None),
    ("stepped on, kicked, trampled",   None, None, None),
    ("mauled",                None, None, None),
    ("bitten and struck by animal",    None, None, None),
    ("bitten or stung",       None, None, None),
    ("thrown, fell, or jumped from animal",  None, None, None),
    ("animal and insect",     None, None, None),
    ("animal transportation", None, None, None),
    ("animal and other non-motorized", None, None, None),
    ("struck by animal",      None, None, None),

    # ============================================================
    # 30. NULL — Overexertion / bodily motion
    # ============================================================
    ("overexertion",       None, None, None),
    ("exertion",           None, None, None),
    ("bending, crawling",  None, None, None),
    ("climbing or stepping", None, None, None),
    ("kneeling",           None, None, None),
    ("walking, without",   None, None, None),
    ("running, without",   None, None, None),
    ("standing, standing up",  None, None, None),
    ("standing up, sitting",   None, None, None),
    ("sitting, sitting down",  None, None, None),
    ("boarding, alighting",    None, None, None),
    ("bodily conditions",  None, None, None),
    ("bodily position",    None, None, None),
    ("twisting, reaching", None, None, None),
    ("sustained bodily",   None, None, None),
    ("multiple types of bodily",   None, None, None),
    ("multiple types of overexertion",  None, None, None),

    # ============================================================
    # 31. NULL — Transport other (aircraft, rail, water, pedal, ski)
    # ============================================================
    ("aircraft incident",  None, None, None),
    ("aircraft crash",     None, None, None),
    ("in-flight crash",    None, None, None),
    ("water vehicle incident",     None, None, None),
    ("water vehicle collision",    None, None, None),
    ("water vehicle or propeller", None, None, None),
    ("capsized or sinking",        None, None, None),
    ("rail vehicle incident",      None, None, None),
    ("rail vehicle collision",     None, None, None),
    ("derailment",         None, None, None),
    ("collision between rail",     None, None, None),
    ("collision between two rail", None, None, None),
    ("pedal cycle incident",       None, None, None),
    ("pedal cycle collision",      None, None, None),
    ("ski, snowboard",     None, None, None),
    ("parachuting",        None, None, None),
    ("machinery or equipment incident on water",   None, None, None),
    ("exposure incident onboard water",            None, None, None),
    ("overexertion incidents onboard water",       None, None, None),

    # ============================================================
    # 32. NULL — Rubbed / abraded
    # ============================================================
    ("rubbed or abraded",  None, None, None),

    # ============================================================
    # 33. NULL — Contact other
    # ============================================================
    ("contact with non-running",       None, None, None),
    ("other contact with non-running", None, None, None),
    ("contact incidents",              None, None, None),
    ("contact with objects and equipment",  None, None, None),
    ("contact  n.e.c.",  None, None, None),

    # ============================================================
    # 34. NULL — Generic / unclassifiable
    # ============================================================
    ("nonclassifiable",    None, None, None),
    ("event or exposure  unspecified",         None, None, None),
    ("transportation incident, unspecified",   None, None, None),
    ("transportation incidents  unspecified",  None, None, None),
    ("roadway incident involving",             None, None, None),
    ("nonroadway incident involving",          None, None, None),
    ("pedestrian vehicular incident",          None, None, None),
    ("pedestrian incidents involving",         None, None, None),
    ("exposure to traumatic",  None, None, None),
    ("exposure to stressful",  None, None, None),

    # ============================================================
    # 35. CATCH-ALL  (last resort)
    # ============================================================
    ("struck by",   None, "struck_by", "low"),
    ("caught in",   None, "caught_in", "low"),
    ("fall",        None, None, None),
    ("noncollision", "mobile_equipment", None, "low"),
    ("collision",   "mobile_equipment", "struck_by", "low"),
    ("roadway",     "mobile_equipment", None, "low"),
    ("nonroadway",  "mobile_equipment", None, "low"),
]


# ── Public API ──────────────────────────────────────────────────

def map_event_title(event_title):
    """Map an OSHA EventTitle to (hazard, exposure, confidence).

    Args:
        event_title: Raw OSHA EventTitle string.

    Returns:
        dict with keys ``hazard``, ``exposure``, ``confidence``.
        Any value may be ``None`` when the event is outside the
        SIF precursor taxonomy or is genuinely ambiguous.
    """

    if not event_title or not event_title.strip():
        return {"hazard": None, "exposure": None, "confidence": None}

    t = event_title.strip().lower()

    for pattern, hazard, exposure, confidence in _RULES:
        if pattern in t:
            return {
                "hazard": hazard,
                "exposure": exposure,
                "confidence": confidence,
            }

    # No rule matched — unmapped EventTitle
    return {"hazard": None, "exposure": None, "confidence": None}
