"""
Multi-metric reasoning engine.
Traverses the environmental relationship graph to identify active relationships,
selects appropriate interventions, and produces a structured reasoning summary.
"""
from app.reasoning.relationship_graph import RELATIONSHIP_GRAPH, INTERVENTIONS


# ─── helpers ────────────────────────────────────────────────────────────────

def _get(profile: dict, dotted: str):
    keys = dotted.split(".")
    cur = profile
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def _is_low(val) -> bool:
    if val is None:
        return False
    if isinstance(val, (int, float)):
        return False  # caller checks threshold
    if isinstance(val, str):
        return val.lower() in ("low", "poor", "degraded", "very low")
    return False


def _is_high(val) -> bool:
    if val is None:
        return False
    if isinstance(val, str):
        return val.lower() in ("high", "very high", "severe")
    return False


# ─── profile → active variable set ──────────────────────────────────────────

def _detect_active_variables(profile: dict) -> list[str]:
    """
    Map a profile to a set of 'active' graph node keys that represent
    conditions requiring attention.
    """
    active = []

    soc = _get(profile, "soil.organic_carbon_percent")
    if soc is not None and soc < 0.6:
        active.append("soil_organic_carbon")

    rainfall = _get(profile, "climate.rainfall_pattern")
    if rainfall and rainfall.lower() in ("low", "very low"):
        active.append("rainfall")

    cropping = _get(profile, "land_use.cropping_system")
    if cropping and "mono" in cropping.lower():
        active.append("monoculture")
        active.append("land_use_intensity")

    frag = _get(profile, "biodiversity.habitat_fragmentation")
    if _is_high(frag):
        active.append("habitat_fragmentation")

    conn = _get(profile, "biodiversity.ecological_connectivity")
    if conn and conn.lower() == "poor":
        active.append("habitat_fragmentation")

    defor = _get(profile, "human_impact.deforestation_pressure")
    if _is_high(defor):
        active.append("deforestation")

    pest = _get(profile, "human_impact.pesticide_pressure")
    if _is_high(pest) or (isinstance(pest, str) and pest.lower() == "moderate"):
        active.append("pesticide_pressure")

    temp = _get(profile, "climate.temperature_c")
    if temp is not None and temp > 30:
        active.append("temperature")

    # Biodiversity decline signals
    species = _get(profile, "biodiversity.species_richness")
    habitat_div = _get(profile, "biodiversity.habitat_diversity")
    pollinator = _get(profile, "biodiversity.pollinator_presence")
    if _is_low(species) or _is_low(habitat_div) or _is_low(pollinator):
        active.append("biodiversity_decline")

    # Remove duplicates while preserving order
    seen = set()
    return [v for v in active if not (v in seen or seen.add(v))]


# ─── build relationship chain ────────────────────────────────────────────────

def _build_relationship_chain(active_vars: list[str]) -> list[str]:
    """
    Traverse the relationship graph to identify downstream effects
    and produce a human-readable reasoning chain.
    """
    chain = []
    seen_relationships = set()

    for var in active_vars:
        node = RELATIONSHIP_GRAPH.get(var)
        if not node:
            continue
        label = node["label"]
        for effect in node["affects"]:
            rel = f"{label} \u2192 {effect.replace('_', ' ')}"
            if rel not in seen_relationships:
                chain.append(rel)
                seen_relationships.add(rel)

    return chain


# ─── select interventions ────────────────────────────────────────────────────

