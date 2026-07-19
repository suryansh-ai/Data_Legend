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

// Simple in-memory cache with TTL to avoid re-fetching data on navigation
const _cache = new Map<string, { data: any; expiry: number }>()
const CACHE_TTL = 30000 // 30 seconds for fast navigation

function getCached<T>(key: string): T | null {
  const entry = _cache.get(key)
  if (entry && Date.now() < entry.expiry) return entry.data as T
  _cache.delete(key)
  return null
}

function setCache(key: string, data: any): void {
  _cache.set(key, { data, expiry: Date.now() + CACHE_TTL })
  // Trim cache if it grows too large
  if (_cache.size > 50) {
    const oldest = _cache.keys().next().value
    if (oldest) _cache.delete(oldest)
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  // Only cache GET requests (read-only data)
  const method = options?.method || 'GET'
  const cacheKey = method === 'GET' ? path : null
  
  // Check cache first
  if (cacheKey) {
    const cached = getCached<T>(cacheKey)
    if (cached) return cached
  }
  
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `HTTP ${res.status}`)
  }
  const data = await res.json()
  
  // Store in cache for GET requests
  if (cacheKey) {
    setCache(cacheKey, data)
  }
  
  return data
}

let autocompleteCache: any[] | null = null
let useBackendAutocomplete = true
let isFetchingCache = false

async function prefetchAutocompleteCache() {
  if (isFetchingCache || autocompleteCache) return
  isFetchingCache = true
  try {
    const all = await request<any[]>('/facilities/map')
    autocompleteCache = all.map(f => ({
      unique_id: f.unique_id,
      name: f.name || '',
      city: f.city || '',
      state: f.state || '',
    }))
  } catch (err) {
    console.error('Failed to prefetch autocomplete cache:', err)
  } finally {
    isFetchingCache = false
  }
}

export const api = {
  async get<T>(path: string, options?: RequestInit): Promise<T> {
    return request<T>(path, { method: 'GET', ...options })
  },

  async post<T>(path: string, body?: any, options?: RequestInit): Promise<T> {
    return request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    })
  },

  async put<T>(path: string, body?: any, options?: RequestInit): Promise<T> {
    return request<T>(path, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    })
  },

  async delete<T>(path: string, body?: any, options?: RequestInit): Promise<T> {
    return request<T>(path, {
      method: 'DELETE',
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    })
  },

  async autocomplete(q: string): Promise<Array<{ unique_id: string; name: string; city: string; state: string }>> {
    const qLower = q.toLowerCase()

    // If backend is known to be missing, do an instant in-memory lookup
    if (!useBackendAutocomplete && autocompleteCache) {
      const startsWith = autocompleteCache.filter(f => f.name.toLowerCase().startsWith(qLower))
      const contains = autocompleteCache.filter(f => f.name.toLowerCase().includes(qLower) && !startsWith.some(sw => sw.unique_id === f.unique_id))
      return [...startsWith, ...contains].slice(0, 10)
    }

    try {
      return await request<Array<{ unique_id: string; name: string; city: string; state: string }>>(`/facilities/autocomplete?q=${encodeURIComponent(q)}`)
    } catch (err) {
      console.warn('Backend autocomplete endpoint failed, switching to client-side filtering.', err)
      useBackendAutocomplete = false // Disable future backend network checks
      
      if (!autocompleteCache) {
        await prefetchAutocompleteCache()
      }

      if (autocompleteCache) {
        const startsWith = autocompleteCache.filter(f => f.name.toLowerCase().startsWith(qLower))
        const contains = autocompleteCache.filter(f => f.name.toLowerCase().includes(qLower) && !startsWith.some(sw => sw.unique_id === f.unique_id))
        return [...startsWith, ...contains].slice(0, 10)
      }
      return []
    }
  },

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
