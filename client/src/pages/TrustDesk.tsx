import { useEffect, useState, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ShieldCheck, Filter, MapPin } from 'lucide-react'
import { api } from '@/lib/api'
import SearchBar from '@/components/SearchBar'
import DataTable from '@/components/DataTable'
import TrustBadge from '@/components/TrustBadge'
import MapView from '@/components/MapView'
import ExportButton from '@/components/ExportButton'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'
import type { Facility, FacilityStats, PaginatedResponse } from '@/lib/types'
import { truncate } from '@/lib/utils'

export default function TrustDesk() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [facilities, setFacilities] = useState<Facility[]>([])
  const [allFacilities, setAllFacilities] = useState<Facility[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [state, setState] = useState(searchParams.get('state') || '')
  const [trustSignal, setTrustSignal] = useState(searchParams.get('trust_signal') || '')
  const [viewMode, setViewMode] = useState<'table' | 'map'>('table')

  const fetchFacilities = useCallback(async () => {
    setLoading(true)
    try {
      const params = {
        q: query || undefined,
        state: state || undefined,
        trust_signal: trustSignal || undefined,
        page,
        limit: 20,
      }
      if (query) {
        const res = await api.search(query, params)
        setFacilities(res.items)
        setTotal(res.total)
      } else {
        const res = await api.getFacilities(params)
        setFacilities(res.items)
        setTotal(res.total)
      }
    } catch {
      setFacilities([])
    } finally {
      setLoading(false)
    }
  }, [query, state, trustSignal, page])

  useEffect(() => { fetchFacilities() }, [fetchFacilities])

  useEffect(() => {
    api.getMapData({ state: state || undefined, trust_signal: trustSignal || undefined })
      .then(setAllFacilities)
      .catch(() => setAllFacilities([]))
  }, [state, trustSignal])

  const handleSearch = () => {
    setPage(1)
    const params = new URLSearchParams()
    if (query) params.set('q', query)
    if (state) params.set('state', state)
    if (trustSignal) params.set('trust_signal', trustSignal)
    setSearchParams(params)
  }

  const columns = [
    {
      key: 'name',
      label: 'Facility',
      sortable: true,
      render: (f: Facility) => (
        <div>
          <button
            onClick={(e) => { e.stopPropagation(); navigate(`/facility/${f.unique_id}`) }}
            className="font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
          >
            {truncate(f.name || 'Unknown', 40)}
          </button>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            {f.address_city || ''} {f.address_stateOrRegion || ''}
          </p>
        </div>
      ),
    },
    {
      key: '_trust_score',
      label: 'Trust Score',
      sortable: true,
      render: (f: Facility) => <TrustBadge score={f._trust_score} signal={f._trust_signal} size="sm" />,
    },
    {
      key: 'numberDoctors',
      label: 'Doctors',
      sortable: true,
      render: (f: Facility) => <span className="font-mono text-xs">{f.numberDoctors ?? '—'}</span>,
    },
    {
      key: 'capacity',
      label: 'Capacity',
      sortable: true,
      render: (f: Facility) => <span className="font-mono text-xs">{f.capacity ?? '—'}</span>,
    },
    {
      key: '_total_claims',
      label: 'Claims',
      sortable: true,
      render: (f: Facility) => (
        <span className="text-xs">
          <span className="font-mono">{f._total_claims ?? 0}</span>
          <span style={{ color: 'var(--text-muted)' }}> / </span>
          <span className="font-mono text-emerald-500">{f._corroborated ?? 0}</span>
        </span>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          <ShieldCheck className="mr-2 inline h-6 w-6 text-emerald-500" />
          Trust Desk
        </h1>
        <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Search, filter, and score healthcare facility claims
        </p>
      </div>

      <SearchBar
        value={query}
        onChange={setQuery}
        onSubmit={handleSearch}
        placeholder="Search by name, city, or capability..."
        filters={
          <div className="flex flex-wrap gap-3">
            <select
              value={state}
              onChange={(e) => { setState(e.target.value); setPage(1) }}
              className="input w-auto"
            >
              <option value="">All States</option>
              {['Andhra Pradesh', 'Bihar', 'Delhi', 'Gujarat', 'Karnataka', 'Kerala', 'Madhya Pradesh',
                'Maharashtra', 'Odisha', 'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telangana', 'Uttar Pradesh',
                'West Bengal'].map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <select
              value={trustSignal}
              onChange={(e) => { setTrustSignal(e.target.value); setPage(1) }}
              className="input w-auto"
            >
              <option value="">All Trust Levels</option>
              <option value="CORROBORATED">Corroborated</option>
              <option value="CLAIMED_ONLY">Claimed Only</option>
              <option value="WEAK">Weak</option>
              <option value="UNKNOWN">Unknown</option>
            </select>
          </div>
        }
      />

      <div className="flex items-center justify-between">
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          {total.toLocaleString('en-IN')} facilities found
        </p>
        <div className="flex items-center gap-2">
          <ExportButton data={facilities} filename="trust-desk-export" />
          <div className="flex rounded-lg border overflow-hidden" style={{ borderColor: 'var(--border-color)' }}>
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-1.5 text-xs font-medium ${viewMode === 'table' ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/30' : ''}`}
              style={viewMode !== 'table' ? { color: 'var(--text-secondary)' } : undefined}
            >
              Table
            </button>
            <button
              onClick={() => setViewMode('map')}
              className={`px-3 py-1.5 text-xs font-medium ${viewMode === 'map' ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/30' : ''}`}
              style={viewMode !== 'map' ? { color: 'var(--text-secondary)' } : undefined}
            >
              <MapPin className="inline h-3 w-3 mr-1" />
              Map
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : viewMode === 'table' ? (
        <>
          <DataTable
            columns={columns}
            data={facilities as unknown as Record<string, unknown>[]}
            onRowClick={(f) => navigate(`/facility/${f.unique_id as string}`)}
            emptyMessage="No facilities match your search"
          />
          {total > 20 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Page {page} of {Math.ceil(total / 20)}
              </span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={page >= Math.ceil(total / 20)}
                className="btn-secondary disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      ) : (
        <MapView
          facilities={allFacilities}
          height="600px"
          onFacilityClick={(f) => navigate(`/facility/${f.unique_id}`)}
        />
      )}
    </div>
  )
}
