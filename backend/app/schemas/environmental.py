from pydantic import BaseModel, Field
from typing import Optional, List

class SoilData(BaseModel):
    ph: Optional[float] = Field(None, ge=0, le=14)
    organic_carbon_percent: Optional[float] = Field(None, ge=0, le=100)
    moisture_percent: Optional[float] = Field(None, ge=0, le=100)
    structure: Optional[str] = None
    nutrient_availability: Optional[str] = None
    microbial_activity: Optional[str] = None

class LandUseData(BaseModel):
    primary_type: Optional[str] = None
    cropping_system: Optional[str] = None
    crop: Optional[str] = None

class BiodiversityData(BaseModel):
    species_richness: Optional[str] = None
    habitat_diversity: Optional[str] = None
    pollinator_presence: Optional[str] = None
    native_vegetation_percent: Optional[float] = None
    ecological_connectivity: Optional[str] = None
    habitat_fragmentation: Optional[str] = None

class ClimateData(BaseModel):
    temperature_c: Optional[float] = None
    rainfall_mm: Optional[float] = None
    rainfall_pattern: Optional[str] = None
    seasonality: Optional[str] = None
    drought_conditions: Optional[bool] = None
    heat_stress: Optional[bool] = None

class HumanImpactData(BaseModel):
    pollution_level: Optional[str] = None
    pesticide_pressure: Optional[str] = None
    deforestation_pressure: Optional[str] = None
    habitat_disturbance: Optional[str] = None

class EnvironmentalProfile(BaseModel):
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    soil: Optional[SoilData] = None
    land_use: Optional[LandUseData] = None
    biodiversity: Optional[BiodiversityData] = None
    climate: Optional[ClimateData] = None
    human_impact: Optional[HumanImpactData] = None

class EnvironmentalProfileCreate(EnvironmentalProfile):
    conversation_id: Optional[str] = None
