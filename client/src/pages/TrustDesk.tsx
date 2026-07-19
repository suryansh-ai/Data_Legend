import { useEffect, useState, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ShieldCheck, Filter, MapPin, Grid, Users, Bed, Check, X, Sparkles, ChevronRight, HelpCircle, Star } from 'lucide-react'
import { api } from '@/lib/api'
import TrustBadge from '@/components/TrustBadge'
import MapView from '@/components/MapView'
import ExportButton from '@/components/ExportButton'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'
import type { Facility } from '@/lib/types'
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
  const [viewMode, setViewMode] = useState<'grid' | 'map' | 'shortlist'>('grid')
  const [shortlistedFacilities, setShortlistedFacilities] = useState<Facility[]>([])
  const [shortlistNotes, setShortlistNotes] = useState<Record<string, string>>({})
  const [loadingShortlist, setLoadingShortlist] = useState(false)

  const [suggestions, setSuggestions] = useState<any[]>([])
  const [showDropdown, setShowDropdown] = useState(false)

  const handleQueryChange = async (val: string) => {
    setQuery(val)
    if (val.trim().length >= 2) {
      try {
        const res = await api.autocomplete(val)
        setSuggestions(res)
        setShowDropdown(true)
      } catch (err) {
        console.error(err)
      }
    } else {
      setSuggestions([])
      setShowDropdown(false)
    }
  }

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

  const loadShortlistDetails = useCallback(async () => {
    setLoadingShortlist(true)
    try {
      const ids = await api.getShortlist()
      if (ids.length > 0) {
        const details = await Promise.all(
          ids.map(async (id) => {
            try {
              return await api.getFacility(id)
            } catch {
              return null;
            }
          })
        )
        const validDetails = details.filter((d): d is Facility => d !== null)
        setShortlistedFacilities(validDetails)

        const notesMap: Record<string, string> = {}
        await Promise.all(
          validDetails.map(async (f) => {
            try {
              const notesList = await api.getNotes(f.unique_id)
              if (notesList.length > 0) {
                notesMap[f.unique_id] = notesList[0].note
              }
            } catch {}
          })
        )
        setShortlistNotes(notesMap)
      } else {
        setShortlistedFacilities([])
      }
    } catch (err) {
      console.error('Failed to load shortlist:', err)
    } finally {
      setLoadingShortlist(false)
    }
  }, [])

  useEffect(() => {
    if (viewMode === 'shortlist') {
      loadShortlistDetails()
    }
  }, [viewMode, loadShortlistDetails])

  const handleExportShortlist = () => {
    const headers = ['Unique ID', 'Hospital Name', 'City', 'State', 'Trust Score', 'Trust Level', 'Verified Doctors', 'Patient Beds', 'Logged Verification Notes'];
    const rows = shortlistedFacilities.map(f => [
      f.unique_id,
      f.name,
      f.address_city || '',
      f.address_stateOrRegion || '',
      (f._trust_score ?? 0).toFixed(0),
      f._trust_signal || 'UNKNOWN',
      f.numberDoctors ?? 0,
      f.capacity ?? 0,
      shortlistNotes[f.unique_id] || 'No notes'
    ]);
    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(e => e.map(val => `"${String(val).replace(/"/g, '""')}"`).join(','))].join('\n');
    
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", "audited_coordinator_shortlist.csv")
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleSearch = () => {
    setPage(1)
    const params = new URLSearchParams()
    if (query) params.set('q', query)
    if (state) params.set('state', state)
    if (trustSignal) params.set('trust_signal', trustSignal)
    setSearchParams(params)
  }

  const getSignalMeta = (signal: string | null) => {
    switch (signal) {
      case 'CORROBORATED':
        return {
          label: 'Double-Checked & Verified',
          desc: 'High Confidence: Stated in descriptions, logs, or doctor lists.',
          color: 'text-emerald-700 bg-emerald-50 dark:bg-emerald-950/30 dark:text-emerald-400 border-emerald-200/50',
          dot: 'bg-emerald-500',
        }
      case 'CLAIMED_ONLY':
        return {
          label: 'Single Claim (Unverified)',
          desc: 'Medium Confidence: Mentioned in one place but needs verification.',
          color: 'text-amber-700 bg-amber-50 dark:bg-amber-950/30 dark:text-amber-400 border-amber-200/50',
          dot: 'bg-amber-500',
        }
      case 'WEAK':
        return {
          label: 'Caution: Negated or Aspirational',
          desc: 'Low Confidence: Listed as "future planned" or currently not functioning.',
          color: 'text-red-700 bg-red-50 dark:bg-red-950/30 dark:text-red-400 border-red-200/50',
          dot: 'bg-red-500',
        }
      default:
        return {
          label: 'No Evidence Found',
          desc: 'Insufficient data: No matching keywords or descriptions.',
          color: 'text-slate-600 bg-slate-50 dark:bg-slate-800 dark:text-slate-400 border-slate-200',
          dot: 'bg-slate-400',
        }
    }
  }

  // Parse capability string into array safely
  const parseCapabilities = (capStr: any): string[] => {
    if (!capStr) return []
    if (Array.isArray(capStr)) return capStr
    try {
      const parsed = JSON.parse(capStr)
      if (Array.isArray(parsed)) return parsed
    } catch {}
    return String(capStr).split(',').map(s => s.trim()).filter(Boolean)
  }

  return (
    <div className="space-y-8 py-2">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-primary)' }}>
              Facility Trust Desk
            </h1>
            <span className="rounded-full bg-teal-50 px-2.5 py-0.5 text-xs font-bold text-teal-700 dark:bg-teal-950/40 dark:text-teal-400">
              {total.toLocaleString('en-IN')} Monitored
            </span>
          </div>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Search hospital claims, check evidence verification, and override trust scores.
          </p>
        </div>

        {/* View Mode & Export */}
        <div className="flex items-center gap-3">
          <ExportButton data={facilities} filename="trust-desk-export" />
          <div className="flex rounded-xl border overflow-hidden p-1 bg-slate-100 dark:bg-slate-800" style={{ borderColor: 'var(--border-color)' }}>
            <button
              onClick={() => setViewMode('grid')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                viewMode === 'grid'
                  ? 'bg-white shadow-sm dark:bg-slate-700 text-teal-700 dark:text-teal-400'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              <Grid className="h-3.5 w-3.5" />
              <span>Grid List</span>
            </button>
            <button
              onClick={() => setViewMode('map')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                viewMode === 'map'
                  ? 'bg-white shadow-sm dark:bg-slate-700 text-teal-700 dark:text-teal-400'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              <MapPin className="h-3.5 w-3.5" />
              <span>Map View</span>
            </button>
            <button
              onClick={() => setViewMode('shortlist')}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                viewMode === 'shortlist'
                  ? 'bg-white shadow-sm dark:bg-slate-700 text-teal-700 dark:text-teal-400'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              <Star className="h-3.5 w-3.5" />
              <span>Shortlist</span>
            </button>
          </div>
        </div>
      </div>

      {/* Filter / Search Form */}
      <div className="card p-6 space-y-4">
        <div className="flex flex-col md:flex-row gap-3 relative">
          <div className="relative flex-1">
            <input
              type="text"
              value={query}
              onChange={(e) => handleQueryChange(e.target.value)}
              onFocus={() => query.trim().length >= 2 && setShowDropdown(true)}
              onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search by name, city, or capability (e.g. ICU, dialysis, Patna)..."
              className="input w-full"
            />

            {/* Autocomplete Dropdown */}
            {showDropdown && suggestions.length > 0 && (
              <div
                className="absolute left-0 right-0 mt-1 max-h-60 overflow-y-auto rounded-xl border bg-white p-2 shadow-lg dark:bg-slate-900 z-50 text-[11px]"
                style={{ borderColor: 'var(--border-color)' }}
              >
                {suggestions.map((s) => (
                  <button
                    key={s.unique_id}
                    onClick={() => {
                      setQuery(s.name)
                      setShowDropdown(false)
                      navigate(`/facility/${s.unique_id}`)
                    }}
                    className="w-full text-left rounded-lg px-2.5 py-1.5 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800 flex flex-col gap-0.5"
                  >
                    <span className="font-bold text-slate-800 dark:text-slate-100 line-clamp-1">{s.name}</span>
                    <span className="text-[10px] text-slate-400 font-semibold">{s.city ? `${s.city}, ` : ''}{s.state}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          <button onClick={handleSearch} className="btn-primary">
            Search
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-400">
            <Filter className="h-3.5 w-3.5" />
            <span>Filter By:</span>
          </div>

          <select
            value={state}
            onChange={(e) => { setState(e.target.value); setPage(1) }}
            className="input py-1.5 text-xs w-auto border-slate-200"
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
            className="input py-1.5 text-xs w-auto border-slate-200"
          >
            <option value="">All Verification Levels</option>
            <option value="CORROBORATED">Verified & Corroborated</option>
            <option value="CLAIMED_ONLY">Stated but Unverified</option>
            <option value="WEAK">Weak / Caution</option>
            <option value="UNKNOWN">Unknown / No details</option>
          </select>
        </div>
      </div>

      {/* List Output */}
      {loading ? (
        <LoadingSpinner />
      ) : viewMode === 'grid' ? (
        facilities.length === 0 ? (
          <EmptyState message="No matching hospitals found. Try broad searches like 'Patna' or 'maternity'." />
        ) : (
          <div className="space-y-6">
            {/* Visual Grid Catalog */}
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {facilities.map((f, i) => {
                const meta = getSignalMeta(f._trust_signal)
                const caps = parseCapabilities(f.capability)

                return (
                  <motion.div
                    key={f.unique_id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: Math.min(i * 0.05, 0.4) }}
                    onClick={() => navigate(`/facility/${f.unique_id}`)}
                    className="card p-5 group cursor-pointer flex flex-col justify-between hover:border-slate-300 dark:hover:border-slate-700"
                  >
                    <div>


                      {/* Trust Badge Bar */}
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-1.5">
                          <span className={`h-2.5 w-2.5 rounded-full ${meta.dot}`} />
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {meta.label}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="text-xs font-bold text-slate-400">Score:</span>
                          <span className="text-sm font-extrabold text-teal-700 dark:text-teal-400">
                            {(f._trust_score ?? 0).toFixed(0)}%
                          </span>
                        </div>
                      </div>

                      {/* Title */}
                      <h3 className="font-extrabold text-base line-clamp-1 group-hover:text-teal-700" style={{ color: 'var(--text-primary)' }}>
                        {f.name}
                      </h3>
                      <p className="text-xs font-semibold mt-0.5" style={{ color: 'var(--text-muted)' }}>
                        {f.address_city ? `${f.address_city}, ` : ''}{f.address_stateOrRegion}
                      </p>

                      {/* Capabilities Overview */}
                      <div className="mt-4 pt-3 border-t space-y-1.5" style={{ borderColor: 'var(--border-color)' }}>
                        <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Claimed services</p>
                        {caps.length === 0 ? (
                          <p className="text-xs italic" style={{ color: 'var(--text-muted)' }}>No specialized services listed</p>
                        ) : (
                          <div className="flex flex-wrap gap-1">
                            {caps.slice(0, 3).map(cap => (
                              <span key={cap} className="inline-flex items-center gap-0.5 rounded bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 text-[10px] font-bold text-slate-700 dark:text-slate-300">
                                <Check className="h-2.5 w-2.5 text-teal-600" />
                                {cap}
                              </span>
                            ))}
                            {caps.length > 3 && (
                              <span className="text-[10px] font-bold text-slate-400 self-center">
                                +{caps.length - 3} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Footer Stats */}
                    <div className="mt-5 pt-3 border-t flex items-center justify-between text-xs font-bold text-slate-600 dark:text-slate-400" style={{ borderColor: 'var(--border-color)' }}>
                      <div className="flex items-center gap-3">
                        <span className="flex items-center gap-1">
                          <Users className="h-3.5 w-3.5 text-slate-400" />
                          {f.numberDoctors ?? '—'} Doctors
                        </span>
                        <span className="flex items-center gap-1">
                          <Bed className="h-3.5 w-3.5 text-slate-400" />
                          {f.capacity ?? '—'} Beds
                        </span>
                      </div>
                      <ChevronRight className="h-4 w-4 text-slate-400" />
                    </div>
                  </motion.div>
                )
              })}
            </div>

            {/* Pagination */}
            {total > 20 && (
              <div className="flex items-center justify-center gap-3 pt-6">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn-secondary disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="text-xs font-bold" style={{ color: 'var(--text-secondary)' }}>
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
          </div>
        )
      ) : viewMode === 'map' ? (
        <MapView
          facilities={allFacilities}
          height="600px"
          onFacilityClick={(f) => navigate(`/facility/${f.unique_id}`)}
        />
      ) : (
        <div className="card p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
            <div>
              <h2 className="text-base font-black text-slate-800 flex items-center gap-2">
                <Star className="h-4.5 w-4.5 text-amber-500 fill-current" />
                Curated Auditor Shortlist
              </h2>
              <p className="text-[10px] text-slate-400">
                Batch list of verified health clinics with logged verification notes.
              </p>
            </div>
            {shortlistedFacilities.length > 0 && (
              <button
                onClick={handleExportShortlist}
                className="btn-primary flex items-center gap-1.5 py-1.5 px-4 text-xs font-bold"
              >
                <span>📥 Export Shortlist (CSV)</span>
              </button>
            )}
          </div>

          {loadingShortlist ? (
            <LoadingSpinner />
          ) : shortlistedFacilities.length === 0 ? (
            <div className="py-12 text-center space-y-2">
              <Star className="h-8 w-8 text-slate-300 mx-auto" />
              <p className="text-xs font-bold text-slate-600">No facilities shortlisted yet</p>
              <p className="text-[10px] text-slate-400">Add them from their details page to build your verified referral batch.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {shortlistedFacilities.map((f) => (
                <div
                  key={f.unique_id}
                  className="p-5 rounded-2xl border bg-slate-50/50 flex flex-col sm:flex-row justify-between sm:items-center gap-4 hover:border-slate-300 transition-colors"
                  style={{ borderColor: 'var(--border-color)' }}
                >
                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <h4
                        onClick={() => navigate(`/facility/${f.unique_id}`)}
                        className="font-extrabold text-sm text-slate-800 hover:text-teal-700 cursor-pointer hover:underline"
                      >
                        {f.name}
                      </h4>
                      <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-teal-50 text-teal-700 border border-teal-100 uppercase">
                        {(f._trust_score ?? f.trust_score ?? 0).toFixed(0)}% Trust ({f._trust_signal})
                      </span>
                    </div>
                    <p className="text-[10px] font-bold text-slate-400">
                      {f.address_city || f.city ? `${f.address_city || f.city}, ` : ''}{f.address_stateOrRegion || f.state}
                    </p>
                    {shortlistNotes[f.unique_id] ? (
                      <div className="text-[11px] leading-relaxed text-slate-600 italic bg-white p-2.5 rounded-lg border mt-2 font-semibold border-slate-200">
                        "Audit Note: {shortlistNotes[f.unique_id]}"
                      </div>
                    ) : (
                      <p className="text-[10px] italic text-slate-400 font-semibold mt-1">No notes logged yet.</p>
                    )}
                  </div>

                  <button
                    onClick={async (e) => {
                      e.stopPropagation();
                      await api.removeFromShortlist(f.unique_id);
                      loadShortlistDetails();
                    }}
                    className="text-xs font-bold text-red-600 hover:text-red-700 border border-red-200 px-3 py-1.5 rounded-lg bg-white shrink-0 self-start sm:self-center"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