INTERVENTION_DETAILS = {
    "legume_intercropping": {
        "title": "Introduce Legume Intercropping",
        "action": "Plant drought-tolerant legumes such as cowpea, moth bean, or pigeonpea between cereal rows during the appropriate growing window for your region.",
        "reasoning": "Legumes fix atmospheric nitrogen through root nodule bacteria, adding biologically available nitrogen to subsequent crops without synthetic fertilizer. Their root systems explore different soil layers than cereals, improving soil structure and porosity. Mixed plant canopies also support a wider range of beneficial insects, including pollinators and natural pest enemies, compared to uniform monocultures.",
        "impacted_metrics": ["soil_organic_carbon", "soil_nitrogen", "habitat_diversity", "pollinator_presence", "water_use_efficiency"],
        "time_horizon": "medium-term",
        "confidence": "Medium",
        "topic_tags": ["soil", "land_use", "biodiversity"],
    },
    "cover_crops": {
        "title": "Establish Cover Crops Between Seasons",
        "action": "Plant short-season cover crops such as cowpea, sunn hemp, or clover during the fallow period between main crop seasons. Select drought-tolerant species suited to your rainfall regime.",
        "reasoning": "Cover crop residue contributes organic matter to the soil, feeds microbial communities, and protects against erosion during dry periods. Leguminous cover crops also fix atmospheric nitrogen. Root systems create biopores that improve water infiltration in soils with degraded structure, extending the effective period of plant-available moisture between rain events.",
        "impacted_metrics": ["soil_organic_carbon", "microbial_activity", "water_retention", "soil_erosion"],
        "time_horizon": "medium-term",
        "confidence": "Medium",
        "topic_tags": ["soil", "land_use"],
    },
    "reduced_tillage": {
        "title": "Transition to Conservation Tillage",
        "action": "Reduce or eliminate annual deep tillage. Retain crop residues on the soil surface rather than incorporating or burning them. Adopt minimum tillage or strip tillage approaches.",
        "reasoning": "Reduced tillage protects soil fungal networks critical for nutrient cycling and carbon stabilization. Residue retention feeds soil microbial communities and gradually builds organic matter. Conservation tillage reduces soil structural disruption, improving water infiltration and aggregate stability. These changes accumulate gradually over multiple seasons.",
        "impacted_metrics": ["soil_organic_carbon", "soil_structure", "microbial_activity", "water_retention"],
        "time_horizon": "long-term",
        "confidence": "Medium",
        "topic_tags": ["soil"],
    },
    "agroforestry": {
        "title": "Integrate Trees into the Farming System",
        "action": "Establish multipurpose native or agroforestry trees at appropriate spacing within or around crop fields. Suitable species for semi-arid India include Moringa, Drumstick, Neem, and Siris (Albizia). Consult local forestry extension for species selection.",
        "reasoning": "Agroforestry systems create vertical structural diversity — canopy, shrub, and ground layers — which supports a broader range of plant and animal species. Tree root systems access deep soil water and nutrients unavailable to crops. Leaf litter contributes organic matter. Canopy provides microclimate buffering, reducing surface temperatures and evapotranspiration under crop canopies. Multiple studies from CIFOR and ICRAF document biodiversity benefits of agroforestry in comparable systems.",
        "impacted_metrics": ["soil_organic_carbon", "habitat_diversity", "species_richness", "microclimate", "biodiversity"],
        "time_horizon": "long-term",
        "confidence": "Medium",
        "topic_tags": ["soil", "biodiversity", "land_use"],
    },
    "native_hedgerows": {
        "title": "Establish Native Species Hedgerows at Field Boundaries",
        "action": "Plant diverse native thorny shrubs and flowering plants at field boundaries and along internal field edges. Use locally native species with sequential flowering to provide year-round resources. Examples for South Asia include wild plum (Ziziphus), karonda (Carissa), and native grasses.",
        "reasoning": "Native hedgerows provide year-round habitat resources for pollinators and other wildlife through sequential flowering, nesting cover, and dispersal pathways. Mixed native hedgerows support substantially higher invertebrate diversity than open field boundaries. They also serve as ecological corridors connecting fragmented habitat patches, improving landscape-scale connectivity for species movement.",
        "impacted_metrics": ["habitat_diversity", "species_richness", "pollinator_presence", "ecological_connectivity"],
        "time_horizon": "medium-term",
        "confidence": "Medium",
        "topic_tags": ["biodiversity"],
    },
    "riparian_buffers": {
        "title": "Establish Vegetated Riparian Buffer Strips",
        "action": "Plant native grasses, shrubs, and trees along all drainage channels, seasonal streams, and water storage areas. Maintain a minimum 5-10 metre vegetated buffer. Exclude livestock grazing from buffer zones.",
        "reasoning": "Riparian buffers intercept sediment, nutrients, and pesticides that would otherwise degrade water quality. Native riparian vegetation provides critical habitat including nesting cover, foraging areas, and movement corridors. Riparian corridors are disproportionately important for biodiversity in agricultural landscapes because they connect habitats across otherwise uniform agricultural land.",
        "impacted_metrics": ["habitat_diversity", "water_quality", "species_richness", "ecological_connectivity"],
        "time_horizon": "medium-term",
        "confidence": "Medium",
        "topic_tags": ["biodiversity", "land_use"],
    },
    "habitat_corridors": {
        "title": "Restore Habitat Connectivity Through Corridor Planting",
        "action": "Identify remnant natural vegetation patches in the landscape. Plant native trees and shrubs to create continuous vegetated strips connecting these patches. Prioritize routes along fence lines, drainage lines, and unused land margins.",
        "reasoning": "Habitat fragmentation isolates plant and animal populations, preventing genetic exchange and range shifts in response to climate change. Even narrow strips of native vegetation substantially improve species movement across fragmented agricultural landscapes. Corridors are most valuable when designed to connect larger habitat patches and when the surrounding agricultural matrix has reduced pesticide use.",
        "impacted_metrics": ["ecological_connectivity", "species_richness", "habitat_diversity", "species_survival"],
        "time_horizon": "long-term",
        "confidence": "Medium",
        "topic_tags": ["biodiversity"],
    },
    "restoration_planting": {
        "title": "Active Restoration Using Native Species",
        "action": "Source locally native tree and shrub species from regional nurseries or community seed banks. Establish native plantings on degraded land margins, eroded slopes, and areas no longer productive for agriculture. Protect planted areas from grazing during establishment.",
        "reasoning": "Ecological restoration of native vegetation is among the highest-leverage interventions for biodiversity recovery in degraded landscapes. Native species are adapted to local soil, climate, and wildlife interactions, and support a broader range of native fauna than introduced species. IUCN guidance emphasizes that restoration success depends on species selection, proximity to seed sources, and ongoing management to protect establishing vegetation.",
        "impacted_metrics": ["native_vegetation", "habitat_diversity", "species_richness", "carbon_stock", "ecological_connectivity"],
        "time_horizon": "long-term",
        "confidence": "Medium",
        "topic_tags": ["biodiversity", "land_use"],
    },
    "integrated_pest_management": {
        "title": "Transition to Integrated Pest Management",
        "action": "Adopt IPM principles: combine preventive practices (crop rotation, resistant varieties), biological controls (conserve natural enemies), and targeted threshold-based pesticide application only when pest pressure exceeds economic thresholds.",
        "reasoning": "IPM substantially reduces pesticide use while maintaining effective crop protection. Reduced pesticide exposure supports pollinator survival and soil microbial recovery. Habitat management for beneficial insects — flower strips, reduced mowing of margins, hedgerow maintenance — enhances biological pest control. FAO documentation cites numerous Asian case studies demonstrating reduced pesticide costs and recovery of beneficial insect populations under IPM.",
        "impacted_metrics": ["pollinator_presence", "soil_microbial_activity", "biodiversity", "pesticide_reduction"],
        "time_horizon": "short-term",
        "confidence": "High",
        "topic_tags": ["human_impact", "biodiversity"],
    },
    "buffer_strips": {
        "title": "Establish Flowering Buffer Strips at Field Margins",
        "action": "Sow diverse native flowering plant mixes at field margins, around field entrances, and along internal pathways. Manage by delayed cutting to allow flowering and seeding. Avoid pesticide application in buffer zones.",
        "reasoning": "Diverse native flowering plants provide year-round pollen and nectar resources for pollinators, reducing the impact of pesticide pressure on pollinator communities. Even small areas of diverse native vegetation support disproportionate pollinator diversity. Buffer strips also reduce pesticide drift and runoff into adjacent habitats.",
        "impacted_metrics": ["pollinator_presence", "habitat_diversity", "species_richness"],
        "time_horizon": "short-term",
        "confidence": "High",
        "topic_tags": ["biodiversity", "human_impact"],
    },
    "water_harvesting": {
        "title": "In-Situ Rainwater Harvesting and Conservation",
        "action": "Implement in-situ soil and water conservation structures appropriate to your topography: tied ridges, broad-bed furrows, or contour bunds on slopes. Combine with mulching and crop residue retention.",
        "reasoning": "In-situ water harvesting substantially increases the proportion of rainfall retained within the field, reducing runoff and increasing soil moisture storage between rain events. Combined with improved soil organic matter, these structural measures are particularly effective because organic-rich soils have higher infiltration rates and greater moisture storage capacity. ICAR research in semi-arid Maharashtra documents benefits of integrated watershed approaches.",
        "impacted_metrics": ["soil_moisture", "water_retention", "drought_resilience", "crop_production"],
        "time_horizon": "short-term",
        "confidence": "Medium",
        "topic_tags": ["climate", "soil"],
    },
    "crop_rotation": {
        "title": "Introduce Diverse Crop Rotation",
        "action": "Replace continuous monoculture with a multi-year rotation. For wheat-dominant systems in semi-arid India, consider a wheat–chickpea or wheat–sorghum–fallow rotation. Include a legume in every rotation cycle.",
        "reasoning": "Crop rotation disrupts pest and disease cycles, reducing pesticide dependency. Different crop root architectures improve soil structure at different depths over successive seasons. Including legumes in rotations contributes biologically fixed nitrogen. At the landscape level, crop rotation creates temporal diversity in vegetation structure, supporting insect communities that require different habitats at different times of year.",
        "impacted_metrics": ["soil_health", "species_richness", "pesticide_reduction", "organic_carbon"],
        "time_horizon": "medium-term",
        "confidence": "High",
        "topic_tags": ["land_use", "soil"],
    },
}


