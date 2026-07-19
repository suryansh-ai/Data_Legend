export interface Facility {
  unique_id: string
  name: string
  description: string
  capability: string | string[]
  procedure: string | string[]
  equipment: string | string[]
  specialties: string | string[]
  numberDoctors: number | null
  capacity: number | null
  address_stateOrRegion: string
  address_city: string
  latitude: number | null
  longitude: number | null
  _trust_score: number | null
  _trust_signal: string | null
  _total_claims: number | null
  _corroborated: number | null
  [key: string]: unknown
}

export interface TrustResult {
  overall_trust: number
  overall_signal: 'CORROBORATED' | 'CLAIMED_ONLY' | 'WEAK' | 'UNKNOWN'
  capabilities: Record<string, CapabilityResult>
  metadata: TrustMetadata
}

export interface CapabilityResult {
  signal: string
  score: number
  evidence: EvidenceItem[]
  gaps: string[]
}

export interface EvidenceItem {
  field: string
  text: string
  weight: number
}

export interface TrustMetadata {
  fields_with_data: number
  fields_empty: number
  total_claims: number
  corroborated_claims: number
}

export interface FacilityNote {
  note: string
  created_at: string
}

export interface Override {
  original_score: number
  new_score: number
  reason: string
  created_at: string
}

export interface FacilityStats {
  total: number
  states: number
  cities: number
  with_description: number
  with_capability: number
  with_procedure: number
  with_equipment: number
  with_specialties: number
  with_doctors: number
  with_capacity: number
}

export interface CoverageGap {
  state: string
  total: number
  avg_trust: number
  low_trust_count: number
  facilities_per_million: number | null
}

export interface SearchParams {
  q?: string
  state?: string
  city?: string
  trust_signal?: string
  capability?: string
  page?: number
  limit?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  pages: number
}

export type Theme = 'light' | 'dark' | 'system'
