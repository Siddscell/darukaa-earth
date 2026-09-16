"""
Environmental extractor: parse natural language into structured environmental profile data.
Uses regex + keyword matching — no LLM dependency for extraction.
"""
import re
from typing import Optional
from app.schemas.environmental import (
    EnvironmentalProfile, SoilData, LandUseData,
    BiodiversityData, ClimateData, HumanImpactData
)


# ─── helpers ────────────────────────────────────────────────────────────────

def _match_float(patterns: list[str], text: str) -> Optional[float]:
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except (IndexError, ValueError):
                pass
    return None


def _match_keyword(keywords: list[str], text: str) -> bool:
    t = text.lower()
    return any(k in t for k in keywords)


# ─── extractors ─────────────────────────────────────────────────────────────

def _extract_region(text: str) -> Optional[str]:
    regions = [
        "Maharashtra", "Punjab", "Karnataka", "Rajasthan", "Gujarat",
        "Andhra Pradesh", "Telangana", "Madhya Pradesh", "Uttar Pradesh",
        "Bihar", "Tamil Nadu", "Odisha", "Deccan", "Indo-Gangetic",
        "Western Ghats", "Eastern Ghats", "Himalayan", "Thar Desert",
    ]
    for r in regions:
        if re.search(r, text, re.IGNORECASE):
            return r

    # generic region descriptors
    if re.search(r"semi[- ]?arid", text, re.IGNORECASE):
        return "Semi-arid region"
    if re.search(r"tropical", text, re.IGNORECASE):
        return "Tropical region"
    if re.search(r"dryland|dry land", text, re.IGNORECASE):
        return "Dryland region"

    # "farm in X" / "located in X"
    m = re.search(
        r"(?:farm|land|region|area|located)\s+in\s+([A-Z][a-zA-Z\s]{2,30}?)(?:[.,;]|$)",
        text,
        re.IGNORECASE,
    )
    if m:
        candidate = m.group(1).strip()
        if len(candidate) > 2:
            return candidate
    return None


def _extract_soil(text: str) -> Optional[SoilData]:
    soil = SoilData()
    changed = False

    # pH
    ph = _match_float(
        [
            r"pH\s*(?:is|of|=|about|around)?\s*(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*pH",
            r"soil\s+pH\s*(?:is|of|=)?\s*(\d+\.?\d*)",
        ],
        text,
    )
    if ph is not None:
        soil.ph = ph
        changed = True

    # Organic carbon
    soc = _match_float(
        [
            r"(?:soil\s+)?organic\s+carbon\s+is\s+(?:only\s+|around\s+|about\s+|just\s+)?(\d+\.?\d*)\s*(?:%|percent)",
        r"SOC\s+is\s+(?:only\s+|around\s+|about\s+|just\s+)?(\d+\.?\d*)\s*(?:%|percent)",
        r"(?:my\s+)?soil\s+carbon\s+is\s+(?:only\s+|around\s+|about\s+|just\s+)?(\d+\.?\d*)\s*(?:%|percent)",
        r"(\d+\.?\d*)\s*(?:%|percent)\s+(?:soil\s+)?organic\s+carbon",
        r"organic\s+carbon\s+(?:is\s+)?(?:only\s+|around\s+|about\s+|just\s+)?(\d+\.?\d*)\s*(?:%|percent)",
        r"carbon\s+(?:content|level)?\s+is\s+(?:only\s+|around\s+|about\s+|just\s+)?(\d+\.?\d*)\s*(?:%|percent)",
        r"OC\s+is\s+(?:only\s+|around\s+|about\s+|just\s+)?(\d+\.?\d*)\s*(?:%|percent)",
        ],
        text,
    )
    if soc is not None:
        soil.organic_carbon_percent = soc
        changed = True
    elif _match_keyword(["low organic carbon", "low soc", "carbon depleted", "carbon deficient"], text):
        soil.organic_carbon_percent = None  # flagged low but no value
        soil.structure = soil.structure or "degraded"
        changed = True

    # Moisture
    moisture = _match_float(
        [
            r"moisture\s*(?:is|of|=|around|about)?\s*(\d+\.?\d*)\s*%",
            r"(\d+\.?\d*)\s*%\s*moisture",
            r"soil\s+moisture\s*(?:is|of|=|around|about)?\s*(\d+\.?\d*)\s*%",
        ],
        text,
    )
    if moisture is not None:
        soil.moisture_percent = moisture
        changed = True

    # Structure qualitative
    if _match_keyword(["compacted soil", "soil compaction", "hard soil", "clay soil"], text):
        soil.structure = "compacted"
        changed = True
    elif _match_keyword(["sandy soil", "loose soil"], text):
        soil.structure = "sandy"
        changed = True

    return soil if changed else None


