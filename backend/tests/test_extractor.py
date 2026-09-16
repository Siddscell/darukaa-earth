from app.reasoning.environmental_extractor import extract_environmental_profile, detect_user_intent

def test_extract_environmental_profile():
    text = "My farm is in Maharashtra. I grow wheat continuously. Rainfall is low and soil organic carbon is around 0.3 percent."
    profile = extract_environmental_profile(text)
    
    assert profile.get("region") == "Maharashtra"
    assert profile.get("soil", {}).get("organic_carbon_percent") == 0.3
    assert profile.get("land_use", {}).get("cropping_system") == "monoculture"
    assert profile.get("land_use", {}).get("crop") == "wheat"
    assert profile.get("climate", {}).get("rainfall_pattern") == "low"

def test_detect_user_intent():
    text = "Biodiversity is declining on my farm."
    intents = detect_user_intent(text)
    assert "biodiversity" in intents


def test_soc_variants():
    """SOC must be extracted from common natural-language phrasings."""
    variants = [
        ("soil organic carbon is 0.3%", 0.3),
        ("soil organic carbon is around 0.3%", 0.3),
        ("soil organic carbon is about 0.3%", 0.3),
        ("soil organic carbon is only 0.3%", 0.3),
        ("soil organic carbon is just 0.3%", 0.3),
        ("SOC is 0.3%", 0.3),
        ("SOC is only 0.3%", 0.3),
        ("my soil carbon is 0.3%", 0.3),
        ("soil carbon is only 0.3%", 0.3),
        ("0.3% soil organic carbon", 0.3),
    ]
    for text, expected in variants:
        profile = extract_environmental_profile(text)
        actual = profile.get("soil", {}).get("organic_carbon_percent")
        assert actual == expected, f"Failed for: {text!r} -> got {actual}"


def test_no_monoculture_from_wheat_farm():
    """'wheat farm' alone must not imply monoculture."""
    profile = extract_environmental_profile(
        "My wheat farm in Maharashtra has low rainfall."
    )
    cropping_system = profile.get("land_use", {}).get("cropping_system")
    assert cropping_system is None, (
        f"Expected no monoculture inference, got {cropping_system!r}"
    )


def test_full_sentence_extraction():
    """Integration test for the frontend bug: full sentence must extract all variables."""
    text = (
        "My wheat farm in Maharashtra has low rainfall and I've noticed "
        "biodiversity declining. Soil organic carbon is only 0.3%."
    )
    profile = extract_environmental_profile(text)
    assert profile.get("region") == "Maharashtra"
    assert profile.get("soil", {}).get("organic_carbon_percent") == 0.3
    assert profile.get("land_use", {}).get("crop") == "wheat"
    assert profile.get("land_use", {}).get("cropping_system") is None
    assert profile.get("climate", {}).get("rainfall_pattern") == "low"
    assert profile.get("biodiversity", {}).get("species_richness") == "low"
    assert profile.get("biodiversity", {}).get("habitat_diversity") == "low"
