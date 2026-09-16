export interface SoilData {
  ph?: number;
  organic_carbon_percent?: number;
  moisture_percent?: number;
  structure?: string;
  nutrient_availability?: string;
}

export interface LandUseData {
  primary_type?: string;
  cropping_system?: string;
  crop?: string;
}

export interface BiodiversityData {
  species_richness?: string;
  habitat_diversity?: string;
  pollinator_presence?: string;
  native_vegetation_percent?: number;
  ecological_connectivity?: string;
}

export interface ClimateData {
  temperature_c?: number;
  rainfall_mm?: number;
  rainfall_pattern?: string;
  seasonality?: string;
  drought_conditions?: boolean;
}

export interface HumanImpactData {
  pollution_level?: string;
  pesticide_pressure?: string;
  deforestation_pressure?: string;
  habitat_disturbance?: string;
}

export interface EnvironmentalProfile {
  region?: string;
  latitude?: number;
  longitude?: number;
  soil?: SoilData;
  land_use?: LandUseData;
  biodiversity?: BiodiversityData;
  climate?: ClimateData;
  human_impact?: HumanImpactData;
}

export interface EvidenceItem {
  title: string;
  source: string;
  year?: number;
  url?: string;
  supporting_excerpt: string;
  topic?: string;
  variables?: string[];
}

export interface RecommendationItem {
  title: string;
  action: string;
  reasoning: string;
  impacted_metrics: string[];
  time_horizon: string;
  confidence: string;
  evidence: EvidenceItem[];
}

export interface ReasoningTrace {
  variables_detected: string[];
  missing_variables: string[];
  retrieved_evidence_count: number;
  environmental_relationships: string[];
  evidence_titles: string[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  recommendations?: RecommendationItem[];
  reasoning_trace?: ReasoningTrace;
  needs_clarification?: boolean;
  clarification_questions?: string[];
  demo_mode?: boolean;
  timestamp: Date;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  recommendations?: RecommendationItem[];
  reasoning_trace?: ReasoningTrace;
  environmental_profile?: EnvironmentalProfile;
  needs_clarification: boolean;
  clarification_questions?: string[];
  demo_mode: boolean;
}

export interface SystemStatus {
  database: boolean;
  vector_db: boolean;
  embeddings: boolean;
  ollama_available: boolean;
  knowledge_base_docs: number;
  ollama_model?: string;
  demo_mode: boolean;
}

export interface DemoScenario {
  id: string;
  name: string;
  description: string;
  profile: EnvironmentalProfile;
  initial_message: string;
}
