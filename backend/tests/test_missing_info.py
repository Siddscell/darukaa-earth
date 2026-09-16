from app.reasoning.missing_info_detector import get_missing_info, needs_clarification, profile_completeness_score

def test_missing_info_for_biodiversity():
    profile = {
        "region": "Maharashtra"
    }
    intents = ["biodiversity"]
    
    questions = get_missing_info(profile, intents)
    
    # Needs to ask for things like SOC, rainfall, land_use since intent is biodiversity
    assert len(questions) > 0
    assert any("carbon" in q.lower() or "organic" in q.lower() for q in questions)
    assert any("rainfall" in q.lower() for q in questions)
    
    # Should need clarification
    assert needs_clarification(profile, intents)

def test_complete_profile_no_clarification():
    profile = {
        "region": "Maharashtra",
        "soil": {"organic_carbon_percent": 1.2, "ph": 6.5, "moisture_percent": 15},
        "climate": {"rainfall_pattern": "moderate", "temperature_c": 25},
        "land_use": {"primary_type": "cropland", "cropping_system": "mixed", "crop": "wheat"},
        "human_impact": {"pesticide_pressure": "low"}
    }
    intents = ["biodiversity"]
    
    questions = get_missing_info(profile, intents)
    assert len(questions) == 0
    assert not needs_clarification(profile, intents)