def _select_interventions(active_vars: list[str], profile: dict) -> list[str]:
    """Select the most relevant intervention keys given the active variables and profile."""
    selected = []

    # Pattern: low SOC + low rainfall + monoculture
    has_soc = "soil_organic_carbon" in active_vars
    has_rainfall = "rainfall" in active_vars
    has_mono = "monoculture" in active_vars
    has_defor = "deforestation" in active_vars
    has_frag = "habitat_fragmentation" in active_vars
    has_pest = "pesticide_pressure" in active_vars

    if has_soc and has_rainfall and has_mono:
        selected.extend(["legume_intercropping", "cover_crops", "agroforestry"])
    elif has_soc and has_mono:
        selected.extend(["crop_rotation", "cover_crops", "reduced_tillage"])
    elif has_soc and has_rainfall:
        selected.extend(["cover_crops", "water_harvesting", "reduced_tillage"])
    elif has_soc:
        selected.extend(["cover_crops", "reduced_tillage"])
    elif has_mono:
        selected.extend(["crop_rotation", "legume_intercropping"])

    if has_defor:
        selected.extend(["restoration_planting", "agroforestry", "riparian_buffers"])

    if has_frag:
        selected.extend(["native_hedgerows", "habitat_corridors", "riparian_buffers"])

    if has_pest:
        selected.extend(["integrated_pest_management", "buffer_strips"])

    if not selected:
        # Fallback: always offer basic interventions
        selected = ["cover_crops", "native_hedgerows", "water_harvesting"]

    # Deduplicate preserving order, limit to 3
    seen = set()
    unique = [s for s in selected if not (s in seen or seen.add(s))]
    return unique[:3]