def _extract_land_use(text: str) -> Optional[LandUseData]:
    lu = LandUseData()
    changed = False

    # Cropping system
    if _match_keyword(
        ["monoculture", "continuous wheat", "wheat continuously", "single crop",
         "only wheat", "continuous monoculture", "continuous cropping",
         "continuous cultivation"],
        text,
    ):
        lu.cropping_system = "monoculture"
        changed = True
    elif _match_keyword(["agroforestry", "agro forestry", "trees and crops"], text):
        lu.cropping_system = "agroforestry"
        lu.primary_type = "cropland"
        changed = True
    elif _match_keyword(["intercrop", "inter-crop", "mixed crop", "crop rotation", "polyculture", "diversified crop"], text):
        lu.cropping_system = "mixed"
        changed = True

    # Primary land use type
    if _match_keyword(["cropland", "farmland", "agricultural land", "farm", "cultivated"], text):
        lu.primary_type = lu.primary_type or "cropland"
        changed = True
    elif _match_keyword(["forest", "woodland"], text) and not _match_keyword(["deforest"], text):
        lu.primary_type = "forest"
        changed = True
    elif _match_keyword(["pasture", "grazing", "grassland"], text):
        lu.primary_type = "pasture"
        changed = True
    elif _match_keyword(["wetland", "marsh", "swamp"], text):
        lu.primary_type = "wetland"
        changed = True
    elif _match_keyword(["degraded", "barren", "eroded land"], text):
        lu.primary_type = "degraded_land"
        changed = True

    # Crop type
    crops = {
        "wheat": ["wheat"],
        "rice": ["rice", "paddy"],
        "maize": ["maize", "corn"],
        "sorghum": ["sorghum", "jowar"],
        "cotton": ["cotton"],
        "sugarcane": ["sugarcane", "sugar cane"],
        "soybean": ["soybean", "soya"],
        "groundnut": ["groundnut", "peanut"],
        "chickpea": ["chickpea", "gram"],
        "vegetables": ["vegetables", "horticulture"],
        "coffee": ["coffee"],
        "tea": ["tea"],
        "millet": ["millet", "bajra"],
    }
    tl = text.lower()
    for crop, kws in crops.items():
        if any(k in tl for k in kws):
            lu.crop = lu.crop or crop
            if lu.primary_type is None:
                lu.primary_type = "cropland"
            changed = True
            break

    return lu if changed else None


def _extract_biodiversity(text: str) -> Optional[BiodiversityData]:
    bd = BiodiversityData()
    changed = False

    if _match_keyword(
        ["biodiversity declining", "biodiversity loss", "species declining",
         "species disappearing", "wildlife loss", "biodiversity poor", "low biodiversity"],
        text,
    ):
        bd.species_richness = "low"
        bd.habitat_diversity = "low"
        changed = True

    if _match_keyword(["pollinator decline", "bee decline", "fewer bees", "fewer pollinators",
                        "pollinators declining", "no pollinators"], text):
        bd.pollinator_presence = "low"
        changed = True

    native_pct = _match_float(
        [r"native\s+vegetation\s+(?:covers?|is|=)?\s*(\d+\.?\d*)\s*%",
         r"(\d+\.?\d*)\s*%\s*native\s+vegetation"],
        text,
    )
    if native_pct is not None:
        bd.native_vegetation_percent = native_pct
        changed = True

    if _match_keyword(["fragmented habitat", "habitat fragmented", "isolated patches",
                        "disconnected habitat"], text):
        bd.habitat_fragmentation = "high"
        changed = True

    if _match_keyword(["poor connectivity", "no connectivity", "isolated"], text):
        bd.ecological_connectivity = "poor"
        changed = True

    return bd if changed else None


