import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { MapPin, AlertTriangle, TrendingDown, Shield, Sparkles, Building2, HelpCircle } from 'lucide-react'
import { api } from '@/lib/api'
import MapView from '@/components/MapView'
import LoadingSpinner from '@/components/LoadingSpinner'
import type { CoverageGap, Facility } from '@/lib/types'

export default function MedicalDesert() {
  const navigate = useNavigate()
  const [stateStats, setStateStats] = useState<CoverageGap[]>([])
  const [facilities, setFacilities] = useState<Facility[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedState, setSelectedState] = useState<string | null>(null)
  const [mapFilter, setMapFilter] = useState<'all' | 'emergency' | 'large'>('all')

  useEffect(() => {
    Promise.all([api.getStateStats(), api.getMapData()])
      .then(([ss, f]) => { setStateStats(ss); setFacilities(f) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  const filteredFacilities = selectedState
    ? facilities.filter(f => f.state === selectedState || f.address_stateOrRegion === selectedState)
    : facilities

  const displayedFacilities = filteredFacilities.filter(f => {
    if (mapFilter === 'emergency') {
      const caps = String(f.capability || '').toLowerCase();
      return caps.includes('icu') || caps.includes('emergency') || caps.includes('trauma');
    }
    if (mapFilter === 'large') {
      return (f.capacity ?? 0) >= 50;
    }
    return true;
  });

  const lowCoverage = stateStats.filter(s => s.avg_trust < 40 || s.total < 20)
  const totalFacilities = stateStats.reduce((s, st) => s + st.total, 0)
  const avgTrust = stateStats.reduce((s, st) => s + st.avg_trust, 0) / (stateStats.length || 1)

  return (
    <div className="space-y-8 py-2">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-primary)' }}>
            Medical Deserts & Gaps
          </h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Locate critical healthcare coverage voids and check regional trust scores.
          </p>
        </div>

        {selectedState && (
          <button
            onClick={() => setSelectedState(null)}
            className="text-xs font-bold text-teal-700 dark:text-teal-400 hover:underline border border-teal-200 dark:border-teal-900/30 px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800"
          >
            Show All States
          </button>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div className="card p-5 space-y-1">
          <span className="text-2xl font-black block" style={{ color: 'var(--text-primary)' }}>
            {totalFacilities.toLocaleString('en-IN')}
          </span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">Active Hospitals</span>
          <span className="text-[10px] text-slate-400 block">Total audited locations</span>
        </div>

        <div className="card p-5 space-y-1">
          <span className="text-2xl font-black block" style={{ color: 'var(--text-primary)' }}>
            {stateStats.length}
          </span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">States Monitored</span>
          <span className="text-[10px] text-slate-400 block">Indian states with details</span>
        </div>

        <div className="card p-5 space-y-1">
          <span className="text-2xl font-black block" style={{ color: avgTrust >= 50 ? 'var(--success)' : 'var(--warning)' }}>
            {avgTrust.toFixed(0)}%
          </span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">Average Trust</span>
          <span className="text-[10px] text-slate-400 block">Verified documentation ratio</span>
        </div>

        <div className="card p-5 space-y-1 border-red-200 bg-red-50/20">
          <span className="text-2xl font-black block text-red-600">
            {lowCoverage.length}
          </span>
          <span className="text-xs font-bold text-red-800 dark:text-red-400 block">Desert States</span>
          <span className="text-[10px] text-red-500 block">Regions needing immediate beds</span>
        </div>
      </div>

      {/* Map View */}
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="card p-6 space-y-4">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>
            🗺️ Coverage Deserts Map
          </h2>
          <p className="text-[10px] text-slate-400">Click a marker to view hospital details and inspect citations.</p>
        </div>
        
        <div className="flex flex-wrap gap-2 pb-2">
          {[
            { id: 'all', label: 'All Audited Locations' },
            { id: 'emergency', label: 'ICU & Emergency Desks Only' },
            { id: 'large', label: 'High Capacity Clinics (50+ beds)' },
          ].map(btn => (
            <button
              key={btn.id}
              onClick={() => setMapFilter(btn.id as any)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${
                mapFilter === btn.id
                  ? 'bg-teal-700 border-teal-700 text-white shadow-sm'
                  : 'bg-white border-slate-200 text-slate-600 hover:text-slate-900'
              }`}
            >
              {btn.label}
            </button>
          ))}
        </div>

        <MapView
          facilities={displayedFacilities}
          height="550px"
          onFacilityClick={(f) => navigate(`/facility/${f.unique_id}`)}
        />
      </motion.div>

      {/* State List Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="card p-6">
          <h3 className="font-bold text-sm uppercase tracking-wider mb-4 flex items-center gap-1.5" style={{ color: 'var(--text-primary)' }}>
            <TrendingDown className="h-4 w-4 text-teal-700" />
            State Audit Rankings
          </h3>
          <div className="divide-y" style={{ borderColor: 'var(--border-color)' }}>
            {[...stateStats].sort((a, b) => b.avg_trust - a.avg_trust).map(s => (
              <div
                key={s.state}
                onClick={() => setSelectedState(s.state)}
                className={`flex items-center justify-between py-3 text-xs cursor-pointer rounded-lg px-2 transition-all hover:bg-slate-50 dark:hover:bg-slate-900 ${selectedState === s.state ? 'bg-teal-50 dark:bg-slate-900 border-l-4 border-teal-600 pl-3' : ''}`}
              >
                <span className="font-bold" style={{ color: 'var(--text-primary)' }}>{s.state}</span>
                <div className="flex items-center gap-4">
                  <span style={{ color: 'var(--text-secondary)' }}>{s.total} Clinics</span>
                  <span className="rounded-full px-2 py-0.5 text-[10px] font-bold"
                        style={{
                          backgroundColor: s.avg_trust >= 50 ? 'var(--success-bg)' : s.avg_trust >= 30 ? 'var(--warning-bg)' : 'var(--danger-bg)',
                          color: s.avg_trust >= 50 ? 'var(--success)' : s.avg_trust >= 30 ? 'var(--warning)' : 'var(--danger)'
                        }}>
                    {s.avg_trust.toFixed(0)}% trust
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Low Coverage Warning Box */}
        <div className="card p-6 space-y-4">
          <h3 className="font-bold text-sm uppercase tracking-wider flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            ⚠️ Desert Warnings (Attention Needed)
          </h3>
          <p className="text-xs text-slate-400">These states have a combination of sparse hospitals or low corroboration credibility score levels.</p>

          <div className="space-y-3">
            {lowCoverage.length === 0 ? (
              <div className="p-4 rounded-xl border text-center text-xs italic text-slate-400">All states show acceptable coverage ratios.</div>
            ) : (
              [...lowCoverage].sort((a, b) => a.avg_trust - b.avg_trust).map(s => (
                <div
                  key={s.state}
                  onClick={() => setSelectedState(s.state)}
                  className="p-3.5 rounded-xl border bg-slate-50 dark:bg-slate-900 cursor-pointer flex justify-between items-center transition-all hover:border-slate-300"
                  style={{ borderColor: 'var(--border-color)' }}
                >
                  <div>
                    <h4 className="font-extrabold text-xs" style={{ color: 'var(--text-primary)' }}>{s.state}</h4>
                    <p className="text-[10px] text-red-500 font-semibold mt-0.5">{s.low_trust_count} hospitals unverified</p>
                  </div>
                  <span className="text-[10px] bg-red-100 dark:bg-red-950/40 text-red-700 dark:text-red-400 px-2 py-0.5 rounded-full font-bold">
                    {s.avg_trust.toFixed(0)}% trust
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
