export interface LocationProfile {
  country?: string;
  state?: string;
  region?: string;
  latitude?: number;
  longitude?: number;
}

export interface SoilProfile {
  ph?: number;
  organic_carbon_percent?: number;
  moisture_percent?: number;
  microbial_activity?: string;
  erosion_risk?: string;
}

export interface ClimateProfile {
  annual_rainfall_mm?: number;
  temperature_c?: number;
  drought_risk?: string;
  seasonality?: string;
}

export interface LandProfile {
  land_use?: string;
  crop?: string;
  cropping_system?: string;
  canopy_cover_percent?: number;
  habitat_fragmentation?: string;
}

export interface BiodiversityProfile {
  species_richness?: number;
  habitat_diversity?: string;
  pollinator_abundance?: string;
  functional_diversity?: string;
}

export interface HumanImpactProfile {
  pesticide_pressure?: string;
  fertilizer_intensity?: string;
  deforestation?: string;
  groundwater_extraction?: string;
  pollution?: string;
}

export interface EnvironmentalState {
  location: LocationProfile;
  soil: SoilProfile;
  climate: ClimateProfile;
  land: LandProfile;
  biodiversity: BiodiversityProfile;
  human_impact: HumanImpactProfile;
}

export interface ImpactedMetric {
  metric: string;
  direction: 'increase' | 'decrease';
  expected_time: 'short_term' | 'medium_term' | 'long_term';
  scientific_basis?: string;
}

export interface ScientificEvidence {
  title: string;
  organization: string;
  authors?: string;
  year: number;
  url: string;
  relevance: string;
  source_type: string;
  metrics_supported: string[];
}

export interface BiodiversityRecommendation {
  id: string;
  title: string;
  action: string;
  why_it_works: string;
  impacted_metrics: ImpactedMetric[];
  time_horizon: {
    short_term: string;
    medium_term: string;
    long_term: string;
  };
  evidence: ScientificEvidence[];
  confidence: 'low' | 'medium' | 'high';
  confidence_rationale?: string;
  connected_variables: string[];
}

export interface TransparencyTrace {
  user_inputs: Record<string, any>;
  variables_considered: string[];
  relationships_identified: string[];
  causal_chains: string[][];
  retrieved_sources_count: number;
  relevant_sources_used: number;
  evidence_validation_summary: string;
  confidence_breakdown: Record<string, any>;
}

export interface ClarificationQuestion {
  field: string;
  priority: 'required' | 'highly_useful' | 'optional';
  question: string;
  unit_or_format: string;
}

export interface ChatResponse {
  conversation_id: string;
  status: 'needs_information' | 'diagnosed';
  overall_diagnosis?: string;
  clarification_questions: string[];
  structured_questions?: ClarificationQuestion[];
  environmental_state: EnvironmentalState;
  recommendations: BiodiversityRecommendation[];
  causal_pathways: string[];
  transparency?: TransparencyTrace;
  insufficient_evidence_notice?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  status?: 'needs_information' | 'diagnosed';
  clarification_questions?: string[];
  recommendations?: BiodiversityRecommendation[];
  causal_pathways?: string[];
  transparency?: TransparencyTrace;
  insufficient_evidence_notice?: string;
}

export interface SourceItem {
  id: string;
  title: string;
  authors?: string;
  organization: string;
  year: number;
  url: string;
  topic: string;
  region: string;
  metrics: string[];
}
