RELATIONSHIP_GRAPH = {
    "soil_organic_carbon": {
        "affects": ["water_retention", "microbial_activity", "soil_fertility", "plant_growth"],
        "label": "Soil Organic Carbon"
    },
    "water_retention": {
        "affects": ["vegetation_health", "drought_resilience", "habitat_quality"],
        "label": "Water Retention"
    },
    "rainfall": {
        "affects": ["water_availability", "vegetation_survival", "habitat_persistence"],
        "label": "Rainfall"
    },
    "monoculture": {
        "affects": ["habitat_diversity", "soil_microbial_diversity", "pollinator_decline"],
        "label": "Monoculture Farming"
    },
    "land_use_intensity": {
        "affects": ["habitat_fragmentation", "species_movement", "biodiversity"],
        "label": "Land Use Intensity"
    },
    "habitat_fragmentation": {
        "affects": ["ecological_connectivity", "species_survival", "biodiversity"],
        "label": "Habitat Fragmentation"
    },
    "deforestation": {
        "affects": ["habitat_loss", "carbon_stock", "microclimate", "species_richness"],
        "label": "Deforestation"
    },
    "pesticide_pressure": {
        "affects": ["pollinator_decline", "soil_microbial_activity", "food_web"],
        "label": "Pesticide Pressure"
    },
    "temperature": {
        "affects": ["evapotranspiration", "plant_stress", "species_range_shift"],
        "label": "Temperature"
    },
    "biodiversity_decline": {
        "affects": ["habitat_quality", "species_survival", "ecological_connectivity"],
        "label": "Biodiversity Decline"
    }
}

INTERVENTIONS = {
    "low_soc_low_rainfall_monoculture": [
        "legume_intercropping", "cover_crops", "reduced_tillage", "agroforestry"
    ],
    "habitat_fragmentation": [
        "native_hedgerows", "riparian_buffers", "habitat_corridors", "restoration_planting"
    ],
    "deforestation": [
        "restoration_planting", "agroforestry", "riparian_restoration"
    ],
    "pesticide_high": [
        "integrated_pest_management", "buffer_strips", "native_habitat_patches"
    ]
}
