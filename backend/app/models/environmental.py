from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base

class EnvironmentalProfile(Base):
    __tablename__ = "environmental_profiles"
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), unique=True)
    region = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    
    soil_ph = Column(Float)
    soil_organic_carbon_percent = Column(Float)
    soil_moisture_percent = Column(Float)
    soil_structure = Column(String)
    soil_nutrient_availability = Column(String)
    
    land_use_primary_type = Column(String)
    land_use_cropping_system = Column(String)
    land_use_crop = Column(String)
    
    biodiversity_species_richness = Column(String)
    biodiversity_habitat_diversity = Column(String)
    biodiversity_pollinator_presence = Column(String)
    biodiversity_native_vegetation = Column(Float)
    biodiversity_connectivity = Column(String)
    
    climate_temperature_c = Column(Float)
    climate_rainfall_mm = Column(Float)
    climate_rainfall_pattern = Column(String)
    climate_seasonality = Column(String)
    climate_drought_conditions = Column(Boolean)
    
    human_impact_pollution_level = Column(String)
    human_impact_pesticide_pressure = Column(String)
    human_impact_deforestation_pressure = Column(String)
    human_impact_habitat_disturbance = Column(String)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
