"""
Missing information detector.
Determines which environmental variables are critical for the detected intent
and asks only the most important ones (at most 3).
"""
from typing import Optional


# Critical variable requirements per intent
INTENT_REQUIREMENTS = {
    "biodiversity": {
        "critical": [
            ("soil.organic_carbon_percent", "What is the approximate soil organic carbon percentage?"),
            ("climate.rainfall_pattern", "What is the rainfall pattern in your area (low / moderate / high / seasonal)?"),
            ("land_use.cropping_system", "What is your current cropping system (monoculture / mixed cropping / agroforestry)?"),
            ("region", "What is the region or geographic location of your land?"),
        ],
        "useful": [
            ("soil.ph", "What is the approximate soil pH?"),
            ("human_impact.pesticide_pressure", "What is the level of pesticide use (low / moderate / high)?"),
        ],
    },
    "soil": {
        "critical": [
            ("soil.ph", "What is the approximate soil pH?"),
            ("soil.organic_carbon_percent", "What is the approximate soil organic carbon percentage?"),
            ("climate.rainfall_pattern", "What is the rainfall pattern in your area?"),
            ("region", "What is the geographic location of your land?"),
        ],
        "useful": [
            ("land_use.cropping_system", "What crops do you grow and how (monoculture / rotation / mixed)?"),
        ],
    },
    "water": {
        "critical": [
            ("climate.rainfall_pattern", "What is the rainfall pattern (low / moderate / high / seasonal)?"),
            ("soil.organic_carbon_percent", "What is the approximate soil organic carbon percentage?"),
            ("soil.moisture_percent", "Do you know the approximate soil moisture percentage?"),
            ("region", "What is the geographic location of your land?"),
        ],
        "useful": [
            ("land_use.primary_type", "What is the primary land use (cropland / pasture / forest)?"),
        ],
    },
    "yield": {
        "critical": [
            ("soil.ph", "What is the approximate soil pH?"),
            ("soil.organic_carbon_percent", "What is the approximate soil organic carbon percentage?"),
            ("climate.rainfall_pattern", "What is the rainfall pattern in your area?"),
            ("land_use.crop", "What crop(s) are you growing?"),
        ],
        "useful": [
            ("land_use.cropping_system", "What cropping system do you use?"),
        ],
    },
    "climate": {
        "critical": [
            ("climate.temperature_c", "What is the approximate average temperature (°C)?"),
            ("climate.rainfall_pattern", "What is the rainfall pattern in your area?"),
            ("region", "What is the geographic location of your land?"),
        ],
        "useful": [],
    },
    "human_impact": {
        "critical": [
            ("human_impact.pesticide_pressure", "What is the level of pesticide use (low / moderate / high)?"),
            ("land_use.cropping_system", "What is your current cropping system?"),
            ("biodiversity.species_richness", "How would you describe local biodiversity (good / declining / poor)?"),
        ],
        "useful": [],
    },
    "general": {
        "critical": [
            ("region", "What is the geographic location of your land?"),
            ("land_use.primary_type", "What is the primary land use type (cropland / forest / pasture)?"),
            ("climate.rainfall_pattern", "What is the rainfall pattern in your area?"),
        ],
        "useful": [],
    },
}


def _get_nested(profile: dict, dotted_key: str) -> Optional[object]:
    """Get a value from a nested dict using dot notation."""
    keys = dotted_key.split(".")
    current = profile
    for k in keys:
        if not isinstance(current, dict) or k not in current:
            return None
        current = current[k]
    if current is None or current == "":
        return None
    return current


def get_missing_info(profile: dict, intents: list[str]) -> list[str]:
    """
    Given a partial environmental profile and detected intents,
    return a list of clarification questions for the most critical
    missing variables (at most 3 questions).
    """
    questions = []
    asked_keys = set()

    for intent in intents:
        requirements = INTENT_REQUIREMENTS.get(intent, INTENT_REQUIREMENTS["general"])

        for var_key, question in requirements["critical"]:
            if var_key in asked_keys:
                continue
            value = _get_nested(profile, var_key)
            if value is None:
                questions.append(question)
                asked_keys.add(var_key)
            if len(questions) >= 3:
                break

        if len(questions) >= 3:
            break

    # If we still have room and profile is very sparse, add useful questions
    if len(questions) < 2:
        for intent in intents:
            requirements = INTENT_REQUIREMENTS.get(intent, INTENT_REQUIREMENTS["general"])
            for var_key, question in requirements.get("useful", []):
                if var_key in asked_keys:
                    continue
                value = _get_nested(profile, var_key)
                if value is None:
                    questions.append(question)
                    asked_keys.add(var_key)
                if len(questions) >= 3:
                    break
            if len(questions) >= 3:
                break

    return questions[:3]


def profile_completeness_score(profile: dict) -> float:
    """Return a 0-1 score indicating how complete the environmental profile is."""
    total_fields = 12  # key diagnostic fields
    filled = 0

    check_fields = [
        ("region", profile),
        ("soil.ph", profile),
        ("soil.organic_carbon_percent", profile),
        ("soil.moisture_percent", profile),
        ("land_use.primary_type", profile),
        ("land_use.cropping_system", profile),
        ("land_use.crop", profile),
        ("climate.temperature_c", profile),
        ("climate.rainfall_pattern", profile),
        ("biodiversity.species_richness", profile),
        ("human_impact.pesticide_pressure", profile),
        ("human_impact.deforestation_pressure", profile),
    ]

    for key, _ in check_fields:
        if _get_nested(profile, key) is not None:
            filled += 1

    return filled / total_fields


def needs_clarification(profile: dict, intents: list[str]) -> bool:
    """Return True if clarification questions should be asked."""
    missing = get_missing_info(profile, intents)
    score = profile_completeness_score(profile)
    # Ask for clarification if score is very low OR critical fields are missing
    return len(missing) > 0 and score < 0.4
