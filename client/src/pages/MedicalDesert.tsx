import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { MapPin, AlertTriangle, TrendingDown } from 'lucide-react'
import { api } from '@/lib/api'
import MapView from '@/components/MapView'
import DataTable from '@/components/DataTable'
import LoadingSpinner from '@/components/LoadingSpinner'
import type { CoverageGap, Facility } from '@/lib/types'

export default function MedicalDesert() {
  const [stateStats, setStateStats] = useState<CoverageGap[]>([])
  const [facilities, setFacilities] = useState<Facility[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedState, setSelectedState] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api.getStateStats(), api.getMapData()])
      .then(([ss, f]) => { setStateStats(ss); setFacilities(f) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  const filteredFacilities = selectedState
    ? facilities.filter(f => f.address_stateOrRegion === selectedState)
    : facilities

  const lowCoverage = stateStats.filter(s => s.avg_trust < 40 || s.total < 20)
  const totalFacilities = stateStats.reduce((s, st) => s + st.total, 0)
  const avgTrust = stateStats.reduce((s, st) => s + st.avg_trust, 0) / (stateStats.length || 1)

  const gapColumns = [
    {
      key: 'state',
      label: 'State',
      sortable: true,
      render: (r: Record<string, unknown>) => (
        <button
          onClick={(e) => { e.stopPropagation(); setSelectedState(r.state as string) }}
          className="font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
        >
          {r.state as string}
        </button>
      ),
    },
    {
      key: 'total',
      label: 'Facilities',
      sortable: true,
      render: (r: Record<string, unknown>) => (
        <span className="font-mono text-sm">{(r.total as number).toLocaleString('en-IN')}</span>
      ),
    },
    {
      key: 'avg_trust',
      label: 'Avg Trust',
      sortable: true,
      render: (r: Record<string, unknown>) => {
        const v = r.avg_trust as number
        return (
          <span className="font-mono text-sm" style={{ color: v >= 50 ? '#10b981' : v >= 30 ? '#f59e0b' : '#ef4444' }}>
            {v.toFixed(1)}
          </span>
        )
      },
    },
    {
      key: 'low_trust_count',
      label: 'Low Trust',
      sortable: true,
      render: (r: Record<string, unknown>) => (
        <span className="font-mono text-sm text-red-500">{r.low_trust_count as number}</span>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          <MapPin className="mr-2 inline h-6 w-6 text-amber-500" />
          Medical Desert Analysis
        </h1>
        <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Identify underserved regions and healthcare coverage gaps across India
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card">
          <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{totalFacilities.toLocaleString('en-IN')}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Total Facilities</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card">
          <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{stateStats.length}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>States Covered</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card">
          <p className="text-2xl font-bold" style={{ color: avgTrust >= 50 ? '#10b981' : '#f59e0b' }}>{avgTrust.toFixed(1)}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Overall Avg Trust</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card">
          <p className="text-2xl font-bold text-red-500">{lowCoverage.length}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Low Coverage States</p>
        </motion.div>
      </div>

      {/* Map */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <div className="card p-0 overflow-hidden">
          <div className="flex items-center justify-between p-4">
            <h2 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
              Facility Distribution Map
            </h2>
            {selectedState && (
              <button
                onClick={() => setSelectedState(null)}
                className="text-xs text-brand-600 hover:text-brand-700 dark:text-brand-400"
              >
                Clear filter
              </button>
            )}
          </div>
          <MapView
            facilities={filteredFacilities}
            height="450px"
            onFacilityClick={(f) => window.open(`/facility/${f.unique_id}`, '_blank')}
          />
        </div>
      </motion.div>

      {/* Gap Table */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
        <div className="card">
          <h2 className="mb-4 font-semibold" style={{ color: 'var(--text-primary)' }}>
            <TrendingDown className="mr-2 inline h-5 w-5 text-amber-500" />
            State Coverage Analysis
          </h2>
          <DataTable
            columns={gapColumns}
            data={stateStats as unknown as Record<string, unknown>[]}
            emptyMessage="No state data available"
          />
        </div>
      </motion.div>

      {/* Low Coverage Alert */}
      {lowCoverage.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <div className="card border-amber-200 bg-amber-50/50 dark:border-amber-800 dark:bg-amber-900/10">
            <h2 className="mb-3 flex items-center gap-2 font-semibold text-amber-700 dark:text-amber-400">
              <AlertTriangle className="h-5 w-5" />
              Low Coverage Alert
            </h2>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {lowCoverage.map(s => (
                <div key={s.state} className="flex items-center justify-between rounded-lg border border-amber-200 bg-white p-3 dark:border-amber-800 dark:bg-slate-800">
                  <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{s.state}</span>
                  <div className="flex items-center gap-2 text-xs">
                    <span style={{ color: 'var(--text-muted)' }}>{s.total} facilities</span>
                    <span className="font-mono text-amber-600">{s.avg_trust.toFixed(0)} avg</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}