# ─── public API ─────────────────────────────────────────────────────────────

def generate_reasoning_chain(profile: dict) -> dict:
    """
    Main reasoning entry point.
    Returns:
        {
            "active_variables": [...],
            "interventions": [...],
            "relationship_chain": [...],
            "intervention_details": [{...}]
        }
    """
    active_vars = _detect_active_variables(profile)
    chain = _build_relationship_chain(active_vars)
    interventions = _select_interventions(active_vars, profile)

    details = []
    for key in interventions:
        if key in INTERVENTION_DETAILS:
            details.append({**INTERVENTION_DETAILS[key], "intervention_key": key})

    return {
        "active_variables": active_vars,
        "interventions": interventions,
        "relationship_chain": chain,
        "intervention_details": details,
    }


def format_active_variables_for_display(active_vars: list[str]) -> list[str]:
    """Convert internal variable keys to human-readable descriptions."""
    label_map = {
        "soil_organic_carbon": "Low soil organic carbon (< 0.6%)",
        "rainfall": "Low rainfall pattern",
        "monoculture": "Monoculture farming system",
        "land_use_intensity": "High land use intensity",
        "habitat_fragmentation": "Habitat fragmentation / poor connectivity",
        "deforestation": "Deforestation pressure",
        "pesticide_pressure": "Pesticide pressure",
        "temperature": "Elevated temperature (> 30°C)",
    }
    return [label_map.get(v, v.replace("_", " ").title()) for v in active_vars]
