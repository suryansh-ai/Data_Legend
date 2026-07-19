import type {
  Facility,
  TrustResult,
  FacilityNote,
  Override,
  FacilityStats,
  CoverageGap,
  SearchParams,
  PaginatedResponse,
} from './types'

const BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  async getFacilities(params: SearchParams = {}): Promise<PaginatedResponse<Facility>> {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') query.set(k, String(v))
    })
    return request(`/facilities?${query}`)
  },

  async getFacility(id: string): Promise<Facility> {
    return request(`/facilities/${id}`)
  },

  async getMapData(params: { state?: string; trust_signal?: string } = {}) {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v) query.set(k, v)
    })
    return request<Facility[]>(`/facilities/map?${query}`)
  },

  async scoreFacility(id: string): Promise<TrustResult> {
    return request(`/trust/score/${id}`, { method: 'POST' })
  },

  async batchScore(ids: string[]): Promise<TrustResult[]> {
    return request('/trust/batch', {
      method: 'POST',
      body: JSON.stringify({ facility_ids: ids }),
    })
  },

  async search(q: string, params: SearchParams = {}): Promise<PaginatedResponse<Facility>> {
    const query = new URLSearchParams({ q, ...Object.fromEntries(
      Object.entries(params).filter(([, v]) => v != null && v !== '')
    ) })
    return request(`/search?${query}`)
  },

  async getStats(): Promise<FacilityStats> {
    return request('/stats')
  },

  async getStateStats(): Promise<CoverageGap[]> {
    return request('/stats/states')
  },

  async getTrustDistribution(): Promise<Record<string, number>> {
    return request('/stats/trust-distribution')
  },

  async getColumnCompleteness(): Promise<Record<string, number>> {
    return request('/stats/column-completeness')
  },

  async getNotes(facilityId: string): Promise<FacilityNote[]> {
    return request(`/persistence/notes/${facilityId}`)
  },

  async addNote(facilityId: string, note: string): Promise<{ ok: boolean }> {
    return request('/persistence/notes', {
      method: 'POST',
      body: JSON.stringify({ facility_id: facilityId, note }),
    })
  },

  async getOverride(facilityId: string): Promise<Override | null> {
    return request(`/persistence/overrides/${facilityId}`)
  },

  async setOverride(facilityId: string, originalScore: number, newScore: number, reason: string): Promise<{ ok: boolean }> {
    return request('/persistence/overrides', {
      method: 'POST',
      body: JSON.stringify({
        facility_id: facilityId,
        original_score: originalScore,
        new_score: newScore,
        reason,
      }),
    })
  },

  async getShortlist(): Promise<string[]> {
    return request('/persistence/shortlist')
  },

  async addToShortlist(facilityId: string): Promise<{ ok: boolean }> {
    return request('/persistence/shortlist', {
      method: 'POST',
      body: JSON.stringify({ facility_id: facilityId }),
    })
  },

  async removeFromShortlist(facilityId: string): Promise<{ ok: boolean }> {
    return request('/persistence/shortlist', {
      method: 'DELETE',
      body: JSON.stringify({ facility_id: facilityId }),
    })
  },
}