def _extract_climate(text: str) -> Optional[ClimateData]:
    climate = ClimateData()
    changed = False

    # Temperature
    temp = _match_float(
        [
            r"temperature\s*(?:is|of|=|around|about)?\s*(\d+\.?\d*)\s*°?C",
            r"(\d+\.?\d*)\s*°C",
            r"(\d+\.?\d*)\s*degrees?\s*[Cc]elsius",
            r"temp(?:erature)?\s*(?:is|of|=|around|about)?\s*(\d+\.?\d*)",
        ],
        text,
    )
    if temp is not None:
        climate.temperature_c = temp
        changed = True

    # Rainfall mm
    rainfall_mm = _match_float(
        [
            r"rainfall\s*(?:of|is|=|about|around)?\s*(\d+\.?\d*)\s*mm",
            r"(\d+\.?\d*)\s*mm\s*(?:of\s+)?(?:annual\s+)?rainfall",
            r"precipitation\s*(?:of|is|=|about|around)?\s*(\d+\.?\d*)\s*mm",
        ],
        text,
    )
    if rainfall_mm is not None:
        climate.rainfall_mm = rainfall_mm
        changed = True

    # Rainfall pattern (qualitative)
    if _match_keyword(["low rainfall", "rainfall is low", "rainfall was low", "little rain", "dry climate", "receives little rainfall",
                        "limited rainfall", "scarce rainfall", "erratic rainfall", "dryland"], text):
        climate.rainfall_pattern = climate.rainfall_pattern or "low"
        changed = True
    elif _match_keyword(["high rainfall", "heavy rain", "abundant rainfall", "wet climate"], text):
        climate.rainfall_pattern = climate.rainfall_pattern or "high"
        changed = True
    elif _match_keyword(["moderate rainfall", "seasonal rainfall", "monsoon"], text):
        climate.rainfall_pattern = climate.rainfall_pattern or "moderate"
        changed = True

    # Drought
    if _match_keyword(["drought", "droughts", "water scarce", "water stress", "water shortage"], text):
        climate.drought_conditions = True
        changed = True

    # Heat stress
    if _match_keyword(["heat stress", "very hot", "extreme heat", "high heat"], text) or (
        temp is not None and temp >= 35
    ):
        climate.heat_stress = True
        changed = True

    return climate if changed else None


def _extract_human_impact(text: str) -> Optional[HumanImpactData]:
    hi = HumanImpactData()
    changed = False

    if _match_keyword(["high pesticide", "heavy pesticide", "lots of pesticide",
                        "significant pesticide", "agrochemical", "herbicide", "insecticide"], text):
        hi.pesticide_pressure = "high"
        changed = True
    elif _match_keyword(["pesticide", "chemical spray", "spray"], text):
        hi.pesticide_pressure = hi.pesticide_pressure or "moderate"
        changed = True
    elif _match_keyword(["low pesticide", "no pesticide", "organic farm", "pesticide free"], text):
        hi.pesticide_pressure = "low"
        changed = True

    if _match_keyword(["deforest", "forest cleared", "forest cut", "logging", "forest loss"], text):
        hi.deforestation_pressure = "high"
        changed = True

    if _match_keyword(["pollution", "contamination", "chemical runoff", "effluent"], text):
        hi.pollution_level = "moderate"
        changed = True

    if _match_keyword(["habitat disturb", "disturbed habitat", "land disturb"], text):
        hi.habitat_disturbance = "high"
        changed = True

    return hi if changed else None


# ─── public API ─────────────────────────────────────────────────────────────

def extract_environmental_profile(text: str) -> dict:
    """
    Parse natural language text into a partial EnvironmentalProfile dict.
    Returns only fields that were actually detected.
    """
    profile: dict = {}

    region = _extract_region(text)
    if region:
        profile["region"] = region

    soil = _extract_soil(text)
    if soil:
        profile["soil"] = soil.model_dump(exclude_none=True)

    land_use = _extract_land_use(text)
    if land_use:
        profile["land_use"] = land_use.model_dump(exclude_none=True)

    biodiversity = _extract_biodiversity(text)
    if biodiversity:
        profile["biodiversity"] = biodiversity.model_dump(exclude_none=True)

    climate = _extract_climate(text)
    if climate:
        profile["climate"] = climate.model_dump(exclude_none=True)

    human_impact = _extract_human_impact(text)
    if human_impact:
        profile["human_impact"] = human_impact.model_dump(exclude_none=True)

    # Geo-coordinates via "lat X, lon Y" patterns
    lat = _match_float([r"lat(?:itude)?\s*[=:]?\s*(-?\d+\.?\d*)"], text)
    lon = _match_float([r"lon(?:gitude)?\s*[=:]?\s*(-?\d+\.?\d*)"], text)
    if lat is not None:
        profile["latitude"] = lat
    if lon is not None:
        profile["longitude"] = lon

    return profile


def detect_user_intent(text: str) -> list[str]:
    """Return a list of detected user concerns/intents."""
    intents = []
    tl = text.lower()
    if any(k in tl for k in ["biodiversity", "species", "wildlife", "pollinator", "habitat"]):
        intents.append("biodiversity")
    if any(k in tl for k in ["soil", "carbon", "ph", "organic matter", "fertility"]):
        intents.append("soil")
    if any(k in tl for k in ["yield", "production", "crop", "harvest"]):
        intents.append("yield")
    if any(k in tl for k in ["water", "rainfall", "drought", "moisture", "irrigation"]):
        intents.append("water")
    if any(k in tl for k in ["climate", "temperature", "heat", "flood"]):
        intents.append("climate")
    if any(k in tl for k in ["pesticide", "chemical", "pollution", "deforest"]):
        intents.append("human_impact")
    if not intents:
        intents.append("general")
    return intents

