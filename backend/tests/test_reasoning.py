from app.reasoning.reasoning_engine import generate_reasoning_chain

def test_reasoning_engine():
    profile = {
        "region": "semi-arid",
        "soil": {"organic_carbon_percent": 0.3},
        "climate": {"rainfall_pattern": "low", "temperature_c": 31},
        "land_use": {"cropping_system": "monoculture", "crop": "wheat"}
    }
    
    result = generate_reasoning_chain(profile)
    
    active_vars = result.get("active_variables", [])
    assert "soil_organic_carbon" in active_vars
    assert "rainfall" in active_vars
    assert "monoculture" in active_vars
    assert "temperature" in active_vars
    
    interventions = result.get("interventions", [])
    assert len(interventions) >= 3
    # Multi-metric rule: low soc + low rainfall + monoculture
    assert "legume_intercropping" in interventions or "cover_crops" in interventions


def test_biodiversity_reasoning():
    """Verify that biodiversity decline relationships appear for the example scenario."""
    profile = {
        "region": "Maharashtra",
        "soil": {"organic_carbon_percent": 0.3},
        "land_use": {"crop": "wheat", "primary_type": "cropland"},
        "climate": {"rainfall_pattern": "low"},
        "biodiversity": {"species_richness": "low", "habitat_diversity": "low"}
    }
    
    result = generate_reasoning_chain(profile)
    active_vars = result.get("active_variables", [])
    
    assert "biodiversity_decline" in active_vars
    assert "soil_organic_carbon" in active_vars
    assert "rainfall" in active_vars
    
    chain = result.get("relationship_chain", [])
    chain_str = " | ".join(chain).lower()
    
    assert "biodiversity decline" in chain_str
    assert "habitat quality" in chain_str or "species survival" in chain_str
    assert "water retention" in chain_str
